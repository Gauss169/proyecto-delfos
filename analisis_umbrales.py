import pandas as pd
from datetime import datetime, timedelta, timezone
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import hmean

class Cripto:
    def __init__(self, ticker, period, date_end=None, hour=0):
        self.ticker = ticker
        if date_end is None:
            self.date_end = datetime.now(timezone.utc)
        else:
            self.date_end = date_end
        self.date_start = self.date_end - timedelta(days=365 * period)
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

        self.df = pd.DataFrame(data)
        self.df = self.df.sort_values(by='time').reset_index(drop=True)
        self.df['date'] = self.df['time'].dt.date
        self.df['openday'] = self.df.groupby('date')['open'].transform('first')
        self.df['high_return'] = self.df['high'] / self.df['openday']
        self.df['low_return'] = self.df['low'] / self.df['openday']
        self.df['RP_return'] = self.df[['low_return','high_return']].apply(lambda x: x['high_return'] if abs(x['high_return'] - 1) > abs(x['low_return'] - 1) else x['low_return'], axis = 1)

        # Calcular el porcentaje de incrementos mayores a 1.015 y menores a 0.985 por día
        total_por_dia = self.df.groupby('date').size()

        high_return_per_day = self.df[self.df['high_return'] > 1.015].groupby('date').size()
        low_return_per_day = self.df[self.df['low_return'] < 0.985].groupby('date').size()

        # El porcentaje de incrementos > 1.015 y < 0.985 por día
        self.df['volume_high'] = self.df['date'].map(lambda x: (high_return_per_day.get(x, 0) / total_por_dia.get(x, 1)))
        self.df['volume_low'] = self.df['date'].map(lambda x: (low_return_per_day.get(x, 0) / total_por_dia.get(x, 1)))

        # Crear target_basica por día
        def compute_target(group, umbral_high, umbral_low):
            # Índice del primer high_return > 1.015
            high_idx = group.index[group['high_return'] > umbral_high]
            # Índice del primer low_return < 0.97
            low_idx = group.index[group['low_return'] < umbral_low]
        
            # ===== CASO NUEVO =====
            # Si NO ocurre NINGUNO (ni high ni low)
            if len(high_idx) == 0 and len(low_idx) == 0:
                # close_return = close_day / open_day
                close_return = group['close'].iloc[-1] / group['open'].iloc[0]
                return pd.Series(close_return, index=group.index)
        
            # ===== CASOS ANTERIORES =====
        
            # Si no ocurre high pero si ocurre low → 0
            if len(high_idx) == 0:
                return pd.Series(0, index=group.index)
        
            # Si no ocurre low pero si ocurre high → 1
            if len(low_idx) == 0:
                return pd.Series(1, index=group.index)
        
            h = high_idx[0]
            l = low_idx[0]
        
            # Si ocurren en el mismo timestamp → 0
            if group.loc[h, 'time'] == group.loc[l, 'time']:
                return pd.Series(0, index=group.index)
        
            # Si high sucede antes que low → 1
            if group.loc[h, 'time'] < group.loc[l, 'time']:
                return pd.Series(1, index=group.index)
        
            # Si low sucede antes que high → 0
            return pd.Series(0, index=group.index)


        # Crear el nuevo DataFrame con las columnas deseadas
        self.df_summary = self.df.groupby('date').agg(
            open_day=('openday', 'first'),
            close_day=('close', 'last'),
            high_day=('high_return', 'max'),
            low_day=('low_return', 'min'),
            high_var=('high_return','var'),
            low_var=('low_return','var'),
            high_mean=('high_return','mean'),
            low_mean=('low_return','mean'),
            high_median=('high_return','median'),
            low_median=('low_return','median'),
            volume_high=('volume_high', 'first'),
            volume_low=('volume_low', 'first'),
            # Cálculo de los cuartiles
            high_q1=('high_return', lambda x: x.quantile(0.25)),
            high_q3=('high_return', lambda x: x.quantile(0.75)),
            low_q1=('low_return', lambda x: x.quantile(0.25)),
            low_q3=('low_return', lambda x: x.quantile(0.75)),
            RP=('RP_return','mean'),
            RP_return = ('RP_return', 'first')
        ).reset_index()

        self.df_summary['date'] = pd.to_datetime(self.df_summary['date'])
        umbrales_high = np.linspace(1.001,1.05,50)
        umbrales_low = np.linspace(0.9,0.99, 10)
        self.result_umbral_max = {}
        self.result_umbral_min = {}
        self.result_umbral_mean = {}
        self.result_umbral_median = {}
        for umbral_high in umbrales_high:
            for umbral_low in umbrales_low:
                result = {}
                self.df[f'target_basica_{umbral_high}_{umbral_low}'] = self.df.groupby('date', group_keys=False).apply(compute_target, umbral_high=umbral_high, umbral_low = umbral_low)
                # ===== PASAR target_basica AL NIVEL DIARIO =====
                daily_target = self.df.groupby('date')[f'target_basica_{umbral_high}_{umbral_low}'].max()
                self.df_summary[f'target_basica_{umbral_high}_{umbral_low}'] = self.df_summary['date'].map(daily_target)
                dataset = self.df_summary
                for i in range(period):
                    dataset_filtered = dataset[
                            (dataset['date'] >= pd.to_datetime(f"202{i}-01-01")) &
                            (dataset['date'] <= pd.to_datetime(f"202{i+1}-12-31"))
                        ]
                    p = 1
                    for j in range(len(dataset_filtered)):
                        obs = dataset_filtered.iloc[j]
                        if obs[f'target_basica_{umbral_high}_{umbral_low}'] == 0:
                            p *= umbral_low
                        elif obs[f'target_basica_{umbral_high}_{umbral_low}'] == 1:
                            p *= umbral_high
                        else:
                            p *= obs['close_day'] / obs['open_day']
                    result[f'202{i}-01-01'] = p
            
                self.result_umbral_max[(umbral_high,umbral_low)] = np.max(list(result.values()))
                self.result_umbral_min[(umbral_high,umbral_low)] = np.min(list(result.values()))
                self.result_umbral_mean[(umbral_high,umbral_low)] = np.mean(list(result.values()))
                self.result_umbral_median[(umbral_high,umbral_low)] = np.median(list(result.values()))

        # Asignar target_basica a cada fila intradía



cripto = Cripto("SOLUSDT",6)



# Encontrar el umbral con ganancia máxima
umbral_max, gan_max = max(cripto.result_umbral_max.items(), key=lambda x: x[1])
umbral_min_max, gan_min_max = max(cripto.result_umbral_min.items(), key=lambda x: x[1])
umbral_mean, gan_mean = max(cripto.result_umbral_mean.items(), key=lambda x: x[1])
umbral_median, gan_median = max(cripto.result_umbral_median.items(), key=lambda x: x[1])

print(f"El umbral donde la ganancia máxima fue máxima fue {umbral_max}, con ganancia {gan_max}")
print(f"El umbral donde la ganancia mínima fue máxima fue {umbral_min_max}, con ganancia {gan_min_max}")
print(f"El umbral donde la ganancia median fue máxima fue {umbral_mean}, con ganancia {gan_mean}")
print(f"El umbral donde la ganancia mediana fue máxima fue {umbral_median}, con ganancia {gan_median}")