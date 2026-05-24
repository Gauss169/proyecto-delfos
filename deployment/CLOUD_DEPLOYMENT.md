# Guía de Deployment en la Nube

Esta guía te ayudará a desplegar el bot de trading en diferentes plataformas cloud de forma segura.

## 🔐 Principios de Seguridad

**NUNCA** incluyas tus credenciales de Binance directamente en el código o en archivos que suban a Git.

Todas las plataformas cloud permiten configurar **variables de entorno** de forma segura:
- Las credenciales se almacenan cifradas en el servicio cloud
- No aparecen en logs ni en el código fuente
- Puedes rotarlas sin modificar el código

---

## ☁️ Opciones de Deployment

### 1. Railway (Recomendado - Más Fácil)

**Ventajas**: Gratis para empezar, muy fácil de usar, deployment automático desde Git

**Pasos**:

1. **Crear cuenta en Railway**: https://railway.app/

2. **Crear nuevo proyecto**:
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta tu repositorio

3. **Configurar variables de entorno**:
   - En el dashboard del proyecto, ve a "Variables"
   - Añade:
     ```
     BINANCE_API_KEY=tu_api_key
     BINANCE_SECRET=tu_secret_key
     ```

4. **Configurar el servicio**:
   - Railway detectará automáticamente el Dockerfile
   - El bot se ejecutará 24/7

5. **Monitorear**:
   - Ve a "Logs" para ver la ejecución en tiempo real

**Costo**: ~$5/mes después del tier gratuito

---

### 2. Render

**Ventajas**: Tier gratuito generoso, fácil configuración

**Pasos**:

1. **Crear cuenta**: https://render.com/

2. **Crear nuevo Web Service**:
   - Click en "New +" → "Web Service"
   - Conecta tu repositorio de GitHub

3. **Configuración**:
   - **Name**: delfos-trading-bot
   - **Environment**: Docker
   - **Plan**: Free (o Starter para 24/7 garantizado)

4. **Variables de entorno**:
   - En "Environment", añade:
     ```
     BINANCE_API_KEY
     BINANCE_SECRET
     ```

5. **Deploy**: Click en "Create Web Service"

**Nota**: El tier gratuito puede tener pausas de inactividad. Para 24/7 real, usa el plan Starter ($7/mes)

---

### 3. AWS (Avanzado)

**Ventajas**: Máximo control, escalabilidad, servicios profesionales

#### Opción A: AWS ECS (Elastic Container Service)

**Pasos**:

1. **Crear repositorio ECR**:
   ```bash
   aws ecr create-repository --repository-name delfos-trading-bot
   ```

2. **Build y push de la imagen Docker**:
   ```bash
   cd deployment
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <tu-account-id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t delfos-trading-bot ..
   docker tag delfos-trading-bot:latest <tu-account-id>.dkr.ecr.us-east-1.amazonaws.com/delfos-trading-bot:latest
   docker push <tu-account-id>.dkr.ecr.us-east-1.amazonaws.com/delfos-trading-bot:latest
   ```

3. **Crear secretos en AWS Secrets Manager**:
   ```bash
   aws secretsmanager create-secret \
     --name delfos/binance/credentials \
     --secret-string '{"BINANCE_API_KEY":"tu_key","BINANCE_SECRET":"tu_secret"}'
   ```

4. **Crear Task Definition en ECS**:
   - Define el contenedor con la imagen de ECR
   - Configura las variables de entorno desde Secrets Manager

5. **Crear servicio ECS**:
   - Usa Fargate para serverless
   - Configura 1 tarea siempre corriendo

**Costo**: ~$15-30/mes (Fargate)

#### Opción B: AWS Lambda (Para ejecuciones programadas)

Si prefieres ejecutar el bot en horarios específicos en lugar de 24/7:

1. **Crear función Lambda**
2. **Usar imagen Docker** (hasta 10GB)
3. **Configurar EventBridge** para ejecutar a horas específicas
4. **Variables de entorno** desde Lambda configuration

**Costo**: Prácticamente gratis (tier gratuito muy generoso)

---

### 4. Google Cloud Run

**Ventajas**: Pago por uso, escalado automático, fácil deployment

**Pasos**:

1. **Instalar gcloud CLI**: https://cloud.google.com/sdk/docs/install

2. **Autenticarse**:
   ```bash
   gcloud auth login
   gcloud config set project tu-proyecto-id
   ```

3. **Build y deploy**:
   ```bash
   cd deployment
   gcloud run deploy delfos-trading-bot \
     --source .. \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars BINANCE_API_KEY=tu_key,BINANCE_SECRET=tu_secret
   ```

4. **Para secretos más seguros**, usa Secret Manager:
   ```bash
   echo -n "tu_api_key" | gcloud secrets create binance-api-key --data-file=-
   echo -n "tu_secret" | gcloud secrets create binance-secret --data-file=-
   ```

**Costo**: ~$5-10/mes

---

### 5. Azure Container Instances

**Ventajas**: Integración con ecosistema Microsoft, simple

**Pasos**:

1. **Crear Resource Group**:
   ```bash
   az group create --name delfos-rg --location eastus
   ```

2. **Crear Container Registry**:
   ```bash
   az acr create --resource-group delfos-rg --name delfosregistry --sku Basic
   ```

3. **Build y push**:
   ```bash
   cd deployment
   az acr build --registry delfosregistry --image delfos-trading-bot:latest ..
   ```

4. **Crear secretos en Key Vault**:
   ```bash
   az keyvault create --name delfos-vault --resource-group delfos-rg
   az keyvault secret set --vault-name delfos-vault --name binance-api-key --value "tu_key"
   az keyvault secret set --vault-name delfos-vault --name binance-secret --value "tu_secret"
   ```

5. **Deploy Container Instance**:
   ```bash
   az container create \
     --resource-group delfos-rg \
     --name delfos-bot \
     --image delfosregistry.azurecr.io/delfos-trading-bot:latest \
     --environment-variables BINANCE_API_KEY=@Microsoft.KeyVault(SecretUri=...) \
     --restart-policy Always
   ```

**Costo**: ~$10-20/mes

---

### 6. DigitalOcean App Platform

**Ventajas**: Muy simple, buen precio

**Pasos**:

1. **Crear cuenta**: https://www.digitalocean.com/

2. **Crear nueva App**:
   - Click en "Create" → "Apps"
   - Conecta tu repositorio GitHub

3. **Configurar**:
   - Selecciona Dockerfile
   - Añade variables de entorno en "Environment Variables"

4. **Deploy**

**Costo**: $5-12/mes

---

## 📊 Comparativa Rápida

| Plataforma | Dificultad | Costo/mes | Mejor para |
|------------|------------|-----------|------------|
| Railway | ⭐ Fácil | $5 | Principiantes |
| Render | ⭐ Fácil | $7 | Simplicidad |
| DigitalOcean | ⭐⭐ Media | $5-12 | Balance precio/facilidad |
| Google Cloud Run | ⭐⭐ Media | $5-10 | Pago por uso |
| AWS ECS | ⭐⭐⭐ Difícil | $15-30 | Producción seria |
| Azure | ⭐⭐⭐ Difícil | $10-20 | Ecosistema Microsoft |

---

## 🔍 Monitoreo y Logs

Todas las plataformas ofrecen:
- **Logs en tiempo real**: Ver qué está haciendo el bot
- **Métricas**: CPU, memoria, uptime
- **Alertas**: Notificaciones si el bot se cae

### Configurar Alertas

Recomendado configurar alertas para:
- Bot detenido inesperadamente
- Errores de API de Binance
- Uso excesivo de recursos

---

## 🛡️ Mejores Prácticas de Seguridad

1. **Nunca** hagas commit de archivos `.env` con credenciales
2. **Usa** siempre variables de entorno o servicios de secretos
3. **Rota** tus API keys periódicamente
4. **Limita** los permisos de las API keys de Binance (solo trading, no withdrawal)
5. **Habilita** IP whitelist en Binance si tu cloud provider tiene IPs estáticas
6. **Monitorea** las operaciones regularmente
7. **Haz backup** de tus modelos ML entrenados

---

## 🚀 Inicio Rápido (Railway - Recomendado)

```bash
# 1. Inicializar Git en tu proyecto
cd delfos-production
git init
git add .
git commit -m "Initial commit"

# 2. Crear repositorio en GitHub (privado)
# Ir a github.com y crear nuevo repositorio PRIVADO

# 3. Push a GitHub
git remote add origin https://github.com/tu-usuario/delfos-production.git
git push -u origin main

# 4. Ir a Railway.app
# - Conectar GitHub
# - Seleccionar el repositorio
# - Añadir variables de entorno
# - Deploy automático

# 5. Monitorear logs
# Ver en el dashboard de Railway
```

---

## ❓ Troubleshooting

### El bot no inicia
- Verifica que las variables de entorno estén configuradas
- Revisa los logs para ver errores específicos
- Asegúrate de que el Dockerfile esté en la ubicación correcta

### Errores de API de Binance
- Verifica que las credenciales sean correctas
- Comprueba que la API key tenga permisos de trading
- Revisa si hay restricciones de IP en Binance

### El contenedor se reinicia constantemente
- Revisa los logs para ver el error
- Verifica que los modelos ML estén en la carpeta correcta
- Comprueba que todas las dependencias estén en requirements.txt

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs del servicio cloud
2. Verifica la configuración de variables de entorno
3. Comprueba que los modelos ML estén correctamente copiados
4. Consulta la documentación específica de tu plataforma cloud
