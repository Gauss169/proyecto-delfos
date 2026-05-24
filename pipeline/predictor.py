import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import pickle
import numpy as np
from config import MODEL_CONFIG, RACHAS


def combinations(l):
    l_final = []
    n = len(l)
    for i in range(n-1):
        for j in range(i+1, n):
            l_final.append((l[i], l[j]))
    return l_final


def create_features(df, rachas=RACHAS):
    df['high_return'] = df['high'] / df['open']
    df['low_return'] = df['low'] / df['open']
    df['close_return'] = df['close'] / df['open']
    df['volatility'] = df['high_return'] - df['low_return']
    
    dinamicas = combinations(rachas)
    
    for r in rachas:
        df[f'high_mean_{r}'] = df['high_return'].rolling(r).mean()
        df[f'low_mean_{r}'] = df['low_return'].rolling(r).mean()
        df[f'close_mean_{r}'] = df['close_return'].rolling(r).mean()
        df[f'volatility_mean_{r}'] = df['volatility'].rolling(r).mean()
    
    for d in dinamicas:
        a, b = d
        df[f'high_dinamica_mean_{a}_{b}'] = (df[f'high_mean_{a}'] / df[f'high_mean_{b}']) - 1
        df[f'volatility_dinamica_mean_{a}_{b}'] = (df[f'volatility_mean_{a}'] / df[f'volatility_mean_{b}']) - 1
        df[f'low_dinamica_mean_{a}_{b}'] = -((df[f'low_mean_{a}'] / df[f'low_mean_{b}']) - 1)
        df[f'close_dinamica_mean_{a}_{b}'] = (df[f'close_mean_{a}'] / df[f'close_mean_{b}']) - 1
        df[f'high_dinamica_mean_{a}_{b}_modified'] = df[f'high_mean_{a}']**2 / df[f'high_mean_{b}']
        df[f'high_pendiente_{a}_{b}'] = df[f'high_dinamica_mean_{a}_{b}'].diff()
        df[f'low_pendiente_{a}_{b}'] = df[f'low_dinamica_mean_{a}_{b}'].diff()
        df[f'close_pendiente_{a}_{b}'] = df[f'close_dinamica_mean_{a}_{b}'].diff()
        df[f'volatility_pendiente_{a}_{b}'] = df[f'volatility_dinamica_mean_{a}_{b}'].diff()
    
    return df


def get_historical_data(client, symbol, period=370, hour=10):
    date_end = datetime.now(timezone.utc)
    date_start = date_end - timedelta(days=period)
    
    intervalo_horas = Client.KLINE_INTERVAL_1HOUR
    
    start_timestamp = int(date_start.timestamp() * 1000)
    end_timestamp = int(date_end.timestamp() * 1000)
    
    klines = client.get_historical_klines(symbol, intervalo_horas, str(start_timestamp), str(end_timestamp))
    
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
    aux['day'] = aux['date'].dt.date
    
    df = aux.groupby('day').agg(
        open=('open', 'first'),
        close=('close', 'last'),
        high=('high', 'max'),
        low=('low', 'min'),
        volume=('volume', 'first'),
        date=('day', 'first')
    )
    
    return df


def add_crypto_features(df, symbol):
    df['cripto_SOL'] = symbol == 'SOLUSDC'
    df['cripto_BTC'] = symbol == 'BTCUSDC'
    df['cripto_ETH'] = symbol == 'ETHUSDC'
    df['cripto_XRP'] = symbol == 'XRPUSDC'
    return df


def predict(client, symbol):
    period = MODEL_CONFIG['prediction_period']
    hour = MODEL_CONFIG['prediction_hour']
    
    df = get_historical_data(client, symbol, period, hour)
    df = create_features(df)
    df = add_crypto_features(df, symbol)
    df = df.dropna()
    
    data = df.drop(columns=['date', 'open', 'high', 'close', 'low'])
    
    with open(MODEL_CONFIG['model_path'], "rb") as f:
        model = pickle.load(f)
    
    with open(MODEL_CONFIG['columns_path'], "rb") as f:
        cols = pickle.load(f)
    
    with open(MODEL_CONFIG['threshold_path'], "rb") as f:
        umbral_max = pickle.load(f)
    
    pred = model.predict_proba(data[cols].tail(1))[:, 1]
    pred_bool = pred > umbral_max[2]
    openday = df['open'].tail(1).values[0]
    virtual_close = openday * umbral_max[0]
    
    return pred[0], pred_bool[0], openday, virtual_close
