# 🚀 Guía de Inicio Rápido

## Configuración en 5 Minutos

### 1. Instalar Dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Credenciales

```bash
# Editar el archivo .env
notepad deployment\.env  # Windows
nano deployment/.env     # Linux/Mac
```

Añade tus credenciales de Binance:
```
BINANCE_API_KEY=tu_api_key_real
BINANCE_SECRET=tu_secret_key_real
```

**⚠️ IMPORTANTE**: 
- Usa API keys con permisos **solo de trading** (no withdrawal)
- Nunca compartas este archivo
- Está excluido de Git por seguridad

### 3. Verificar Setup

```bash
python scripts/setup.py
```

### 4. Probar Localmente

```bash
cd pipeline
python bot.py
```

El bot comenzará a ejecutarse y verás logs como:
```
2024-05-24 10:52:00 - INFO - 🚀 Iniciando bot de trading para SOLUSDC
2024-05-24 10:52:00 - INFO - ⏰ Hora objetivo: 14:00
```

### 5. Desplegar en la Nube

Consulta `deployment/CLOUD_DEPLOYMENT.md` para instrucciones detalladas.

**Opción más fácil (Railway)**:
1. Sube tu código a GitHub (repositorio privado)
2. Conecta Railway a tu repo
3. Añade variables de entorno en Railway
4. Deploy automático ✅

---

## 📊 Desarrollar Nuevos Modelos

```bash
# Iniciar Jupyter
cd notebooks
jupyter notebook

# Abrir model_training.ipynb
# Entrenar tu modelo
# Exportar a ../pipeline/models/
# Actualizar ../pipeline/config.py
```

---

## 🔧 Configuración Avanzada

Edita `pipeline/config.py` para personalizar:

```python
TRADING_CONFIG = {
    'symbol': 'SOLUSDC',           # Par de trading
    'target_time': '14:00',         # Hora de ejecución diaria
    'check_interval': 2,            # Segundos entre checks
    'stop_loss_threshold': 0.9,     # Stop loss al -10%
    'take_profit_threshold': 1.02,  # Take profit al +2%
}

MODEL_CONFIG = {
    'model_path': 'models/tu_modelo.pkl',  # Ruta a tu modelo
    # ... más configuración
}
```

---

## 📝 Checklist Pre-Producción

Antes de ejecutar con dinero real:

- [ ] Credenciales configuradas correctamente
- [ ] Modelos ML copiados a `pipeline/models/`
- [ ] Bot probado localmente sin errores
- [ ] Backtesting realizado con resultados positivos
- [ ] API keys con permisos limitados (solo trading)
- [ ] Monitoreo configurado (logs, alertas)
- [ ] Probado en Binance Testnet (opcional pero recomendado)
- [ ] Límites de riesgo definidos (max inversión, stop loss)

---

## ❓ Problemas Comunes

### "ModuleNotFoundError: No module named 'binance'"
```bash
pip install -r requirements.txt
```

### "No se obtuvieron datos históricos"
- Verifica tus credenciales de Binance
- Comprueba tu conexión a internet
- Asegúrate de que el símbolo existe (ej: SOLUSDC)

### "FileNotFoundError: models/gb_low_model.pkl"
```bash
python scripts/copy_models.py
```

### El bot no ejecuta operaciones
- Verifica que la hora objetivo esté configurada correctamente
- Revisa los logs para ver predicciones
- Comprueba que tengas saldo en tu cuenta de Binance

---

## 📞 Soporte

1. Revisa `README.md` para documentación completa
2. Consulta `deployment/CLOUD_DEPLOYMENT.md` para deployment
3. Lee `notebooks/README.md` para desarrollo de modelos
4. Verifica los logs en `pipeline/logs/trading.log`

---

## ⚠️ Disclaimer

Este bot opera con dinero real. Úsalo bajo tu propio riesgo. El rendimiento pasado no garantiza rendimiento futuro. Siempre prueba exhaustivamente antes de usar en producción.
