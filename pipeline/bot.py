import threading
import time
import logging
from datetime import datetime
from binance.client import Client
from binance.exceptions import BinanceAPIException
import numpy as np

from config import BINANCE_API_KEY, BINANCE_SECRET, TRADING_CONFIG
from predictor import predict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/trading.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

client = Client(BINANCE_API_KEY, BINANCE_SECRET)

server_time = client.get_server_time()["serverTime"]
local_time = int(time.time() * 1000)
client.timestamp_offset = server_time - local_time


def get_binance_time(client, formatted=True):
    server_time = client.get_server_time()["serverTime"]
    dt = datetime.fromtimestamp(server_time / 1000)
    
    if formatted:
        return dt.strftime("%H:%M:%S")
    else:
        return dt


def create_sell_order(symbol, sell_price):
    try:
        base_asset = symbol[:-4]
        balance = client.get_asset_balance(asset=base_asset)
        qty = float(balance['free'])

        if qty <= 0:
            logger.warning(f"No tienes {base_asset} disponible para vender.")
            return None

        symbol_info = client.get_symbol_info(symbol)
        step_size = None
        min_notional = None

        for f in symbol_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                step_size = float(f['stepSize'])
            elif f['filterType'] == 'NOTIONAL':
                min_notional = float(f['minNotional'])

        if step_size is None or min_notional is None:
            raise ValueError("No se pudo obtener stepSize o minNotional del par")

        qty_to_sell = np.floor(qty / step_size) * step_size

        if qty_to_sell * sell_price < min_notional:
            raise ValueError(f"Valor total de la orden ({qty_to_sell*sell_price:.2f}) menor que minNotional ({min_notional})")

        order = client.create_order(
            symbol=symbol,
            side="SELL",
            type="LIMIT",
            quantity=qty_to_sell,
            price=str(sell_price),
            timeInForce="GTC"
        )

        logger.info(f"✅ Orden de venta creada para {symbol} a {sell_price}")
        return order

    except BinanceAPIException as e:
        logger.error(f"❌ Error de API al crear orden de venta: {e}")
    except Exception as e:
        logger.error(f"❌ Otro error al crear orden de venta: {e}")


def cancel_sell_order(symbol):
    try:
        open_orders = client.get_open_orders(symbol=symbol)
        if not open_orders:
            logger.info(f"No hay órdenes abiertas para {symbol}.")
            return None

        order_id = open_orders[0]['orderId']
        canceled_order = client.cancel_order(symbol=symbol, orderId=order_id)
        logger.info(f"✅ Orden cancelada para {symbol}")
        return canceled_order

    except BinanceAPIException as e:
        logger.error(f"❌ Error de API al cancelar orden: {e}")
    except Exception as e:
        logger.error(f"❌ Otro error al cancelar orden: {e}")


def buy_with_full_quote(symbol, fee_margin=None, timeout=None):
    if fee_margin is None:
        fee_margin = TRADING_CONFIG['fee_margin']
    if timeout is None:
        timeout = TRADING_CONFIG['timeout']
    
    server_time = client.get_server_time()["serverTime"]
    local_time = int(time.time() * 1000)
    client.timestamp_offset = server_time - local_time

    try:
        quote_asset = symbol[-4:]
        balance = client.get_asset_balance(asset=quote_asset)
        free_amount = float(balance['free'])

        if free_amount <= 0:
            logger.warning(f"No tienes {quote_asset} disponible.")
            return None, None

        amount_to_use = round(free_amount * fee_margin, 2)

        order = client.create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quoteOrderQty=amount_to_use
        )

        order_id = order["orderId"]
        logger.info("⏳ Esperando confirmación de ejecución...")

        start_time = time.time()

        while True:
            current_order = client.get_order(symbol=symbol, orderId=order_id)
            status = current_order["status"]

            if status == "FILLED":
                break

            if time.time() - start_time > timeout:
                raise TimeoutError("La orden no se ejecutó dentro del tiempo esperado.")

            time.sleep(10)

        trades = client.get_my_trades(symbol=symbol)
        relevant_trades = [t for t in trades if t["orderId"] == order_id]

        total_qty = sum(float(t["qty"]) for t in relevant_trades)
        total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

        avg_price = total_quote / total_qty if total_qty > 0 else 0

        logger.info(f"✅ Compra ejecutada completamente en {symbol}")
        logger.info(f"Precio medio real: {avg_price:.6f}")

        return avg_price, current_order

    except BinanceAPIException as e:
        logger.error(f"❌ Error de API: {e}")
        return None, None
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return None, None


def check_sell_execution(symbol, order_id=None):
    try:
        if order_id:
            order = client.get_order(symbol=symbol, orderId=order_id)
        else:
            orders = client.get_all_orders(symbol=symbol, limit=5)
            if not orders:
                logger.info("No hay órdenes registradas.")
                return False
            order = orders[-1]

        status = order["status"]

        if status == "FILLED":
            logger.info("✅ Orden de venta ejecutada.")

            trades = client.get_my_trades(symbol=symbol)
            relevant_trades = [t for t in trades if t["orderId"] == order["orderId"]]

            total_qty = sum(float(t["qty"]) for t in relevant_trades)
            total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

            avg_price = total_quote / total_qty if total_qty > 0 else 0
            logger.info(f"Precio medio ejecución: {avg_price:.4f}")

            return True

        elif status in ["NEW", "PARTIALLY_FILLED"]:
            logger.info("⏳ Orden aún no ejecutada completamente.")
            return False

        else:
            logger.warning(f"⚠️ Estado de la orden: {status}")
            return False

    except BinanceAPIException as e:
        logger.error(f"❌ Error de API: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Otro error: {e}")
        return False


def sell_market_order_retry(symbol, retry_interval=15, max_attempts=1000):
    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        logger.info(f"🔄 Intento de venta #{attempts}")

        try:
            base_asset = symbol[:-4]
            balance = client.get_asset_balance(asset=base_asset)
            qty = float(balance['free'])

            if qty <= 0:
                logger.info("✅ No queda saldo. Venta completada.")
                return None, None

            symbol_info = client.get_symbol_info(symbol)

            step_size = None
            for f in symbol_info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    step_size = float(f['stepSize'])

            if step_size is None:
                raise ValueError("No se pudo obtener stepSize")

            qty_to_sell = np.floor(qty / step_size) * step_size

            if qty_to_sell <= 0:
                logger.info("Cantidad ajustada es 0. Fin.")
                return None, None

            order = client.create_order(
                symbol=symbol,
                side="SELL",
                type="MARKET",
                quantity=qty_to_sell
            )

            order_id = order["orderId"]

            while True:
                current_order = client.get_order(symbol=symbol, orderId=order_id)
                if current_order["status"] == "FILLED":
                    break
                time.sleep(2)

            trades = client.get_my_trades(symbol=symbol)
            relevant_trades = [t for t in trades if t["orderId"] == order_id]

            total_qty = sum(float(t["qty"]) for t in relevant_trades)
            total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

            avg_price = total_quote / total_qty if total_qty > 0 else 0

            logger.info(f"✅ Venta ejecutada. Precio medio: {avg_price:.6f}")

            balance = client.get_asset_balance(asset=base_asset)
            remaining_qty = float(balance['free'])

            if remaining_qty <= step_size:
                logger.info("🎯 Venta completamente finalizada.")
                return avg_price, order

            logger.warning("⚠️ Queda saldo pequeño, reintentando...")

        except Exception as e:
            logger.error(f"❌ Error en intento de venta: {e}")

        logger.info(f"⏳ Esperando {retry_interval} segundos antes de reintentar...")
        time.sleep(retry_interval)

    logger.error("❌ Se alcanzó el máximo de intentos.")
    return None, None


def get_current_price(symbol):
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker["price"])
        return price

    except BinanceAPIException as e:
        logger.error(f"❌ Error de API al obtener precio: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Otro error: {e}")
        return None


def main(symbol=None, check_interval=None, target_time=None):
    if symbol is None:
        symbol = TRADING_CONFIG['symbol']
    if check_interval is None:
        check_interval = TRADING_CONFIG['check_interval']
    if target_time is None:
        target_time = TRADING_CONFIG['target_time']
    
    logger.info(f"🚀 Iniciando bot de trading para {symbol}")
    logger.info(f"⏰ Hora objetivo: {target_time}")
    
    global active_timer

    openday = None

    def check_time():
        now = datetime.strptime(
            get_binance_time(client, formatted=True),
            "%H:%M:%S"
        ).time()

        target = datetime.strptime(target_time, "%H:%M").time()

        return now >= target

    cont = check_time()

    def shot_time():
        nonlocal cont, openday
        global active_timer

        try:
            new_iter = check_time()

            trigger = (not cont) and new_iter
            cont = new_iter

            if trigger:
                logger.info("⏰ Trigger activado - Ejecutando predicción")

                pred, pred_bool, _, _ = predict(client, symbol)
                
                logger.info(f"📊 Predicción: {pred:.4f} | Decisión: {'COMPRAR' if pred < 0.5 else 'NO COMPRAR'}")

                if pred < 0.5:
                    if check_sell_execution(symbol, order_id=None):
                        openday, order = buy_with_full_quote(symbol)
                        if openday:
                            sell_price = round(openday * TRADING_CONFIG['take_profit_threshold'], 2)
                            create_sell_order(symbol, sell_price)
                    else:
                        logger.warning("No se ha comprado porque check_sell_execution dio False")

                else:
                    if check_sell_execution(symbol, order_id=None):
                        sell_market_order_retry(symbol)
                    logger.info("No se ha comprado - Predicción no favorable")

            if openday:
                current_price = get_current_price(symbol)
                if current_price and current_price < openday * TRADING_CONFIG['stop_loss_threshold']:
                    logger.warning("⚠️ Stop loss activado")
                    cancel_sell_order(symbol)
                    sell_market_order_retry(symbol)
                    openday = None

            active_timer = threading.Timer(check_interval, shot_time)
            active_timer.start()

        except Exception as e:
            logger.error(f"❌ Error: {e}")
            active_timer = threading.Timer(5, shot_time)
            active_timer.start()

    active_timer = threading.Timer(check_interval, shot_time)
    active_timer.start()


if __name__ == "__main__":
    import os
    os.makedirs('logs', exist_ok=True)
    main()
