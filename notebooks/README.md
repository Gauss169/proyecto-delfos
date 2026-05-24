# Notebooks - Desarrollo de Modelos ML

Esta carpeta contiene notebooks de Jupyter para desarrollar, entrenar y evaluar nuevos modelos de Machine Learning.

## 📓 Notebooks Disponibles

### 1. `model_training.ipynb`
Notebook para entrenar nuevos modelos desde cero.

**Incluye**:
- Carga de datos históricos desde Binance
- Creación de features técnicas
- Entrenamiento de modelos (Gradient Boosting, Random Forest, etc.)
- Optimización de hiperparámetros
- Exportación del modelo para producción

### 2. `model_evaluation.ipynb`
Notebook para evaluar el rendimiento de modelos entrenados.

**Incluye**:
- Backtesting con datos históricos
- Métricas financieras (Sharpe Ratio, Max Drawdown, Win Rate)
- Análisis de rentabilidad
- Visualizaciones de rendimiento

## 🚀 Cómo Usar

### Configuración Inicial

1. **Instalar Jupyter**:
   ```bash
   pip install jupyter notebook
   ```

2. **Iniciar Jupyter**:
   ```bash
   cd notebooks
   jupyter notebook
   ```

3. **Configurar credenciales**:
   - Copia el archivo `.env.example` como `.env` en la raíz del proyecto
   - Añade tus credenciales de Binance

### Workflow de Desarrollo de Modelos

```
1. Exploración de datos
   ↓
2. Creación de features (model_training.ipynb)
   ↓
3. Entrenamiento del modelo (model_training.ipynb)
   ↓
4. Evaluación y backtesting (model_evaluation.ipynb)
   ↓
5. Exportar modelo a ../pipeline/models/
   ↓
6. Actualizar config.py con el nuevo modelo
   ↓
7. Probar en local antes de deployment
```

## 📦 Exportar Modelo a Producción

Después de entrenar un modelo en `model_training.ipynb`, exporta los archivos necesarios:

```python
import pickle

model_name = 'mi_nuevo_modelo'

# 1. Guardar modelo
with open(f'../pipeline/models/{model_name}.pkl', 'wb') as f:
    pickle.dump(model, f)

# 2. Guardar columnas (features)
with open(f'../pipeline/models/{model_name}_columns.pkl', 'wb') as f:
    pickle.dump(columns_list, f)

# 3. Guardar configuración de umbrales
umbral_config = [
    1.02,  # Take profit threshold (ej: vender a +2%)
    0.98,  # Stop loss threshold (ej: vender a -2%)
    0.5    # Umbral de probabilidad del modelo
]

with open(f'../pipeline/models/{model_name}_umbral.pkl', 'wb') as f:
    pickle.dump(umbral_config, f)
```

## 🔧 Conectar Modelo al Pipeline

Una vez exportado el modelo, actualiza `../pipeline/config.py`:

```python
MODEL_CONFIG = {
    'model_path': 'models/mi_nuevo_modelo.pkl',
    'columns_path': 'models/mi_nuevo_modelo_columns.pkl',
    'threshold_path': 'models/mi_nuevo_modelo_umbral.pkl',
    'prediction_period': 370,
    'prediction_hour': 10
}
```

## 📊 Datos para Entrenamiento

### Obtener Datos Históricos

Usa la API de Binance directamente desde los notebooks:

```python
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()
client = Client(os.getenv("BINANCE_API_KEY"), os.getenv("BINANCE_SECRET"))

# Descargar datos
klines = client.get_historical_klines(
    "SOLUSDC",
    Client.KLINE_INTERVAL_1HOUR,
    "1 Jan, 2023",
    "1 Jan, 2024"
)
```

### Criptomonedas Soportadas

El sistema actual soporta:
- SOL (Solana)
- BTC (Bitcoin)
- ETH (Ethereum)
- XRP (Ripple)

Para añadir más, actualiza la función `add_crypto_features()` en `predictor.py`.

## 🧪 Testing de Modelos

Antes de poner un modelo en producción:

1. **Backtesting exhaustivo**: Mínimo 6 meses de datos históricos
2. **Validación cruzada**: Evitar overfitting
3. **Análisis de riesgo**: Max Drawdown, Sharpe Ratio
4. **Prueba en testnet**: Usar Binance Testnet primero
5. **Paper trading**: Simular operaciones sin dinero real

## 💡 Tips para Mejorar Modelos

### Features Efectivas
- Medias móviles de diferentes períodos
- Ratios de volatilidad
- Dinámicas entre períodos cortos y largos
- Pendientes de tendencias
- Volumen de trading

### Evitar Overfitting
- Usar validación cruzada temporal (no aleatoria)
- No usar demasiadas features correlacionadas
- Regularización en los modelos
- Probar en datos out-of-sample

### Optimización
- Grid search para hiperparámetros
- Optimizar umbral de decisión según tu tolerancia al riesgo
- Considerar costos de transacción en el backtesting

## 📚 Recursos Adicionales

- [Documentación Binance API](https://binance-docs.github.io/apidocs/)
- [Scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [TA-Lib (Technical Analysis)](https://mrjbq7.github.io/ta-lib/)

## ⚠️ Advertencias

- **Nunca** entrenes modelos con datos futuros (data leakage)
- **Siempre** usa datos out-of-sample para evaluación final
- **Considera** los costos de transacción en tus backtests
- **Recuerda** que rendimiento pasado no garantiza rendimiento futuro
- **Prueba** exhaustivamente antes de usar dinero real
