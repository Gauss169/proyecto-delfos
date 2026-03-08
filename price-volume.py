import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np

# =====================
# CONFIGURACIÓN
# =====================
criptos = ['sol', 'btc', 'eth', 'xrp']
date_end = None
period = 6        # años
hour = 14         # shift horario
df_final = None

# =====================
# BINANCE CLIENT
# =====================
api_key = "TU_API_KEY"
api_secret = "TU_API_SECRET"
client = Client(api_key, api_secret)

# =====================
# LOOP PRINCIPAL
# =====================
for cripto in criptos:
    ticker = cripto.upper() + 'USDC'

    if date_end is None:
        date_end = datetime.now(timezone.utc)

    date_start = date_end - timedelta(days=365 * period)
    intervalo_horas = Client.KLINE_INTERVAL_1HOUR

    start_timestamp = int(date_start.timestamp() * 1000)
    end_timestamp = int(date_end.timestamp() * 1000)

    klines = client.get_historical_klines(
        ticker,
        intervalo_horas,
        str(start_timestamp),
        str(end_timestamp)
    )

    if not klines:
        raise ValueError(f"No hay datos para {ticker}")

    # =====================
    # CONSTRUIR DATAFRAME HORARIO
    # =====================
    rows = []

    def timestamp_to_utc(ts):
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)

    for kline in klines:
        rows.append({
            'time': timestamp_to_utc(float(kline[0])),
            'open': float(kline[1]),
            'high': float(kline[2]),
            'low': float(kline[3]),
            'close': float(kline[4]),
            'quote_volume': float(kline[7])  # USDC
        })

    aux = pd.DataFrame(rows)

    # =====================
    # AJUSTE FECHA Y AGREGACIÓN DIARIA
    # =====================
    aux['date'] = pd.to_datetime(aux['time'])
    aux['date'] = aux['date'].shift(-hour)
    aux['day'] = aux['date'].dt.date

    df = aux.groupby('day').agg(
        open=('open', 'first'),
        close=('close', 'last'),
        high=('high', 'max'),
        low=('low', 'min'),
        quote_volume=('quote_volume', 'sum')
    ).reset_index().rename(columns={'day': 'date'})

    # =====================
    # MÉTRICAS
    # =====================
    df[f'high_return_{cripto}'] = df['high'] / df['open']
    df[f'low_return_{cripto}'] = df['low'] / df['open']
    df[f'close_return_{cripto}'] = df['close'] / df['open']
    df[f'volatility_{cripto}'] = (
        df[f'high_return_{cripto}'] - df[f'low_return_{cripto}']
    )

    # =====================
    # RENOMBRAR COLUMNAS
    # =====================
    df.rename(columns={
        'open': f'open_{cripto}',
        'close': f'close_{cripto}',
        'high': f'high_{cripto}',
        'low': f'low_{cripto}',
        'quote_volume': f'quote_volume_{cripto}'
    }, inplace=True)

    # =====================
    # MERGE FINAL
    # =====================
    if df_final is None:
        df_final = df
    else:
        df_final = df_final.merge(df, how='left', on='date')

# =====================
# VARIABLES AGREGADAS
# =====================
df_final['volume_total'] = df_final.filter(like='quote_volume').sum(axis=1)
df_final['price_total'] = df_final.filter(like='open_').sum(axis=1)

# =====================
# UTILIDAD, VALOR REAL Y NORMALIZACIÓN
# =====================
for cripto in criptos:
    df_final[f'utility_{cripto}'] = (
        df_final[f'quote_volume_{cripto}'] / df_final['volume_total']
    )

    df_final[f'real_value_{cripto}'] = (
        df_final[f'utility_{cripto}'] * df_final['price_total']
    )

    df_final[f'open_norm_{cripto}'] = (
        df_final[f'open_{cripto}'] / df_final[f'open_{cripto}'].iloc[0]
    )

    df_final[f'real_value_norm_{cripto}'] = (
        df_final[f'real_value_{cripto}'] / df_final[f'real_value_{cripto}'].iloc[0]
    )

    # =====================
    # GRÁFICO
    # =====================
    plt.figure(figsize=(12, 6))

    plt.plot(
        df_final['date'],
        df_final[f'open_norm_{cripto}'],
        label='Precio (normalizado)',
        linewidth=2
    )

    plt.plot(
        df_final['date'],
        df_final[f'real_value_norm_{cripto}'],
        label='Valor real (normalizado)',
        linewidth=2
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.title(f"Precio vs Valor Real Normalizados – {cripto.upper()}")
    plt.xlabel("Fecha")
    plt.ylabel("Índice (base = 1)")
    plt.tight_layout()
    plt.show()
