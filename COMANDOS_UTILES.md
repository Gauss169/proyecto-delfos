# 🛠️ Comandos Útiles - Delfos Trading Bot

Referencia rápida de comandos más usados.

---

## 🚀 Setup Inicial

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar proyecto
python scripts/setup.py

# Copiar modelos ML
python scripts/copy_models.py
```

---

## 🧪 Testing y Verificación

```bash
# Probar predicción del modelo
python scripts/test_prediction.py

# Verificar que todo está configurado
python scripts/setup.py
```

---

## ▶️ Ejecutar el Bot

```bash
# Ejecutar localmente
cd pipeline
python bot.py

# Ejecutar en background (Linux/Mac)
cd pipeline
nohup python bot.py > ../logs/bot.log 2>&1 &

# Ejecutar en background (Windows PowerShell)
cd pipeline
Start-Process python -ArgumentList "bot.py" -WindowStyle Hidden
```

---

## 📊 Desarrollo de Modelos

```bash
# Iniciar Jupyter Notebook
cd notebooks
jupyter notebook

# Iniciar JupyterLab (alternativa moderna)
cd notebooks
jupyter lab

# Convertir notebook a script Python
jupyter nbconvert --to script model_training.ipynb
```

---

## 🐳 Docker

```bash
# Build de la imagen
cd deployment
docker build -t delfos-trading-bot -f Dockerfile ..

# Ejecutar contenedor
docker run -d \
  --name delfos-bot \
  --env-file .env \
  -v $(pwd)/../pipeline/logs:/app/pipeline/logs \
  delfos-trading-bot

# Ver logs
docker logs -f delfos-bot

# Detener contenedor
docker stop delfos-bot

# Eliminar contenedor
docker rm delfos-bot

# Docker Compose (recomendado)
cd deployment
docker-compose up -d          # Iniciar
docker-compose logs -f        # Ver logs
docker-compose down           # Detener
docker-compose restart        # Reiniciar
```

---

## 📝 Logs

```bash
# Ver logs en tiempo real (Linux/Mac)
tail -f pipeline/logs/trading.log

# Ver logs en tiempo real (Windows PowerShell)
Get-Content pipeline\logs\trading.log -Wait

# Ver últimas 100 líneas
tail -n 100 pipeline/logs/trading.log    # Linux/Mac
Get-Content pipeline\logs\trading.log -Tail 100  # Windows

# Buscar errores en logs
grep "ERROR" pipeline/logs/trading.log   # Linux/Mac
Select-String "ERROR" pipeline\logs\trading.log  # Windows
```

---

## 🔧 Git

```bash
# Inicializar repositorio
git init

# Añadir archivos
git add .

# Commit
git commit -m "Initial commit - Delfos Trading Bot v1.0"

# Conectar a GitHub (repositorio PRIVADO)
git remote add origin https://github.com/tu-usuario/delfos-production.git

# Push
git push -u origin main

# Ver estado
git status

# Ver historial
git log --oneline
```

---

## ☁️ Deployment - Railway

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Inicializar proyecto
railway init

# Añadir variables de entorno
railway variables set BINANCE_API_KEY=tu_key
railway variables set BINANCE_SECRET=tu_secret

# Deploy
railway up

# Ver logs
railway logs

# Abrir dashboard
railway open
```

---

## ☁️ Deployment - AWS ECR + ECS

```bash
# Login a ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build y tag
docker build -t delfos-trading-bot -f deployment/Dockerfile .
docker tag delfos-trading-bot:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/delfos-trading-bot:latest

# Push a ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/delfos-trading-bot:latest

# Crear secreto
aws secretsmanager create-secret \
  --name delfos/binance/credentials \
  --secret-string '{"BINANCE_API_KEY":"tu_key","BINANCE_SECRET":"tu_secret"}'
```

---

## ☁️ Deployment - Google Cloud Run

```bash
# Autenticar
gcloud auth login

# Configurar proyecto
gcloud config set project tu-proyecto-id

# Build y deploy
gcloud run deploy delfos-trading-bot \
  --source . \
  --region us-central1 \
  --set-env-vars BINANCE_API_KEY=tu_key,BINANCE_SECRET=tu_secret

# Ver logs
gcloud run logs read delfos-trading-bot --region us-central1
```

---

## 🔍 Monitoreo

```bash
# Ver procesos Python corriendo
ps aux | grep python              # Linux/Mac
Get-Process python                # Windows

# Ver uso de CPU/RAM
top                               # Linux/Mac
htop                              # Linux/Mac (mejor)
Get-Process python | Select-Object CPU,WorkingSet  # Windows

# Matar proceso del bot
pkill -f bot.py                   # Linux/Mac
Stop-Process -Name python         # Windows (cuidado, mata todos los Python)
```

---

## 📦 Gestión de Dependencias

```bash
# Instalar dependencia específica
pip install nombre-paquete

# Actualizar requirements.txt
pip freeze > requirements.txt

# Instalar desde requirements.txt
pip install -r requirements.txt

# Actualizar todas las dependencias (cuidado)
pip install --upgrade -r requirements.txt

# Ver paquetes instalados
pip list

# Ver paquetes desactualizados
pip list --outdated
```

---

## 🧹 Limpieza

```bash
# Limpiar archivos Python compilados
find . -type d -name "__pycache__" -exec rm -r {} +  # Linux/Mac
Get-ChildItem -Recurse -Filter "__pycache__" | Remove-Item -Recurse  # Windows

# Limpiar logs antiguos
rm pipeline/logs/*.log            # Linux/Mac
Remove-Item pipeline\logs\*.log   # Windows

# Limpiar notebooks checkpoints
find . -type d -name ".ipynb_checkpoints" -exec rm -r {} +  # Linux/Mac
```

---

## 🔐 Seguridad

```bash
# Verificar que .env no está en Git
git status --ignored

# Ver qué archivos están siendo trackeados
git ls-files

# Eliminar .env del historial si se subió por error (PELIGROSO)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch deployment/.env" \
  --prune-empty --tag-name-filter cat -- --all
```

---

## 📊 Análisis de Datos

```bash
# Abrir Python interactivo con pandas
python -c "import pandas as pd; import pickle; \
  with open('pipeline/models/gb_low_model.pkl', 'rb') as f: \
    model = pickle.load(f); \
  print(model)"

# Ver importancia de features
python -c "import pickle; \
  with open('pipeline/models/gb_low_model.pkl', 'rb') as f: \
    model = pickle.load(f); \
  print(model.feature_importances_)"
```

---

## 🆘 Troubleshooting

```bash
# Verificar versión de Python
python --version

# Verificar instalación de paquetes
python -c "import binance; import sklearn; import pandas; print('OK')"

# Verificar conexión a Binance
python -c "from binance.client import Client; \
  import os; from dotenv import load_dotenv; \
  load_dotenv('deployment/.env'); \
  client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_SECRET')); \
  print(client.get_server_time())"

# Reinstalar todo desde cero
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

---

## 💡 Tips Útiles

```bash
# Crear alias para comandos frecuentes (Linux/Mac - añadir a ~/.bashrc)
alias delfos-start='cd ~/delfos-production/pipeline && python bot.py'
alias delfos-logs='tail -f ~/delfos-production/pipeline/logs/trading.log'
alias delfos-test='cd ~/delfos-production && python scripts/test_prediction.py'

# Crear alias (Windows PowerShell - añadir a $PROFILE)
function delfos-start { cd C:\...\delfos-production\pipeline; python bot.py }
function delfos-logs { Get-Content C:\...\delfos-production\pipeline\logs\trading.log -Wait }
function delfos-test { cd C:\...\delfos-production; python scripts\test_prediction.py }
```

---

## 📱 Monitoreo Remoto

```bash
# SSH a servidor
ssh usuario@tu-servidor.com

# Ver logs remotos
ssh usuario@servidor "tail -f /path/to/delfos-production/pipeline/logs/trading.log"

# Ejecutar comando remoto
ssh usuario@servidor "cd /path/to/delfos-production && python scripts/test_prediction.py"

# Copiar logs desde servidor
scp usuario@servidor:/path/to/logs/trading.log ./local-logs/
```

---

## 🔄 Actualización del Bot

```bash
# Pull últimos cambios
git pull origin main

# Reinstalar dependencias si cambiaron
pip install -r requirements.txt

# Reiniciar bot (Docker)
cd deployment
docker-compose restart

# Reiniciar bot (local)
pkill -f bot.py && cd pipeline && python bot.py &  # Linux/Mac
```

---

## 📈 Backup

```bash
# Backup de modelos
tar -czf models-backup-$(date +%Y%m%d).tar.gz pipeline/models/

# Backup de logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz pipeline/logs/

# Backup completo
tar -czf delfos-backup-$(date +%Y%m%d).tar.gz \
  --exclude='venv' \
  --exclude='.git' \
  --exclude='__pycache__' \
  delfos-production/
```

---

**Tip**: Guarda este archivo como referencia rápida. Puedes buscar comandos con Ctrl+F.
