import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hmean

criptos = ['sol','btc','eth','xrp']
date_end = None
period = 6
hour = 14 

for cripto in criptos:
    ticker = cripto.upper() + 'USDC'
    if date_end is None:
        date_end = datetime.now(timezone.utc)
    else:
        date_end = date_end
    date_start = date_end - timedelta(days=365 * period)
    
    
    intervalo_horas = Client.KLINE_INTERVAL_1HOUR
    
    # Inicializar el cliente con tus credenciales
    api_key = 'cAGsQPkvI5sxkMt1qTJY7ancjALp1EeabYyF8GltqJ8KuOKvgfZH7aKzYHyQc9X8'
    api_secret = 'qkj0jJxLcbzEvpyJvYfww5jzYkv8ExYayhT7mXGbFfeWwT0bnH8VrolE4tNr1WO0'
    
    client = Client(api_key, api_secret)
    
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
    aux['date'] = aux['date'].shift(-hour)
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
    df['target_low'] = df['low_return'].shift(-1)
    df['target_high'] = df['high_return'].shift(-1)
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
    
    
    
    df.to_csv(cripto.lower() + "_dinamicas.csv", index = False)