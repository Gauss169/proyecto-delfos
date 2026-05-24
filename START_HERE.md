# 👋 ¡EMPIEZA AQUÍ!

## 🎉 ¡Bienvenido a Delfos Trading Bot!

Tu pipeline de trading automatizado está **completamente configurado** y listo para usar.

---

## ⚡ Inicio Ultra-Rápido (3 pasos)

### 1️⃣ Configurar Credenciales (2 minutos)

Edita el archivo `deployment/.env`:

```bash
# Windows
notepad deployment\.env

# Linux/Mac
nano deployment/.env
```

Añade tus credenciales de Binance:
```
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET=tu_secret_key_aqui
```

⚠️ **IMPORTANTE**: Usa API keys con permisos **solo de trading** (no withdrawal)

### 2️⃣ Instalar Dependencias (1 minuto)

```bash
pip install -r requirements.txt
```

### 3️⃣ Ejecutar el Bot (1 segundo)

```bash
cd pipeline
python bot.py
```

✅ **¡Listo!** El bot está corriendo 24/7

---

## 📋 ¿Qué Puedes Hacer Ahora?

### Opción A: Ejecutar Localmente
```bash
cd pipeline
python bot.py
```
El bot ejecutará operaciones según las predicciones del modelo ML.

### Opción B: Desplegar en la Nube (Recomendado)
```bash
# Ver guía completa
cat deployment/CLOUD_DEPLOYMENT.md
```
**Más fácil**: Railway (5 minutos, $5/mes)

### Opción C: Desarrollar Nuevos Modelos
```bash
cd notebooks
jupyter notebook
# Abrir model_training.ipynb
```

---

## 📚 Documentación Disponible

| Archivo | ¿Para Qué? |
|---------|------------|
| **[INDEX.md](INDEX.md)** | 📑 Índice de toda la documentación |
| **[QUICKSTART.md](QUICKSTART.md)** | ⚡ Guía rápida de 5 minutos |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | 📊 Resumen completo del proyecto |
| **[ESTRUCTURA.txt](ESTRUCTURA.txt)** | 🗂️ Estructura visual del proyecto |
| **[HOW_TO_CONNECT_NEW_MODEL.md](HOW_TO_CONNECT_NEW_MODEL.md)** | 🔌 Conectar modelos ML |
| **[deployment/CLOUD_DEPLOYMENT.md](deployment/CLOUD_DEPLOYMENT.md)** | ☁️ Desplegar en la nube |

---

## 🧪 Probar que Todo Funciona

Antes de ejecutar el bot completo, prueba que todo esté bien:

```bash
# Verificar setup
python scripts/setup.py

# Probar predicción
python scripts/test_prediction.py
```

Si ves algo como esto, ¡todo está bien! ✅
```
✅ RESULTADOS DE LA PREDICCIÓN
Probabilidad de compra: 0.3245 (32.45%)
Decisión: 🔴 NO COMPRAR
```

---

## 🗺️ Rutas Sugeridas

### 🚀 Quiero ejecutar el bot YA
1. Configurar `deployment/.env` con credenciales
2. `pip install -r requirements.txt`
3. `cd pipeline && python bot.py`

### ☁️ Quiero desplegarlo en la nube
1. Leer `deployment/CLOUD_DEPLOYMENT.md`
2. Elegir plataforma (Railway recomendado)
3. Seguir instrucciones específicas

### 🧪 Quiero desarrollar mis propios modelos
1. Leer `notebooks/README.md`
2. Abrir `notebooks/model_training.ipynb`
3. Entrenar modelo
4. Seguir `HOW_TO_CONNECT_NEW_MODEL.md`

### 📖 Quiero entender todo el proyecto
1. Leer `PROJECT_SUMMARY.md`
2. Ver `ESTRUCTURA.txt`
3. Explorar código en `pipeline/`

---

## ✅ Checklist Pre-Ejecución

Antes de ejecutar con dinero real:

- [ ] Credenciales configuradas en `deployment/.env`
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Test de predicción exitoso (`python scripts/test_prediction.py`)
- [ ] API keys con permisos limitados (solo trading)
- [ ] Entiendes cómo funciona el bot (lee `README.md`)
- [ ] Has hecho backtesting del modelo (opcional pero recomendado)
- [ ] Defines límites de riesgo (cuánto estás dispuesto a perder)

---

## 🎯 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    BINANCE API                          │
│              (Datos + Ejecución de Órdenes)             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  PIPELINE (bot.py)                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. Obtener datos históricos                    │   │
│  │  2. Generar predicción con ML (predictor.py)    │   │
│  │  3. Decidir: ¿Comprar o No?                     │   │
│  │  4. Ejecutar orden si es favorable              │   │
│  │  5. Monitorear stop-loss                        │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MODELO ML (models/*.pkl)                   │
│  • Gradient Boosting Classifier                        │
│  • Entrenado con datos históricos                      │
│  • Predice probabilidad de operación exitosa           │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 Seguridad

✅ **Credenciales protegidas** con variables de entorno  
✅ **`.env` excluido de Git** (no se subirá accidentalmente)  
✅ **Sin hardcoding** de API keys en el código  
✅ **Compatible con servicios cloud** de secretos  

⚠️ **NUNCA** compartas tu archivo `.env`  
⚠️ **NUNCA** subas credenciales a GitHub  
⚠️ **SIEMPRE** usa API keys con permisos limitados  

---

## 💡 Tips Importantes

### Para Principiantes
- Empieza con cantidades pequeñas
- Monitorea el bot regularmente los primeros días
- Entiende qué hace cada operación (revisa los logs)
- Considera usar Binance Testnet primero

### Para Avanzados
- Desarrolla tus propios modelos ML en `notebooks/`
- Optimiza los umbrales de decisión
- Implementa estrategias más complejas
- Usa ensemble de múltiples modelos

---

## 📊 Monitoreo

### Ver Logs en Tiempo Real
```bash
# Windows
Get-Content pipeline\logs\trading.log -Wait

# Linux/Mac
tail -f pipeline/logs/trading.log
```

### Logs Típicos
```
2024-05-24 14:00:00 - INFO - ⏰ Trigger activado - Ejecutando predicción
2024-05-24 14:00:05 - INFO - 📊 Predicción: 0.3245 | Decisión: NO COMPRAR
2024-05-24 14:00:05 - INFO - 💡 El modelo NO recomienda comprar en este momento
```

---

## 🆘 Problemas Comunes

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "FileNotFoundError: models/gb_low_model.pkl"
```bash
python scripts/copy_models.py
```

### "No se obtuvieron datos históricos"
- Verifica credenciales en `deployment/.env`
- Comprueba conexión a internet
- Asegúrate de que el símbolo existe (ej: SOLUSDC)

### El bot no ejecuta operaciones
- Verifica la hora objetivo en `pipeline/config.py`
- Revisa los logs para ver predicciones
- Comprueba que tengas saldo en Binance

---

## 🚀 Próximos Pasos

1. **Ahora**: Configura credenciales y prueba localmente
2. **Hoy**: Despliega en Railway para ejecución 24/7
3. **Esta semana**: Monitorea rendimiento y ajusta parámetros
4. **Este mes**: Desarrolla tu propio modelo ML mejorado

---

## 📞 Recursos

- **Documentación completa**: Ver [INDEX.md](INDEX.md)
- **Binance API Docs**: https://binance-docs.github.io/apidocs/
- **Scikit-learn**: https://scikit-learn.org/

---

## ⚠️ Disclaimer

Este bot opera con **dinero real**. Úsalo bajo tu propio riesgo. El rendimiento pasado no garantiza rendimiento futuro. Siempre prueba exhaustivamente antes de usar en producción.

---

## 🎉 ¡Listo!

Tu proyecto está completamente configurado. Solo necesitas:
1. Configurar credenciales en `deployment/.env`
2. Ejecutar `cd pipeline && python bot.py`

**¡Buena suerte con tu trading automatizado! 🚀📈**

---

**¿Tienes dudas?** Consulta [INDEX.md](INDEX.md) para encontrar la documentación que necesitas.
