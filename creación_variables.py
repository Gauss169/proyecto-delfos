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
        #self.df[['open','high','low','close','volume']] = self.df[['open','high','low','close','volume']].shift(-hour*2)
        self.df['openday'] = self.df.groupby('date')['open'].transform('first')
        self.df['volume_open'] =  self.df.groupby('date')['volume'].transform('first')
        self.df['volume_intraday'] = self.df['volume'] / self.df['volume_open']
        self.df['high_return_intraday'] = self.df['high'] / self.df['openday']
        self.df['close_return_intraday'] = self.df['close'] / self.df['openday']
        self.df['low_return_intraday'] = self.df['low'] / self.df['openday']
        self.df['RP_return_intraday'] = self.df[['low_return_intraday','high_return_intraday']].apply(lambda x: x['high_return_intraday'] if abs(x['high_return_intraday'] - 1) > abs(x['low_return_intraday'] - 1) else x['low_return_intraday'], axis = 1)
        self.df['high_return_intrahour'] = self.df['high'] / self.df['open']
        self.df['close_return_intrahour'] = self.df['close'] / self.df['open']
        self.df['low_return_intrahour'] = self.df['low'] / self.df['open']
        self.df['RP_return_intrahour'] = self.df[['low_return_intrahour','high_return_intrahour']].apply(lambda x: x['high_return_intrahour'] if abs(x['high_return_intrahour'] - 1) > abs(x['low_return_intrahour'] - 1) else x['low_return_intrahour'], axis = 1)



        # Crear target_basica por día
        def compute_target(group, umbral_high, umbral_low):
            # Índice del primer high_return > 1.015
            high_idx = group.index[group['high_return'] > umbral_high]
            # Índice del primer low_return < 0.97
            low_idx = group.index[group['low_return'] < umbral_low]
        
            # ===== CASO NUEVO =====
            # Si NO ocurre NINGUNO (ni high ni low)
            if len(high_idx) == 0 and len(low_idx) == 0:
                return pd.Series(2, index=group.index)
        
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
            high_day=('high_return_intraday', 'max'),
            low_day=('low_return_intraday', 'min'),
        ).reset_index()
        self.df_summary['date'] = pd.to_datetime(self.df_summary['date'])
    def create_features(self,x):
        dataset = self.df.groupby('date').agg(
            media = (x,'mean'),
            mediana = (x,'median'),
            varianza = (x,'var'),
            maximo = (x,'max'),
            minimo = (x, 'min'),
            q1 = (x,lambda x: x.quantile(0.25)),
            q3 = (x,lambda x: x.quantile(0.75)),
            primera = (x, 'first'),
            ultima = (x,'last')
            ).reset_index()


        self.df_summary[f'{x}_mean'] = dataset['media']
        self.df_summary[f'{x}_median'] = dataset['mediana']
        self.df_summary[f'{x}_sesgo'] = self.df_summary[f'{x}_mean'] - self.df_summary[f'{x}_median']
        self.df_summary[f'{x}_var'] = dataset['varianza']
        self.df_summary[f'{x}_min'] = dataset['minimo']
        self.df_summary[f'{x}_max'] = dataset['maximo']
        self.df_summary[f'{x}_q1'] = dataset['q1']
        self.df_summary[f'{x}_q3'] = dataset['q3']
        self.df_summary[f'{x}_manana'] = dataset['primera']
        self.df_summary[f'{x}_noche'] = dataset['ultima']


    def indicadores(self,x, n):
        dataset = self.df_summary.copy()
        change = dataset[x].diff(1)
        dataset['Gain'] = change.mask(change < 0, 0)
        dataset['Loss'] = abs(change.mask(change > 0, 0))
        dataset['AVG_Gain'] = dataset['Gain'].rolling(n).mean()
        dataset['AVG_Loss'] = dataset['Loss'].rolling(n).mean()
        dataset['RS'] = dataset['AVG_Gain'] / dataset['AVG_Loss']
        dataset['RSI'] = 100 - (100 / (1 + dataset['RS']))
        
        # Calcular Stochastic RSI
        dataset['RSIMAX'] = dataset['RSI'].rolling(n).max()
        dataset['RSIMIN'] = dataset['RSI'].rolling(n).min()
        dataset['StochRSI'] = (dataset['RSI'] - dataset['RSIMIN']) / (dataset['RSIMAX'] - dataset['RSIMIN'])

        

        
        dataset[f'{n}_mean'] = dataset[x].rolling(n).mean()
        dataset[f'{n}_median'] = dataset[x].rolling(n).median()
        dataset[f'{n}_min'] = dataset[x].rolling(n).min()
        dataset[f'{n}_max'] = dataset[x].rolling(n).max()
        dataset[f'{n}_var'] = dataset[x].rolling(n).var()
        dataset[f'{n}_sesgo'] = dataset[f'{n}_mean'] - dataset[f'{n}_median']
        #dataset[f'{n}_hmean'] = dataset[f'{n}_hmean'].rolling(n).apply(lambda x: hmean(x) if all(x > 0) else float('nan'))
        #dataset[f'{n}_prod'] = dataset[f'{n}_prod'].rolling(n).apply(lambda x: x.prod())
        self.df_summary[f'{x}_RS'] = dataset['RS']
        self.df_summary[f'{x}_RSI'] = dataset['RSI']
        self.df_summary[f'{x}_RSIMAX'] = dataset['RSIMAX']
        self.df_summary[f'{x}_RSIMIN'] = dataset['RSIMIN']
        self.df_summary[f'{x}_StochRSI'] = dataset['StochRSI']
        
        # Estadísticas rolling con ventana n
        self.df_summary[f'{x}_{n}_mean'] = dataset[f'{n}_mean']
        self.df_summary[f'{x}_{n}_median'] = dataset[f'{n}_median']
        self.df_summary[f'{x}_{n}_min'] = dataset[f'{n}_min']
        self.df_summary[f'{x}_{n}_max'] = dataset[f'{n}_max']
        self.df_summary[f'{x}_{n}_var'] = dataset[f'{n}_var']
        self.df_summary[f'{x}_{n}_sesgo'] = dataset[f'{n}_sesgo']
        #self.df_summary[f'{x}_{n}_hmean'] = dataset[f'{n}_hmean']
        #self.df_summary[f'{x}_{n}_prod'] = dataset[f'{n}_prod']


        
    def macd(self,x):
        dataset = self.df_summary.copy()
        # Calcular MACD
        periodo_corto = 12
        periodo_largo = 26
        periodo_señal = 9
        
        dataset['ema_corto'] = dataset[x].ewm(span=periodo_corto, adjust=False).mean()
        dataset['ema_largo'] = dataset[x].ewm(span=periodo_largo, adjust=False).mean()
        
        # Calcular la línea MACD
        dataset['macd_line'] = dataset['ema_corto'] - dataset['ema_largo']
        
        # Calcular la línea de señal MACD
        dataset['macd_signal'] = dataset['macd_line'].ewm(span=periodo_señal, adjust=False).mean()
        
        self.df_summary[f'{x}_macd_line'] = dataset['macd_line']
        self.df_summary[f'{x}_macd_signal'] = dataset['macd_signal']

            
        
        """
        umbrales_high = np.linspace(1.001,1.05,50)
        umbrales_low = np.linspace(0.9,0.99, 10)
        self.result_final = {}
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
                self.result_final[(umbral_high,umbral_low)] = result
                self.result_umbral_max[(umbral_high,umbral_low)] = np.max(list(result.values()))
                self.result_umbral_min[(umbral_high,umbral_low)] = np.min(list(result.values()))
                self.result_umbral_mean[(umbral_high,umbral_low)] = np.mean(list(result.values()))
                self.result_umbral_median[(umbral_high,umbral_low)] = np.median(list(result.values()))

        # Asignar target_basica a cada fila intradía
        """


cripto = Cripto("SOLUSDT",6, hour = 8)

variables = ['volume_intraday','high_return_intraday','close_return_intraday',
             'low_return_intraday','RP_return_intraday',
             'high_return_intrahour','close_return_intrahour',
             'low_return_intrahour','RP_return_intrahour']
for x in variables:
    cripto.create_features(x)
    for a in ['mean','median','min','max','var','q1','q3','sesgo','manana','noche']:
        cripto.macd(f'{x}_{a}')
        for n in range(2,14):
            cripto.indicadores(f'{x}_{a}',n)
cripto.df_summary.to_csv('solana_2.csv', index=False)

"""
# Encontrar el umbral con ganancia máxima
umbral_max, gan_max = max(cripto.result_umbral_max.items(), key=lambda x: x[1])
umbral_min_max, gan_min_max = max(cripto.result_umbral_min.items(), key=lambda x: x[1])
umbral_mean, gan_mean = max(cripto.result_umbral_mean.items(), key=lambda x: x[1])
umbral_median, gan_median = max(cripto.result_umbral_median.items(), key=lambda x: x[1])

print(f"El umbral donde la ganancia máxima fue máxima fue {umbral_max}, con ganancia {cripto.result_final[umbral_max]}")
print(f"El umbral donde la ganancia mínima fue máxima fue {umbral_min_max}, con ganancia {cripto.result_final[umbral_min_max]}")
print(f"El umbral donde la ganancia median fue máxima fue {umbral_mean}, con ganancia {cripto.result_final[umbral_mean]}")
print(f"El umbral donde la ganancia mediana fue máxima fue {umbral_median}, con ganancia {cripto.result_final[umbral_median]}")
"""