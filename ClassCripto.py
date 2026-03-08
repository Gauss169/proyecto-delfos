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
        def compute_target(group):
            # Índice del primer high_return > 1.015
            high_idx = group.index[group['high_return'] > 1.015]
            # Índice del primer low_return < 0.97
            low_idx = group.index[group['low_return'] < 0.97]
        
            # Si no ocurre high o low, target = 0
            if len(high_idx) == 0:
                return pd.Series([0] * len(group), index=group.index)
            if len(low_idx) == 0:
                return pd.Series([1] * len(group), index=group.index)
        
            h = high_idx[0]
            l = low_idx[0]
        
            # Caso mismo instante → target = 0
            if group.loc[h, 'time'] == group.loc[l, 'time']:
                return pd.Series([0] * len(group), index=group.index)
        
            # high sucede antes que low → target = 1
            if group.loc[h, 'time'] < group.loc[l, 'time']:
                return pd.Series([1] * len(group), index=group.index)
        
            # low sucede primero → target = 0
            return pd.Series([0] * len(group), index=group.index)
        
        # Asignar target_basica a cada fila intradía
        self.df['target_basica'] = self.df.groupby('date', group_keys=False).apply(compute_target)


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
        # ===== PASAR target_basica AL NIVEL DIARIO =====
        daily_target = self.df.groupby('date')['target_basica'].max()
        
        self.df_summary['target_basica'] = self.df_summary['date'].map(daily_target)

        # Ahora, calcular los indicadores en el df_summary (después de agregación)
        n = 14  # Período para RSI
        # Calcular el RSI
        change = self.df_summary['close_day'].diff(1)
        self.df_summary['Gain'] = change.mask(change < 0, 0)
        self.df_summary['Loss'] = abs(change.mask(change > 0, 0))
        self.df_summary['AVG_Gain'] = self.df_summary['Gain'].rolling(n).mean()
        self.df_summary['AVG_Loss'] = self.df_summary['Loss'].rolling(n).mean()
        self.df_summary['RS'] = self.df_summary['AVG_Gain'] / self.df_summary['AVG_Loss']
        self.df_summary['RSI'] = 100 - (100 / (1 + self.df_summary['RS']))
        
        
        # Calcular Stochastic RSI
        self.df_summary['RSIMAX'] = self.df_summary['RSI'].rolling(n).max()
        self.df_summary['RSIMIN'] = self.df_summary['RSI'].rolling(n).min()
        self.df_summary['StochRSI'] = (self.df_summary['RSI'] - self.df_summary['RSIMIN']) / (self.df_summary['RSIMAX'] - self.df_summary['RSIMIN'])

        # Calcular MACD
        periodo_corto = 12
        periodo_largo = 26
        periodo_señal = 9

        self.df_summary['ema_corto'] = self.df_summary['close_day'].ewm(span=periodo_corto, adjust=False).mean()
        self.df_summary['ema_largo'] = self.df_summary['close_day'].ewm(span=periodo_largo, adjust=False).mean()

        # Calcular la línea MACD
        self.df_summary['macd_line'] = self.df_summary['ema_corto'] - self.df_summary['ema_largo']

        # Calcular la línea de señal MACD
        self.df_summary['macd_signal'] = self.df_summary['macd_line'].ewm(span=periodo_señal, adjust=False).mean()
        self.df_summary['return_change'] = self.df_summary['RP_return'].diff()
        self.df_summary['return_accel'] = self.df_summary['return_change'].diff()  # segunda derivada
        self.df_summary['RP_return_ema'] = self.df_summary['RP_return'].ewm(span=n).mean()
        self.df_summary['volume_high_ema'] = self.df_summary['volume_high'].ewm(span=n).mean()
        self.df_summary['volume_low_ema'] = self.df_summary['volume_low'].ewm(span=n).mean()



        # Oferta y Demanda
        self.df_summary['oferta_demanda'] = np.where(
            self.df_summary['close_day'] == self.df_summary['open_day'], 
            0, 
            self.df_summary['high_day'] * ((self.df_summary['close_day'] - self.df_summary['open_day']) / abs(self.df_summary['close_day'] - self.df_summary['open_day']))
        )
        
        self.df_summary['oferta_demanda_mean'] = self.df_summary['oferta_demanda'].rolling(n).mean()
        self.df_summary['oferta_demanda_slope'] = self.df_summary['oferta_demanda'].diff()
        self.df_summary['oferta_demanda_ratio'] = (
            self.df_summary['volume_high'] / (self.df_summary['volume_low'] + 1e-9)
        ) * np.sign(self.df_summary['oferta_demanda'])


        self.df_summary['RP_vol_mix'] = (
            self.df_summary['RP_return'] * (self.df_summary['volume_high'] - self.df_summary['volume_low'])
        )
        self.df_summary['volatility_index'] = (
            self.df_summary['high_var'] + self.df_summary['low_var']
        )
        self.df_summary['RSI_MACD_interact'] = self.df_summary['RSI'] * self.df_summary['macd_line']

        self.df_summary['high_low_ratio'] = self.df_summary['volume_high'] / (self.df_summary['volume_low'] + 1e-9)
        self.df_summary['high_low_diff'] = self.df_summary['volume_high'] - self.df_summary['volume_low']
        self.df_summary['RP_vol_high_ratio'] = self.df_summary['RP_return'] / (self.df_summary['volume_high'] + 1e-9)
        self.df_summary['RP_vol_low_ratio'] = self.df_summary['RP_return'] / (self.df_summary['volume_low'] + 1e-9)
        
        self.df_summary['RP_return_z'] = (
            (self.df_summary['RP_return'] - self.df_summary['RP_return'].rolling(n).mean()) /
            self.df_summary['RP_return'].rolling(n).std()
        )
        
        self.df_summary['corr_high_low'] = (
            self.df_summary['volume_high'].rolling(n)
            .corr(self.df_summary['volume_low'])
        )
        self.df_summary['corr_RP_volume'] = (
            self.df_summary['RP_return'].rolling(n)
            .corr(self.df_summary['volume_high'])
        )

        # Índice de presión compradora-vendedora (versión mejorada)
        self.df_summary['OD_pressure'] = (
            ((self.df_summary['close_day'] - self.df_summary['low_day']) /
             (self.df_summary['high_day'] - self.df_summary['low_day'] + 1e-9))  # Normaliza entre 0-1
            * (self.df_summary['high_day'] - self.df_summary['low_day'])          # Añade fuerza del rango
            * (self.df_summary['volume_high'] - self.df_summary['volume_low'])    # Incluye componente de volumen
        )

        self.df_summary['OD_pressure_norm'] = (
            2 * ((self.df_summary['close_day'] - self.df_summary['low_day']) /
                 (self.df_summary['high_day'] - self.df_summary['low_day'] + 1e-9)) - 1
        ) * (self.df_summary['volume_high'] - self.df_summary['volume_low'])



        for i in range(n):
            self.df_summary[f"volume_high_{i+1}"] = self.df_summary['volume_high'].shift(i)
            self.df_summary[f"volume_low_{i+1}"] = self.df_summary['volume_low'].shift(i)
            self.df_summary[f"volume_high_{i+1}^2"] = self.df_summary[f"volume_high_{i+1}"]**2
            self.df_summary[f"volume_low_{i+1}^2"] = self.df_summary[f"volume_low_{i+1}"]**2
            self.df_summary[f"volume_high_{i+1}^3"] = self.df_summary[f"volume_high_{i+1}"]**3
            self.df_summary[f"volume_low_{i+1}^3"] = self.df_summary[f"volume_low_{i+1}"]**3
            self.df_summary[f'RP_return_{i}'] = self.df_summary["RP_return"].shift(i)
  

        self.df_summary['target'] = self.df_summary['volume_high'].apply(lambda x: 1 if x > 0 else 0)
        columnas = list(set(self.df_summary.columns) - set(['target','date']))
        self.df_summary[columnas] = self.df_summary[columnas].shift(1)
        
        for i in range(2,n-1):
            self.df_summary[f'volume_high_mean_{i}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).mean()        
            self.df_summary[f'volume_high_hmean_{i}'] = (
                self.df_summary[f"volume_high_{i+1}"]
                .rolling(n)
                .apply(lambda x: hmean(x) if all(x > 0) else float('nan'))
            )       
            self.df_summary[f'volume_high_median_{i}'] = (
                self.df_summary[f"volume_high_{i+1}"].rolling(n).median()
            )
            self.df_summary[f'volume_high_var_{i}'] = (
                self.df_summary[f"volume_high_{i+1}"].rolling(n).var()
            )
            self.df_summary[f'volume_high_prod_{i}'] = (
                self.df_summary[f"volume_high_{i+1}"].rolling(n).apply(lambda x: x.prod())
            )
            
            # Media aritmética
            self.df_summary[f'volume_low_mean_{i}'] = (
                self.df_summary[f"volume_low_{i+1}"].rolling(n).mean()
            )
        
            # Media armónica
            self.df_summary[f'volume_low_hmean_{i}'] = (
                self.df_summary[f"volume_low_{i+1}"]
                .rolling(n)
                .apply(lambda x: hmean(x) if all(x > 0) else float('nan'))
            )
        
            # Mediana
            self.df_summary[f'volume_low_median_{i}'] = (
                self.df_summary[f"volume_low_{i+1}"].rolling(n).median()
            )
        
            # Varianza
            self.df_summary[f'volume_low_var_{i}'] = (
                self.df_summary[f"volume_low_{i+1}"].rolling(n).var()
            )
        
            # Producto
            self.df_summary[f'volume_low_prod_{i}'] = (
                self.df_summary[f"volume_low_{i+1}"]
                .rolling(n)
                .apply(lambda x: x.prod())
            )
            
            self.df_summary[f'RP_return_mean_{i}'] = (
                self.df_summary[f"RP_return_{i+1}"].rolling(n).mean()
            )
        
            # Media armónica
            self.df_summary[f'RP_return_hmean_{i}'] = (
                self.df_summary[f"RP_return_{i+1}"]
                .rolling(n)
                .apply(lambda x: hmean(x) if all(x > 0) else float('nan'))
            )
        
            # Mediana
            self.df_summary[f'RP_return_median_{i}'] = (
                self.df_summary[f"RP_return_{i+1}"].rolling(n).median()
            )
        
            # Varianza
            self.df_summary[f'RP_return_var_{i}'] = (
                self.df_summary[f"RP_return_{i+1}"].rolling(n).var()
            )
        
            # Producto
            self.df_summary[f'RP_return_prod_{i}'] = (
                self.df_summary[f"RP_return_{i+1}"]
                .rolling(n)
                .apply(lambda x: x.prod())
            )
            self.df_summary[f'volume_high_std_{i+1}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).std()  # Desviación estándar
            self.df_summary[f'volume_high_skew_{i+1}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).skew() # Asimetría
            self.df_summary[f'volume_high_kurt_{i+1}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).kurt() # Curtosis
            self.df_summary[f'volume_high_min_{i+1}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).min()
            self.df_summary[f'volume_high_max_{i+1}'] = self.df_summary[f"volume_high_{i+1}"].rolling(n).max()
            self.df_summary[f'volume_high_range_{i+1}'] = (
                self.df_summary[f'volume_high_max_{i+1}'] - self.df_summary[f'volume_high_min_{i+1}']
            )
# Crear una instancia de la clase Cripto
avax = Cripto('DOGEUSDT', 5)

# Imprimir el DataFrame resumido con las columnas que deseas
print(avax.df_summary)
"""
# Graficar los resultados
plt.figure(figsize=(10, 6))

# Histograma para target_high
plt.subplot(2, 2, 1)
plt.plot(avax.df_summary.date,avax.df_summary.high_day, color = 'blue')
plt.title('Histograma de Target High')

# Histograma para target_low
plt.subplot(2, 2, 2)
plt.plot(avax.df_summary.date, avax.df_summary.target_high, color = 'red')
plt.legend()
plt.title('Evolución de var a lo largo del tiempo')

# Gráfico de target_high
plt.subplot(2, 2, 3)
plt.scatter(avax.df_summary['target_high'],avax.df_summary['target_high'].shift(), color = 'green')
plt.xlabel('Target_high')
plt.ylabel('Target_low')
plt.title('Relación Target_high-Target_low_shift')


# Gráfico de target_low
plt.subplot(2, 2, 4)
plt.scatter(avax.df_summary['target_high'],avax.df_summary['RP'].shift(), color = 'green')
plt.xlabel('Target_high')
plt.ylabel('Target_low')
plt.title('Relación Target_high-Target_high_shift')

# Ajustar el layout
plt.tight_layout()
plt.show()
"""
# Guardar el df_summary en un archivo CSV
avax.df_summary.to_csv('doge_summary_1,5_more_variables.csv', index=False)
