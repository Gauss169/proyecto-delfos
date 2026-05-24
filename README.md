# 🚀 Delfos Trading Bot - Production Pipeline

Sistema de trading automatizado 24/7 con Machine Learning para criptomonedas.

> **✅ PROYECTO LISTO PARA USAR** - Pipeline completo de producción con gestión segura de credenciales, desarrollo de modelos ML y deployment en múltiples clouds.

## 📁 Estructura del Proyecto

```
delfos-production/
├── pipeline/              # Pipeline de trading en producción
│   ├── bot.py            # Bot principal de trading
│   ├── predictor.py      # Módulo de predicción ML
│   ├── config.py         # Configuración del sistema
│   └── models/           # Modelos ML entrenados
├── notebooks/            # Desarrollo de nuevos modelos
│   ├── model_training.ipynb
│   └── model_evaluation.ipynb
├── deployment/           # Configuración para la nube
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env.example
├── requirements.txt      # Dependencias Python
└── README.md            # Este archivo
```

## 🚀 Inicio Rápido

### 1. Configuración Local

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar credenciales
cp deployment/.env.example deployment/.env
# Editar deployment/.env con tus credenciales de Binance
```

### 2. Ejecutar Bot Localmente

```bash
cd pipeline
python bot.py
```

### 3. Deployment en la Nube (Docker)

```bash
cd deployment
docker-compose up -d
```

## 🔐 Gestión Segura de Credenciales

**NUNCA** subas el archivo `.env` a Git. Las credenciales se gestionan mediante:

1. **Variables de entorno**: El bot lee credenciales desde variables de entorno
2. **Archivo .env**: Solo para desarrollo local (excluido en .gitignore)
3. **Secrets en la nube**: Usar servicios como AWS Secrets Manager, Azure Key Vault, o variables de entorno en el servicio cloud

### Configurar en AWS/Azure/GCP:

- **AWS**: Usar AWS Secrets Manager o variables de entorno en ECS/Lambda
- **Azure**: Usar Azure Key Vault o App Service Configuration
- **GCP**: Usar Secret Manager o Cloud Run environment variables
- **Railway/Render**: Variables de entorno en el dashboard

## 🤖 Desarrollo de Nuevos Modelos

### Entrenar un Nuevo Modelo

1. Abre `notebooks/model_training.ipynb`
2. Desarrolla y entrena tu modelo
3. Exporta el modelo entrenado:

```python
import pickle

# Guardar modelo
with open("../pipeline/models/nuevo_modelo.pkl", "wb") as f:
    pickle.dump(modelo, f)

# Guardar columnas
with open("../pipeline/models/nuevo_modelo_columns.pkl", "wb") as f:
    pickle.dump(columnas, f)

# Guardar umbrales
with open("../pipeline/models/nuevo_modelo_umbral.pkl", "wb") as f:
    pickle.dump(umbral, f)
```

### Conectar Modelo al Pipeline

Edita `pipeline/config.py`:

```python
MODEL_CONFIG = {
    'model_path': 'models/nuevo_modelo.pkl',
    'columns_path': 'models/nuevo_modelo_columns.pkl',
    'threshold_path': 'models/nuevo_modelo_umbral.pkl'
}
```

El pipeline cargará automáticamente el nuevo modelo.

## 📊 Monitoreo

El bot genera logs en tiempo real. Para monitorear:

```bash
# Ver logs en Docker
docker-compose logs -f trading-bot

# Ver logs locales
tail -f pipeline/logs/trading.log
```

## ⚙️ Configuración Avanzada

Edita `pipeline/config.py` para ajustar:

- Símbolo de trading (por defecto: SOLUSDC)
- Hora de ejecución diaria
- Intervalo de verificación
- Parámetros de stop-loss
- Configuración del modelo ML

## 🛡️ Seguridad

- ✅ Credenciales en variables de entorno
- ✅ `.env` excluido de Git
- ✅ Uso de `.env.example` como plantilla
- ✅ Sin credenciales hardcodeadas en el código

## 📝 Notas Importantes

- El bot ejecuta operaciones reales con dinero real
- Prueba primero en testnet de Binance
- Monitorea regularmente el rendimiento
- Mantén backups de tus modelos entrenados
