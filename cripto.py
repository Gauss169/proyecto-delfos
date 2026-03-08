import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np
import os
from dotenv import load_dotenv



class Cripto:
    def __init__(self,ticker, period, date_end = None, hour = 0):
        self.ticker = ticker
        if date_end == None:
            self.date_end = datetime.now(timezone.utc)
        self.date_start = self.date_end - timedelta(days=365*period)
        self.hour = hour % 24

        intervalo_horas = Client.KLINE_INTERVAL_30MINUTE

        # Inicializar el cliente con tus credenciales
        api_key = 'cAGsQPkvI5sxkMt1qTJY7ancjALp1EeabYyF8GltqJ8KuOKvgfZH7aKzYHyQc9X8'
        api_secret = 'qkj0jJxLcbzEvpyJvYfww5jzYkv8ExYayhT7mXGbFfeWwT0bnH8VrolE4tNr1WO0'

        client = Client(api_key, api_secret)

        # Obtener datos históricos
        start_timestamp = int(self.date_start.timestamp() * 1000)
        end_timestamp = int(self.date_end.timestamp() * 1000)

        klines = client.get_historical_klines(self.ticker, intervalo_horas, str(start_timestamp), str(end_timestamp))

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
                'volume': float(kline[5])
            })

        df = pd.DataFrame(data)
        df = df.sort_values(by='time').reset_index(drop=True)
        df['date'] = df['time'].dt.date
        df['openday'] = df.groupby('date')['open'].transform('first')
        df['incremento'] = df['high'] / df['openday']
        df['target'] = df[df['incremento'] > 1.015].groupby('date').count() / df.groupby('date').count

        print(df)

        self.df = pd.DataFrame(data)
        self.df = self.df.sort_values(by='time').reset_index(drop=True)
        self.df['date'] = self.df['time'].dt.date
        self.df['openday'] = self.df.groupby('date')['open'].transform('first')
        self.df['incremento'] = self.df['high'] / self.df['openday']
        self.df['target'] = self.df[self.df['incremento'] > 1.015].groupby('date').count() / self.df.groupby('date').count

        print(self.df)


def main():
    # Crear una instancia de la clase Cripto
    cripto = Cripto(ticker='SOLUSDT', period=1)

    # Puedes agregar aquí cualquier otra acción, como graficar los datos
    # Por ejemplo:
    # cripto.df.plot(x='time', y='close')
    # plt.show()

if __name__ == "__main__":
    main()