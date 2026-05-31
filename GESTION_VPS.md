# 🖥️ Guía de Gestión del VPS - Delfos Trading Bot

Esta guía explica cómo gestionar el bot de trading en tu VPS de Contabo.

---

## 📡 Conectarse al VPS

### Desde Windows (PowerShell):

```powershell
ssh root@37.60.240.107
```

Te pedirá la contraseña del VPS. Escríbela y presiona Enter.

---

## ▶️ Iniciar el Bot

### Si el bot está detenido:

```bash
systemctl start delfos-bot
```

### Verificar que inició correctamente:

```bash
systemctl status delfos-bot
```

Deberías ver: **"Active: active (running)"** ✅

---

## ⏸️ Detener el Bot

### Para detener el bot temporalmente:

```bash
systemctl stop delfos-bot
```

### Verificar que se detuvo:

```bash
systemctl status delfos-bot
```

Deberías ver: **"Active: inactive (dead)"** ⏹️

---

## 🔄 Reiniciar el Bot

### Si el bot tiene problemas o actualizaste el código:

```bash
systemctl restart delfos-bot
```

Esto detiene y vuelve a iniciar el bot automáticamente.

---

## 🔍 Verificar si el Bot Está Funcionando

### Ver estado del servicio:

```bash
systemctl status delfos-bot
```

### Ver logs en tiempo real:

```bash
tail -f /root/proyecto-delfos/pipeline/logs/bot.log
```

Para salir de los logs: **Ctrl + C**

### Ver últimas 100 líneas de logs:

```bash
tail -n 100 /root/proyecto-delfos/pipeline/logs/bot.log
```

### Ver si el proceso está corriendo:

```bash
ps aux | grep bot.py
```

---

## 🚫 Deshabilitar Inicio Automático

### Si NO quieres que el bot inicie automáticamente al reiniciar el VPS:

```bash
systemctl disable delfos-bot
```

### Para volver a habilitar el inicio automático:

```bash
systemctl enable delfos-bot
```

---

## 🔄 Actualizar el Código del Bot

### Si hiciste cambios en GitHub y quieres actualizar el VPS:

```bash
# 1. Detener el bot
systemctl stop delfos-bot

# 2. Ir a la carpeta del proyecto
cd /root/proyecto-delfos

# 3. Descargar cambios de GitHub
git pull

# 4. Reiniciar el bot
systemctl start delfos-bot

# 5. Verificar que funciona
systemctl status delfos-bot
```

---

## 📊 Ver Logs y Errores

### Logs del bot (archivo):

```bash
# Ver todo el log
cat /root/proyecto-delfos/pipeline/logs/bot.log

# Ver últimas 50 líneas
tail -n 50 /root/proyecto-delfos/pipeline/logs/bot.log

# Ver en tiempo real
tail -f /root/proyecto-delfos/pipeline/logs/bot.log
```

### Logs del sistema (systemd):

```bash
# Ver últimos 50 mensajes
journalctl -u delfos-bot -n 50

# Ver en tiempo real
journalctl -u delfos-bot -f

# Ver errores
journalctl -u delfos-bot -p err
```

---

## 🔧 Cambiar Configuración del Bot

### Modificar parámetros de trading:

```bash
nano /root/proyecto-delfos/pipeline/config.py
```

Edita los valores que necesites:
- `symbol`: Par de trading (ej: 'SOLUSDC')
- `target_time`: Hora de ejecución (ej: '14:00')
- `stop_loss_threshold`: Umbral de stop loss (ej: 0.9)
- `take_profit_threshold`: Umbral de take profit (ej: 1.02)

Guardar: **Ctrl + O**, **Enter**, **Ctrl + X**

Luego reinicia el bot:

```bash
systemctl restart delfos-bot
```

---

## 🔐 Cambiar Credenciales de Binance

### Si necesitas actualizar tus API keys:

```bash
nano /root/proyecto-delfos/pipeline/.env
```

Edita:
```
BINANCE_API_KEY=nueva_api_key
BINANCE_SECRET=nuevo_secret
```

Guardar: **Ctrl + O**, **Enter**, **Ctrl + X**

Reiniciar el bot:

```bash
systemctl restart delfos-bot
```

---

## 🗑️ Eliminar el Bot Completamente

### Si quieres desinstalar todo:

```bash
# 1. Detener y deshabilitar el servicio
systemctl stop delfos-bot
systemctl disable delfos-bot

# 2. Eliminar el servicio
rm /etc/systemd/system/delfos-bot.service
systemctl daemon-reload

# 3. Eliminar el código
rm -rf /root/proyecto-delfos
```

---

## 🔌 Desconectarse del VPS

### Cuando termines de trabajar:

```bash
exit
```

Esto te desconectará del VPS. El bot seguirá corriendo en segundo plano.

---

## 📋 Resumen de Comandos Principales

| Acción | Comando |
|--------|---------|
| **Conectar al VPS** | `ssh root@37.60.240.107` |
| **Iniciar bot** | `systemctl start delfos-bot` |
| **Detener bot** | `systemctl stop delfos-bot` |
| **Reiniciar bot** | `systemctl restart delfos-bot` |
| **Ver estado** | `systemctl status delfos-bot` |
| **Ver logs en vivo** | `tail -f /root/proyecto-delfos/pipeline/logs/bot.log` |
| **Actualizar código** | `cd /root/proyecto-delfos && git pull && systemctl restart delfos-bot` |
| **Desconectar** | `exit` |

---

## ⚠️ Notas Importantes

1. **El bot corre 24/7** - No necesitas estar conectado al VPS para que funcione
2. **Inicio automático** - El bot se reiniciará automáticamente si el VPS se reinicia
3. **Logs** - Revisa los logs regularmente para detectar problemas
4. **Actualizaciones** - Siempre detén el bot antes de actualizar el código
5. **Credenciales** - Nunca compartas tus credenciales de Binance o del VPS

---

## 🆘 Solución de Problemas

### El bot no inicia:

```bash
# Ver errores detallados
journalctl -u delfos-bot -n 100

# Verificar que existen los archivos
ls -la /root/proyecto-delfos/pipeline/

# Verificar credenciales
cat /root/proyecto-delfos/pipeline/.env
```

### El bot se detiene solo:

```bash
# Ver por qué se detuvo
journalctl -u delfos-bot -n 50

# Revisar logs del bot
tail -n 100 /root/proyecto-delfos/pipeline/logs/bot.log
```

### Error de conexión a Binance:

- Verifica que las credenciales en `.env` son correctas
- Verifica que la IP del VPS no está bloqueada por Binance
- Revisa los logs para ver el error específico

---

## 💰 Gestión del VPS de Contabo

### Ver uso de recursos:

```bash
# Uso de CPU y memoria
htop

# Espacio en disco
df -h

# Procesos corriendo
ps aux
```

### Apagar el VPS (⚠️ Cuidado):

```bash
# Esto apagará el VPS completamente
shutdown -h now
```

### Reiniciar el VPS:

```bash
# Esto reiniciará el VPS (el bot se iniciará automáticamente)
reboot
```

---

**Última actualización:** Mayo 2026
