# 🔌 Cómo Conectar un Nuevo Modelo al Pipeline

Esta guía te muestra paso a paso cómo conectar un modelo ML recién entrenado al pipeline de trading.

## 📋 Proceso Completo

### 1. Entrenar el Modelo en Jupyter

Abre `notebooks/model_training.ipynb` y entrena tu modelo.

Al final del notebook, **exporta 3 archivos**:

```python
import pickle

# Nombre de tu modelo (usa un nombre descriptivo)
model_name = 'gradient_boost_v2'  # Ejemplo

# 1️⃣ Guardar el modelo entrenado
with open(f'../pipeline/models/{model_name}.pkl', 'wb') as f:
    pickle.dump(model, f)

# 2️⃣ Guardar las columnas (features) que usa el modelo
# IMPORTANTE: Debe ser la lista exacta de columnas en el orden correcto
with open(f'../pipeline/models/{model_name}_columns.pkl', 'wb') as f:
    pickle.dump(X_train.columns.tolist(), f)

# 3️⃣ Guardar configuración de umbrales
umbral_config = [
    1.02,   # [0] Take profit: precio objetivo de venta (ej: +2%)
    0.98,   # [1] Stop loss: precio mínimo de venta (ej: -2%)
    0.65    # [2] Umbral de probabilidad del modelo para comprar
]

with open(f'../pipeline/models/{model_name}_umbral.pkl', 'wb') as f:
    pickle.dump(umbral_config, f)

print(f"✅ Modelo exportado a ../pipeline/models/{model_name}.*")
```

### 2. Verificar que los Archivos Existen

```bash
# Desde la raíz del proyecto
ls pipeline/models/

# Deberías ver:
# - gradient_boost_v2.pkl
# - gradient_boost_v2_columns.pkl
# - gradient_boost_v2_umbral.pkl
```

### 3. Actualizar la Configuración

Edita `pipeline/config.py`:

```python
MODEL_CONFIG = {
    'model_path': 'models/gradient_boost_v2.pkl',              # ← Tu modelo
    'columns_path': 'models/gradient_boost_v2_columns.pkl',    # ← Tus columnas
    'threshold_path': 'models/gradient_boost_v2_umbral.pkl',   # ← Tus umbrales
    'prediction_period': 370,  # Días de historia para predicción
    'prediction_hour': 10      # Hora de referencia para agrupar datos
}
```

### 4. Probar Localmente

```bash
cd pipeline
python bot.py
```

Verifica en los logs que:
- El modelo se carga correctamente
- Las predicciones se generan sin errores
- Los valores de predicción tienen sentido

### 5. Hacer Backtesting

Antes de usar en producción, evalúa el modelo:

```bash
cd notebooks
jupyter notebook model_evaluation.ipynb
```

Verifica:
- **Win Rate** > 50%
- **Sharpe Ratio** > 1.0 (idealmente)
- **Max Drawdown** aceptable para tu tolerancia al riesgo
- Rentabilidad positiva en diferentes períodos

### 6. Deploy a Producción

Una vez validado:

```bash
# Si usas Docker
cd deployment
docker-compose down
docker-compose up --build -d

# Si usas cloud (ej: Railway)
git add .
git commit -m "Update model to gradient_boost_v2"
git push origin main
# Railway hará deploy automático
```

---

## 🎯 Ejemplo Completo

### Escenario: Quieres usar un Random Forest en lugar de Gradient Boosting

**1. En `model_training.ipynb`:**

```python
from sklearn.ensemble import RandomForestClassifier

# Entrenar
model = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Evaluar
y_pred_proba = model.predict_proba(X_test)[:, 1]
# ... análisis de resultados ...

# Exportar
model_name = 'random_forest_v1'

with open(f'../pipeline/models/{model_name}.pkl', 'wb') as f:
    pickle.dump(model, f)

with open(f'../pipeline/models/{model_name}_columns.pkl', 'wb') as f:
    pickle.dump(X_train.columns.tolist(), f)

umbral_config = [1.025, 0.975, 0.60]  # Ajustado según backtesting

with open(f'../pipeline/models/{model_name}_umbral.pkl', 'wb') as f:
    pickle.dump(umbral_config, f)
```

**2. En `pipeline/config.py`:**

```python
MODEL_CONFIG = {
    'model_path': 'models/random_forest_v1.pkl',
    'columns_path': 'models/random_forest_v1_columns.pkl',
    'threshold_path': 'models/random_forest_v1_umbral.pkl',
    'prediction_period': 370,
    'prediction_hour': 10
}
```

**3. Probar:**

```bash
cd pipeline
python bot.py
```

---

## 🔧 Personalización Avanzada

### Cambiar Features (Variables)

Si tu nuevo modelo usa features diferentes:

1. **Modifica `predictor.py`** en la función `create_features()`:

```python
def create_features(df, rachas=RACHAS):
    # Tus features personalizadas
    df['mi_feature_custom'] = df['close'] / df['open'].shift(7)
    # ... más features
    return df
```

2. **Asegúrate** de que las columnas exportadas coincidan exactamente

### Cambiar Símbolo de Trading

En `pipeline/config.py`:

```python
TRADING_CONFIG = {
    'symbol': 'BTCUSDC',  # Cambiar de SOL a BTC
    # ...
}
```

Y actualiza las features de cripto en `predictor.py`:

```python
def add_crypto_features(df, symbol):
    df['cripto_SOL'] = symbol == 'SOLUSDC'
    df['cripto_BTC'] = symbol == 'BTCUSDC'  # ← Asegúrate de que coincida
    df['cripto_ETH'] = symbol == 'ETHUSDC'
    df['cripto_XRP'] = symbol == 'XRPUSDC'
    return df
```

### Múltiples Modelos (Ensemble)

Para usar varios modelos y promediar predicciones:

1. **Exporta varios modelos** con nombres diferentes
2. **Modifica `predictor.py`**:

```python
def predict(client, symbol):
    # ... código existente ...
    
    # Cargar múltiples modelos
    models = []
    for model_name in ['gb_low_model', 'random_forest_v1', 'xgboost_v1']:
        with open(f'models/{model_name}.pkl', 'rb') as f:
            models.append(pickle.load(f))
    
    # Promediar predicciones
    predictions = []
    for model in models:
        pred = model.predict_proba(data[cols].tail(1))[:, 1]
        predictions.append(pred[0])
    
    final_pred = np.mean(predictions)
    # ... resto del código
```

---

## ✅ Checklist de Conexión

- [ ] Modelo entrenado y evaluado en notebook
- [ ] 3 archivos .pkl exportados a `pipeline/models/`
- [ ] `config.py` actualizado con rutas correctas
- [ ] Bot probado localmente sin errores
- [ ] Backtesting realizado con resultados positivos
- [ ] Logs verificados (predicciones coherentes)
- [ ] Configuración de umbrales optimizada
- [ ] Deploy a producción realizado

---

## ⚠️ Errores Comunes

### "KeyError: 'columna_x'"
**Causa**: Las columnas del modelo no coinciden con las del DataFrame

**Solución**: Verifica que `create_features()` genere exactamente las mismas columnas que usaste en el entrenamiento

### "FileNotFoundError: models/mi_modelo.pkl"
**Causa**: Ruta incorrecta en `config.py` o archivo no exportado

**Solución**: Verifica que el archivo existe y la ruta en `config.py` es correcta

### Predicciones siempre iguales
**Causa**: Modelo no está aprendiendo o datos mal preparados

**Solución**: Revisa el entrenamiento, verifica que no haya data leakage

### El bot no compra nunca
**Causa**: Umbral de probabilidad muy alto o modelo muy conservador

**Solución**: Ajusta `umbral_config[2]` a un valor más bajo (ej: 0.4 en lugar de 0.7)

---

## 📊 Monitoreo del Modelo

Después de conectar un nuevo modelo, monitorea:

1. **Tasa de predicciones positivas**: ¿Cuántas veces predice comprar?
2. **Distribución de probabilidades**: ¿Están balanceadas o muy sesgadas?
3. **Rendimiento real vs backtesting**: ¿Coinciden los resultados?
4. **Drift del modelo**: ¿El rendimiento se degrada con el tiempo?

Considera reentrenar el modelo cada 3-6 meses con datos frescos.

---

## 🎓 Recursos

- Ver `notebooks/README.md` para más detalles sobre desarrollo de modelos
- Ver `README.md` para arquitectura general del sistema
- Ver `deployment/CLOUD_DEPLOYMENT.md` para deployment en producción
