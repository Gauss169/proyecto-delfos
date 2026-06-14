# 🔄 Flujo de Trabajo - Subir Cambios y Actualizar VPS

Guía paso a paso para subir cambios del bot a GitHub y actualizar el VPS.

---

## 📋 Resumen del Flujo

```
[Windows/Local] → [GitHub] → [VPS]
     Modificar    →   Push   →  Pull + Restart
```

---

## 📝 Paso 1: Hacer Cambios en Windows

### 1.1 Modifica los archivos necesarios:

- `pipeline/bot.py` - Lógica del bot
- `pipeline/config.py` - Configuración (horario, símbolo, etc.)
- `pipeline/predictor.py` - Modelo de predicción

---

## 📤 Paso 2: Subir Cambios a GitHub

### 2.1 Verificar qué archivos cambiaron:

```bash
cd "c:\Users\emima\OneDrive\Escritorio\proyecto delfos - copia\delfos-production"
git status
```

Verás archivos modificados en rojo (untracked) o verde (modified).

### 2.2 Agregar archivos al commit:

```bash
# Agregar archivos específicos
git add pipeline/bot.py pipeline/config.py

# O agregar TODOS los cambios
git add .
```

### 2.3 Crear el commit:

```bash
git commit -m "Descripción de los cambios realizados"
```

Ejemplos de mensajes:
- `"Actualizar target_time a 19:30"`
- `"Agregar logs de predicción"`
- `"Fix: Corregir error de sintaxis en venta"`

### 2.4 Subir a GitHub:

```bash
git push origin main
```

✅ **Listo** - Los cambios están en GitHub.

---

## 🖥️ Paso 3: Actualizar el VPS

### 3.1 Conectar al VPS:

```bash
ssh root@37.60.240.107
```

### 3.2 Descargar cambios de GitHub:

```bash
cd /root/proyecto-delfos
git pull origin main
```

### 3.3 Reiniciar el bot:

```bash
systemctl restart delfos-bot
```

### 3.4 Verificar que funciona:

```bash
systemctl status delfos-bot
```

Deberías ver: **"Active: active (running)"** ✅

---

## ⚡ Comando Rápido (Todo en uno)

Después de hacer `git push` en Windows, en el VPS ejecuta:

```bash
cd /root/proyecto-delfos && git pull && systemctl restart delfos-bot && systemctl status delfos-bot
```

---

## 📊 Verificar Logs

### Ver que el bot arrancó correctamente:

```bash
tail -f /root/proyecto-delfos/pipeline/logs/bot.log
```

Para salir: **Ctrl + C**

---

## 🔄 Ejemplo Completo

### Ejemplo 1: Cambiar la hora de trading

**En Windows:**
```bash
# Editar config.py y cambiar target_time
git add pipeline/config.py
git commit -m "Cambiar hora de trading a 20:00"
git push origin main
```

**En VPS:**
```bash
ssh root@37.60.240.107
cd /root/proyecto-delfos && git pull && systemctl restart delfos-bot
```

---

### Ejemplo 2: Agregar nuevos logs

**En Windows:**
```bash
# Editar bot.py y agregar logger.info()
git add pipeline/bot.py
git commit -m "Agregar logs para depuración de predicciones"
git push origin main
```

**En VPS:**
```bash
ssh root@37.60.240.107
cd /root/proyecto-delfos && git pull && systemctl restart delfos-bot && tail -f pipeline/logs/bot.log
```

---

## ⚠️ Solución de Problemas

### Error: "Your local changes would be overwritten"

Si editaste archivos directamente en el VPS:

```bash
cd /root/proyecto-delfos
# Guardar cambios locales en stash
git stash

# Descargar cambios de GitHub
git pull

# Aplicar cambios locales (si son necesarios)
git stash pop
```

### Error: "Permission denied"

Si no puedes hacer push a GitHub, verifica:
- Estás en la carpeta correcta: `delfos-production`
- El repositorio remoto está configurado: `git remote -v`

---

## 📋 Checklist Rápido

Antes de cada actualización:

- [ ] Modifiqué los archivos necesarios en Windows
- [ ] Hice `git add` de los archivos cambiados
- [ ] Creé commit con mensaje descriptivo
- [ ] Hice `git push origin main`
- [ ] Me conecté al VPS vía SSH
- [ ] Ejecuté `git pull` en el VPS
- [ ] Reinicié el bot con `systemctl restart delfos-bot`
- [ ] Verifiqué que el bot está running con `systemctl status`

---

## 🔗 Comandos Rápidos

| Acción | Comando Windows | Comando VPS |
|--------|-----------------|-------------|
| **Ver cambios** | `git status` | `git status` |
| **Agregar** | `git add archivo.py` | - |
| **Commit** | `git commit -m "mensaje"` | - |
| **Push** | `git push origin main` | - |
| **Pull** | - | `git pull` |
| **Restart** | - | `systemctl restart delfos-bot` |
| **Ver logs** | - | `tail -f pipeline/logs/bot.log` |

---

**Nota:** Siempre mantén la carpeta `delfos-production` sincronizada. No edites directamente en el VPS sin subir cambios a GitHub primero.
