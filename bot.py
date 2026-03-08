import threading
from datetime import datetime
import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hmean
import pickle
import sklearn

# Inicializar el cliente con tus credenciales
from dotenv import load_dotenv
import os

load_dotenv()  # lee el .env

api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_SECRET")
client = Client(api_key, api_secret)

from binance.client import Client
from binance.exceptions import BinanceAPIException
import numpy as np
import time
import threading


client = Client(api_key, api_secret)

# 🔹 Sincronizar reloj
server_time = client.get_server_time()["serverTime"]
local_time = int(time.time() * 1000)
client.timestamp_offset = server_time - local_time

def predict(symbol):

    date_end = None
    period = 370
    hour = 10 

    ticker = symbol
    if date_end is None:
        date_end = datetime.now(timezone.utc)
    else:
        date_end = date_end
    date_start = date_end - timedelta(days=period)


    intervalo_horas = Client.KLINE_INTERVAL_1HOUR


    # Obtener datos históricos
    start_timestamp = int(date_start.timestamp() * 1000)
    end_timestamp = int(date_end.timestamp() * 1000)

    klines = client.get_historical_klines(ticker, intervalo_horas, str(start_timestamp), str(end_timestamp))

    if not klines:
        raise ValueError("No se obtuvieron datos históricos para la criptomoneda y el período especificados.")

    data = []

    def timestamp_to_utc(ts):
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)

    for kline in klines:
        data.append({
            'time': timestamp_to_utc(float(kline[0])),
            'open': float(kline[1]),
            'high': float(kline[2]),
            'low': float(kline[3]),
            'close': float(kline[4]),
            'volume': float(kline[5]),
        })

    aux = pd.DataFrame(data)

    aux['date'] = pd.to_datetime(aux['time'])
    aux['date'] = aux['date'].shift(hour)
    aux['day'] = aux['day'] = aux['date'].dt.date

    df = aux.groupby('day').agg(
        open = ('open', 'first'),
        close =('close', 'last'),
        high = ('high', 'max'),
        low =('low', 'min'),
        volume =('volume','first'),
        date = ('day','first')
        )

    df['high_return'] = df['high']/ df['open']
    df['low_return'] = df['low']/ df['open']
    df['close_return'] = df['close']/ df['open']
    df['volatility'] = df['high_return'] - df['low_return']
    def combinations(l):
        l_final = []
        n = len(l)
        for i in range(n-1):
            for j in range(i+1,n):
                l_final.append((l[i],l[j]))
        return l_final 

    rachas = [1,3,7,14,30,90,180,360]           

    dinamicas = combinations(rachas)
            

    for r in rachas:
        df[f'high_mean_{r}'] = df['high_return'].rolling(r).mean()
        df[f'low_mean_{r}'] = df['low_return'].rolling(r).mean()
        df[f'close_mean_{r}'] = df['close_return'].rolling(r).mean()
        df[f'volatility_mean_{r}'] = df['volatility'].rolling(r).mean()



    for d in dinamicas:
        a,b = d
        df[f'high_dinamica_mean_{a}_{b}'] = (df[f'high_mean_{a}'] / df[f'high_mean_{b}']) -1
        df[f'volatility_dinamica_mean_{a}_{b}'] =(df[f'volatility_mean_{a}'] / df[f'volatility_mean_{b}']) - 1
        df[f'low_dinamica_mean_{a}_{b}'] = -((df[f'low_mean_{a}'] / df[f'low_mean_{b}']) -1)
        df[f'close_dinamica_mean_{a}_{b}'] = (df[f'close_mean_{a}'] / df[f'close_mean_{b}']) -1
        df[f'high_dinamica_mean_{a}_{b}_modified'] = df[f'high_mean_{a}']**2 / df[f'high_mean_{b}']
        df[f'high_pendiente_{a}_{b}'] = df[f'high_dinamica_mean_{a}_{b}'].diff()
        df[f'low_pendiente_{a}_{b}'] = df[f'low_dinamica_mean_{a}_{b}'].diff()
        df[f'close_pendiente_{a}_{b}'] = df[f'close_dinamica_mean_{a}_{b}'].diff()
        df[f'volatility_pendiente_{a}_{b}'] = df[f'volatility_dinamica_mean_{a}_{b}'].diff()

    df['cripto_SOL'] = True
    df['cripto_BTC'] = False
    df['cripto_ETH'] = False
    df['cripto_XRP'] = False

    df = df.dropna()
    
    data = df.drop(columns={'date','open','high','close','low'})

    
    print('checkpoint')
    with open("gb_low/gb_low_model.pkl", "rb") as f:
        gb_low = pickle.load(f)
    print('checkpoint')
    with open("gb_low/gb_low_columns.pkl", "rb") as f:
        cols = pickle.load(f)
    print('checkpoint')     
    with open("gb_low/umbral_gb_low_columns.pkl", "rb") as f:
        umbral_max = pickle.load(f)
    print('checkpoint')
    pred = gb_low.predict_proba(data[cols].tail(1))[:, 1]
    pred_bool = pred > umbral_max[2]
    openday = df['open'].tail(1)
    virtual_close = openday*umbral_max[0]

    return pred, pred_bool

# 🔹 Función para crear orden de venta LIMIT
def create_sell_order(symbol, sell_price):
    try:
        # Obtener saldo disponible del activo base
        base_asset = symbol[:-4]  # asumiendo par tipo XXXUSDC
        balance = client.get_asset_balance(asset=base_asset)
        qty = float(balance['free'])

        if qty <= 0:
            print(f"No tienes {base_asset} disponible para vender.")
            return None

        # Ajustar cantidad según stepSize y minNotional
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

        print(f"✅ Orden de venta creada para {symbol} a {sell_price}:")
        print(order)
        return order

    except BinanceAPIException as e:
        print("❌ Error de API al crear orden de venta:", e)
    except Exception as e:
        print("❌ Otro error al crear orden de venta:", e)

# 🔹 Función para cancelar orden de venta abierta
def cancel_sell_order(symbol):
    try:
        # Obtener todas las órdenes abiertas del par
        open_orders = client.get_open_orders(symbol=symbol)
        if not open_orders:
            print(f"No hay órdenes abiertas para {symbol}.")
            return None

        # Cancelar la primera orden encontrada
        order_id = open_orders[0]['orderId']
        canceled_order = client.cancel_order(symbol=symbol, orderId=order_id)
        print(f"✅ Orden cancelada para {symbol}:")
        print(canceled_order)
        return canceled_order

    except BinanceAPIException as e:
        print("❌ Error de API al cancelar orden:", e)
    except Exception as e:
        print("❌ Otro error al cancelar orden:", e)

def get_binance_time(client, formatted=True):
    """
    Devuelve la hora actual del servidor de Binance.
    
    Args:
        client: instancia de Client de Binance
        formatted (bool):
            True  -> devuelve string formateado
            False -> devuelve datetime
    
    Returns:
        str o datetime
    """
    server_time = client.get_server_time()["serverTime"]  # milisegundos
    dt = datetime.fromtimestamp(server_time / 1000)

    if formatted:
        return dt.strftime("%H:%M:%S")
    else:
        return dt

# 🔹 Función para comprar todo el saldo disponible de la moneda de cotización
def buy_with_full_quote(symbol, fee_margin=0.995, timeout=15):
    """
    Ejecuta orden MARKET comprando con todo el saldo disponible y
    no termina hasta que la orden esté completamente ejecutada.

    Args:
        symbol (str): Par de trading, por ejemplo "SOLUSDC"
        fee_margin (float): Margen para fees
        timeout (int): Segundos máximos de espera

    Returns:
        float: Precio medio real de ejecución
        dict: Orden completa
    """

    # 🔹 Sincronizar reloj
    server_time = client.get_server_time()["serverTime"]
    local_time = int(time.time() * 1000)
    client.timestamp_offset = server_time - local_time

    try:
        quote_asset = symbol[-4:]
        balance = client.get_asset_balance(asset=quote_asset)
        free_amount = float(balance['free'])

        if free_amount <= 0:
            print(f"No tienes {quote_asset} disponible.")
            return None, None

        amount_to_use = round(free_amount * fee_margin, 2)

        # 🔹 Crear orden MARKET
        order = client.create_order(
            symbol=symbol,
            side="BUY",
            type="MARKET",
            quoteOrderQty=amount_to_use
        )

        order_id = order["orderId"]

        print("⏳ Esperando confirmación de ejecución...")

        # 🔹 Esperar hasta que esté FILLED
        start_time = time.time()

        while True:
            current_order = client.get_order(symbol=symbol, orderId=order_id)
            status = current_order["status"]

            if status == "FILLED":
                break

            if time.time() - start_time > timeout:
                raise TimeoutError("La orden no se ejecutó dentro del tiempo esperado.")

            time.sleep(10)

        # 🔹 Calcular precio medio real usando trades
        trades = client.get_my_trades(symbol=symbol)

        relevant_trades = [t for t in trades if t["orderId"] == order_id]

        total_qty = sum(float(t["qty"]) for t in relevant_trades)
        total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

        avg_price = total_quote / total_qty if total_qty > 0 else 0

        print(f"✅ Compra ejecutada completamente en {symbol}")
        print(f"Precio medio real: {avg_price:.6f}")

        return avg_price, current_order

    except BinanceAPIException as e:
        print("❌ Error de API:", e)
        return None, None
    except Exception as e:
        print("❌ Error:", e)
        return None, None

def check_sell_execution(symbol, order_id=None):
    """
    Comprueba si una orden de venta fue ejecutada.

    Args:
        symbol (str): Par de trading (ej. "SOLUSDC")
        order_id (int, optional): ID específico de la orden

    Returns:
        bool: True si está FILLED
        float: Precio medio de ejecución (si aplica)
        dict: Datos completos de la orden
    """

    try:
        # Si se pasa order_id, consultamos esa orden concreta
        if order_id:
            order = client.get_order(symbol=symbol, orderId=order_id)
        else:
            # Si no, revisamos historial reciente
            orders = client.get_all_orders(symbol=symbol, limit=5)
            if not orders:
                print("No hay órdenes registradas.")
                return False
            order = orders[-1]  # última orden

        status = order["status"]

        if status == "FILLED":
            print("✅ Orden de venta ejecutada.")

            # Calcular precio medio real
            trades = client.get_my_trades(symbol=symbol)

            # Filtrar trades de esa orderId
            relevant_trades = [t for t in trades if t["orderId"] == order["orderId"]]

            total_qty = sum(float(t["qty"]) for t in relevant_trades)
            total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

            avg_price = total_quote / total_qty if total_qty > 0 else 0

            print(f"Precio medio ejecución: {avg_price:.4f}")

            return True

        elif status in ["NEW", "PARTIALLY_FILLED"]:
            print("⏳ Orden aún no ejecutada completamente.")
            return False

        else:
            print(f"⚠️ Estado de la orden: {status}")
            return False

    except BinanceAPIException as e:
        print("❌ Error de API:", e)
        return False
    except Exception as e:
        print("❌ Otro error:", e)
        return False

def sell_market_order_retry(symbol, retry_interval=15, max_attempts=1000):
    """
    Intenta vender con orden MARKET.
    Si falla o no se vende completamente, reintenta cada X segundos.

    Args:
        symbol (str): Par, ej. "SOLUSDC"
        retry_interval (int): segundos entre intentos
        max_attempts (int): máximo número de intentos

    Returns:
        float: Precio medio de ejecución final
        dict: Última orden ejecutada
    """

    attempts = 0

    while attempts < max_attempts:
        attempts += 1
        print(f"🔄 Intento de venta #{attempts}")

        try:
            base_asset = symbol[:-4]
            balance = client.get_asset_balance(asset=base_asset)
            qty = float(balance['free'])

            if qty <= 0:
                print("✅ No queda saldo. Venta completada.")
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
                print("Cantidad ajustada es 0. Fin.")
                return None, None

            # 🔹 Ejecutar MARKET
            order = client.create_order(
                symbol=symbol,
                side="SELL",
                type="MARKET",
                quantity=qty_to_sell
            )

            # Confirmar ejecución
            order_id = order["orderId"]

            while True:
                current_order = client.get_order(symbol=symbol, orderId=order_id)
                if current_order["status"] == "FILLED":
                    break
                time.sleep(2)

            # Calcular precio medio real
            trades = client.get_my_trades(symbol=symbol)
            relevant_trades = [t for t in trades if t["orderId"] == order_id]

            total_qty = sum(float(t["qty"]) for t in relevant_trades)
            total_quote = sum(float(t["quoteQty"]) for t in relevant_trades)

            avg_price = total_quote / total_qty if total_qty > 0 else 0

            print(f"✅ Venta ejecutada. Precio medio: {avg_price:.6f}")

            # Verificar si aún queda polvo
            balance = client.get_asset_balance(asset=base_asset)
            remaining_qty = float(balance['free'])

            if remaining_qty <= step_size:
                print("🎯 Venta completamente finalizada.")
                return avg_price, order

            print("⚠️ Queda saldo pequeño, reintentando...")

        except Exception as e:
            print("❌ Error en intento de venta:", e)

        print(f"⏳ Esperando {retry_interval} segundos antes de reintentar...")
        time.sleep(retry_interval)

    print("❌ Se alcanzó el máximo de intentos.")
    return None, None

def get_current_price(symbol):
    """
    Devuelve el precio actual de mercado de un símbolo.

    Args:
        symbol (str): Par de trading, ej. "SOLUSDC"

    Returns:
        float: Precio actual
    """
    try:
        ticker = client.get_symbol_ticker(symbol=symbol)
        price = float(ticker["price"])
        return price

    except BinanceAPIException as e:
        print("❌ Error de API al obtener precio:", e)
        return None
    except Exception as e:
        print("❌ Otro error:", e)
        return None

def main(symbol, check_interval=2, target_time="14:00"):

    global active_timer
    from datetime import datetime

    openday = None  # ← importante inicializarlo aquí

    def check_time():
        now = datetime.strptime(
            get_binance_time(client, formatted=True),
            "%H:%M:%S"
        ).time()

        target = datetime.strptime(target_time, "%H:%M").time()

        return now >= target

    cont = check_time()  # estado inicial

    def shot_time():
        nonlocal cont, openday
        global active_timer

        try:
            new_iter = check_time()

            trigger = (not cont) and new_iter
            cont = new_iter

            # 🔥 SOLO se ejecuta una vez cuando cruza la hora
            if trigger:
                print("⏰ Trigger activado")

                pred, pred_bool = predict(symbol)

                if pred < 0.5:
                    if check_sell_execution(symbol, order_id=None):
                        openday, order = buy_with_full_quote(symbol)
                        if openday:
                            create_sell_order(symbol, round(openday * 1.02,2))
                    else:
                        print("No se ha comprado porque check_sell_execution dio False")

                else:
                    if check_sell_execution(symbol, order_id=None):
                        sell_market_order_retry(symbol)
                    print("No se ha comprado")

            # 🔻 Lógica de stop-loss continua
            if openday:
                current_price = get_current_price(symbol)
                if current_price < openday * 0.9:
                    print("⚠️ Stop loss activado")
                    cancel_sell_order(symbol)
                    sell_market_order_retry(symbol)
                    openday = None  # evitar repetir venta

            # 🔁 Reprogramar timer
            active_timer = threading.Timer(check_interval, shot_time)
            active_timer.start()

        except Exception as e:
            print("❌ Error:", e)
            active_timer = threading.Timer(5, shot_time)
            active_timer.start()

    # Primera ejecución
    active_timer = threading.Timer(check_interval, shot_time)
    active_timer.start()

if __name__ == "__main__":
    main("SOLUSDC")