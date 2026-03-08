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
period = 2
hour = 14
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
    # DATAFRAME HORARIO
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
            'volume': float(kline[5]),        # cantidad cripto
            'quote_volume': float(kline[7])   # USDC
        })

    aux = pd.DataFrame(rows)

    # =====================
    # AGREGACIÓN DIARIA
    # =====================
    aux['date'] = pd.to_datetime(aux['time'])
    aux['date'] = aux['date'].shift(-hour)
    aux['day'] = aux['date'].dt.date

    df = aux.groupby('day').agg(
        open=('open', 'first'),
        close=('close', 'last'),
        high=('high', 'max'),
        low=('low', 'min'),
        volume=('volume', 'sum'),
        quote_volume=('quote_volume', 'sum')
    ).reset_index().rename(columns={'day': 'date'})

    # =====================
    # PRECIO REAL (VWAP)
    # =====================
    df[f'real_value_{cripto}'] = df['quote_volume'] / df['volume']

    # =====================
    # RENOMBRAR
    # =====================
    df.rename(columns={
        'open': f'open_{cripto}',
        'close': f'close_{cripto}',
        'high': f'high_{cripto}',
        'low': f'low_{cripto}',
        'volume': f'volume_{cripto}',
        'quote_volume': f'quote_volume_{cripto}'
    }, inplace=True)

    # =====================
    # MERGE
    # =====================
    if df_final is None:
        df_final = df
    else:
        df_final = df_final.merge(df, how='left', on='date')

# =====================
# NORMALIZACIÓN Y GRÁFICO
# =====================
for cripto in criptos:
    df_final[f'open_norm_{cripto}'] = (
        df_final[f'open_{cripto}'] / df_final[f'open_{cripto}'].iloc[0]
    )

    df_final[f'real_value_norm_{cripto}'] = (
        df_final[f'real_value_{cripto}'] / df_final[f'real_value_{cripto}'].iloc[0]
    )

    df_final[f'comparison_{cripto}'] = df_final[f'real_value_norm_{cripto}'] / df_final[f'open_norm_{cripto}']
    plt.figure(figsize=(12, 6))

    plt.plot(
        df_final['date'],
        df_final[f'open_norm_{cripto}'],
        label='Open (normalizado)',
        linewidth=2
    )

    plt.plot(
        df_final['date'],
        df_final[f'real_value_norm_{cripto}'],
        label='Precio real (VWAP)',
        linewidth=2
    )

    plt.legend()
    plt.grid(alpha=0.3)
    plt.title(f"Open vs Precio Real (VWAP) – {cripto.upper()}")
    plt.xlabel("Fecha")
    plt.ylabel("Índice (base = 1)")
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(12, 6))

    plt.plot(
        df_final['date'],
        df_final[f'comparison_{cripto}'],
        label='Comparison (normalizado)',
        linewidth=2
    )
    
    plt.legend()
    plt.grid(alpha=0.3)
    plt.title(f"Comparación de open con precio medio – {cripto.upper()}")
    plt.xlabel("Fecha")
    plt.ylabel("Índice (base = 1)")
    plt.tight_layout()
    plt.show()
    
    df_final[f'mean_price_ratio_{cripto}'] = np.log(df_final[f'real_value_norm_{cripto}'] / df_final[f'real_value_norm_{cripto}'].shift(1))
    plt.figure(figsize=(12, 6))

    plt.plot(
        df_final['date'],
        df_final[f'mean_price_ratio_{cripto}'],
        label='Comparison (normalizado)',
        linewidth=2
    )
    
    plt.legend()
    plt.grid(alpha=0.3)
    plt.title(f"Ratio precio medio – {cripto.upper()}")
    plt.xlabel("Fecha")
    plt.ylabel("Índice (base = 1)")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(12, 6))
    plt.hist(df_final[f'mean_price_ratio_{cripto}'], bins = 20, edgecolor = 'white')
    plt.show()
    
    import numpy as np
    import scipy.stats as stats
    import matplotlib.pyplot as plt
    
    data = df_final[f'mean_price_ratio_{cripto}'].dropna()
    
    # Test de normalidad (Shapiro-Wilk)
    stat, p_value = stats.shapiro(data)
    
    print(f"Shapiro-Wilk statistic: {stat:.4f}")
    print(f"p-value: {p_value:.4e}")

    jb_stat, jb_p = stats.jarque_bera(data)
    
    print(f"Jarque-Bera statistic: {jb_stat:.4f}")
    print(f"p-value: {jb_p:.4e}")

    # Parámetros de la normal ajustada
    mu, sigma = data.mean(), data.std()
    
    # Histograma normalizado
    plt.figure(figsize=(12, 6))
    plt.hist(data, bins=20, density=True, edgecolor='white', alpha=0.7)
    
    # Curva normal teórica
    x = np.linspace(data.min(), data.max(), 300)
    pdf = stats.norm.pdf(x, mu, sigma)
    plt.plot(x, pdf, linewidth=2, label='Normal teórica')
    
    plt.title(
        f"Histograma + Normal teórica – {cripto.upper()}\n"
        f"Shapiro p-value = {p_value:.2e}"
    )
    plt.xlabel("Mean price ratio")
    plt.ylabel("Densidad")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(6, 6))
    stats.probplot(data, dist="norm", plot=plt)
    plt.title(f"Q-Q plot – {cripto.upper()}")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    from scipy import stats
    
    data = df_final[f'mean_price_ratio_{cripto}'].dropna()
    
    # One-sample t-test contra media = 0
    t_stat, p_ttest = stats.ttest_1samp(data, 0)
    
    print(f"T-statistic: {t_stat:.4f}")
    print(f"p-value (t-test): {p_ttest:.4e}")
    
    # Media e intervalo de confianza
    mean = data.mean()
    std = data.std(ddof=1)
    n = len(data)
    
    alpha = 0.05
    t_crit = stats.t.ppf(1 - alpha/2, df=n-1)
    ci_low = mean - t_crit * std / np.sqrt(n)
    ci_high = mean + t_crit * std / np.sqrt(n)
    
    print(f"Mean return: {mean:.6f}")
    print(f"95% CI: [{ci_low:.6f}, {ci_high:.6f}]")

