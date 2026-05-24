# 📑 Índice de Documentación - Delfos Trading Bot

## 🎯 Empezar Aquí

### Para Usuarios Nuevos
1. **[QUICKSTART.md](QUICKSTART.md)** - Configuración en 5 minutos
2. **[ESTRUCTURA.txt](ESTRUCTURA.txt)** - Visualización completa del proyecto
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Resumen ejecutivo

### Para Deployment
1. **[deployment/CLOUD_DEPLOYMENT.md](deployment/CLOUD_DEPLOYMENT.md)** - Guías para Railway, AWS, GCP, Azure, etc.
2. **[deployment/.env.example](deployment/.env.example)** - Plantilla de credenciales

### Para Desarrollo de Modelos
1. **[notebooks/README.md](notebooks/README.md)** - Guía de uso de notebooks
2. **[HOW_TO_CONNECT_NEW_MODEL.md](HOW_TO_CONNECT_NEW_MODEL.md)** - Conectar modelos al pipeline
3. **[notebooks/model_training.ipynb](notebooks/model_training.ipynb)** - Entrenar modelos
4. **[notebooks/model_evaluation.ipynb](notebooks/model_evaluation.ipynb)** - Evaluar modelos

---

## 📚 Documentación Completa

### Documentos Principales

| Archivo | Descripción | Cuándo Leer |
|---------|-------------|-------------|
| **[README.md](README.md)** | Documentación general del proyecto | Primero |
| **[QUICKSTART.md](QUICKSTART.md)** | Guía de inicio rápido | Para empezar rápido |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Resumen ejecutivo completo | Para entender el proyecto |
| **[ESTRUCTURA.txt](ESTRUCTURA.txt)** | Estructura visual del proyecto | Para navegar el código |
| **[HOW_TO_CONNECT_NEW_MODEL.md](HOW_TO_CONNECT_NEW_MODEL.md)** | Conectar modelos ML al pipeline | Al desarrollar modelos |

### Documentación Técnica

| Archivo | Descripción |
|---------|-------------|
| **[pipeline/config.py](pipeline/config.py)** | Configuración del sistema |
| **[pipeline/bot.py](pipeline/bot.py)** | Bot principal de trading |
| **[pipeline/predictor.py](pipeline/predictor.py)** | Módulo de predicción ML |

### Deployment

| Archivo | Descripción |
|---------|-------------|
| **[deployment/CLOUD_DEPLOYMENT.md](deployment/CLOUD_DEPLOYMENT.md)** | Guías de deployment en clouds |
| **[deployment/Dockerfile](deployment/Dockerfile)** | Imagen Docker |
| **[deployment/docker-compose.yml](deployment/docker-compose.yml)** | Orquestación Docker |
| **[deployment/.env.example](deployment/.env.example)** | Plantilla de credenciales |

### Desarrollo de Modelos

| Archivo | Descripción |
|---------|-------------|
| **[notebooks/README.md](notebooks/README.md)** | Guía de notebooks |
| **[notebooks/model_training.ipynb](notebooks/model_training.ipynb)** | Entrenar modelos |
| **[notebooks/model_evaluation.ipynb](notebooks/model_evaluation.ipynb)** | Evaluar modelos |

### Scripts de Utilidad

| Script | Descripción |
|--------|-------------|
| **[scripts/setup.py](scripts/setup.py)** | Setup inicial del proyecto |
| **[scripts/copy_models.py](scripts/copy_models.py)** | Copiar modelos desde carpeta original |
| **[scripts/test_prediction.py](scripts/test_prediction.py)** | Probar predicciones del modelo |

---

## 🗺️ Rutas de Aprendizaje

### Ruta 1: Usuario que quiere ejecutar el bot YA
```
1. QUICKSTART.md
2. Configurar deployment/.env
3. python scripts/setup.py
4. cd pipeline && python bot.py
```

### Ruta 2: Usuario que quiere desplegar en la nube
```
1. QUICKSTART.md
2. deployment/CLOUD_DEPLOYMENT.md
3. Elegir plataforma (Railway recomendado)
4. Seguir guía específica de la plataforma
```

### Ruta 3: Desarrollador que quiere crear nuevos modelos
```
1. notebooks/README.md
2. notebooks/model_training.ipynb
3. HOW_TO_CONNECT_NEW_MODEL.md
4. notebooks/model_evaluation.ipynb
```

### Ruta 4: Usuario que quiere entender todo el proyecto
```
1. PROJECT_SUMMARY.md
2. ESTRUCTURA.txt
3. README.md
4. Explorar código en pipeline/
```

---

## 🔍 Búsqueda Rápida

### ¿Cómo...?

**¿Cómo empezar rápidamente?**
→ [QUICKSTART.md](QUICKSTART.md)

**¿Cómo configurar credenciales de Binance?**
→ [QUICKSTART.md](QUICKSTART.md) - Sección 2

**¿Cómo desplegar en Railway?**
→ [deployment/CLOUD_DEPLOYMENT.md](deployment/CLOUD_DEPLOYMENT.md) - Sección 1

**¿Cómo desplegar en AWS?**
→ [deployment/CLOUD_DEPLOYMENT.md](deployment/CLOUD_DEPLOYMENT.md) - Sección 3

**¿Cómo entrenar un nuevo modelo?**
→ [notebooks/model_training.ipynb](notebooks/model_training.ipynb)

**¿Cómo conectar un modelo al pipeline?**
→ [HOW_TO_CONNECT_NEW_MODEL.md](HOW_TO_CONNECT_NEW_MODEL.md)

**¿Cómo hacer backtesting?**
→ [notebooks/model_evaluation.ipynb](notebooks/model_evaluation.ipynb)

**¿Cómo cambiar el símbolo de trading (ej: de SOL a BTC)?**
→ [pipeline/config.py](pipeline/config.py) - TRADING_CONFIG

**¿Cómo cambiar los parámetros del modelo?**
→ [pipeline/config.py](pipeline/config.py) - MODEL_CONFIG

**¿Cómo ver los logs del bot?**
→ `pipeline/logs/trading.log`

**¿Cómo probar que todo funciona sin ejecutar el bot completo?**
→ `python scripts/test_prediction.py`

---

## 📂 Estructura de Archivos

```
delfos-production/
│
├── 📄 Documentación
│   ├── README.md                          ← Inicio
│   ├── INDEX.md                           ← Este archivo
│   ├── QUICKSTART.md                      ← Inicio rápido
│   ├── PROJECT_SUMMARY.md                 ← Resumen
│   ├── ESTRUCTURA.txt                     ← Estructura visual
│   └── HOW_TO_CONNECT_NEW_MODEL.md        ← Conectar modelos
│
├── 📂 pipeline/                           ← Código de producción
│   ├── bot.py
│   ├── predictor.py
│   ├── config.py
│   ├── models/
│   └── logs/
│
├── 📂 notebooks/                          ← Desarrollo de modelos
│   ├── model_training.ipynb
│   ├── model_evaluation.ipynb
│   └── README.md
│
├── 📂 deployment/                         ← Configuración cloud
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── CLOUD_DEPLOYMENT.md
│
└── 📂 scripts/                            ← Utilidades
    ├── setup.py
    ├── copy_models.py
    └── test_prediction.py
```

---

## ⚡ Comandos Más Usados

```bash
# Setup inicial
python scripts/setup.py

# Probar predicción
python scripts/test_prediction.py

# Ejecutar bot
cd pipeline
python bot.py

# Iniciar Jupyter
cd notebooks
jupyter notebook

# Docker
cd deployment
docker-compose up -d
docker-compose logs -f trading-bot
```

---

## 🆘 Ayuda

Si tienes problemas:

1. **Revisa los logs**: `pipeline/logs/trading.log`
2. **Ejecuta el test**: `python scripts/test_prediction.py`
3. **Verifica credenciales**: `deployment/.env`
4. **Consulta la documentación** relevante arriba

---

## 📞 Contacto y Recursos

- **Binance API**: https://binance-docs.github.io/apidocs/
- **Scikit-learn**: https://scikit-learn.org/
- **Docker**: https://docs.docker.com/

---

**Última actualización**: Mayo 2026
