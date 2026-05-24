#!/bin/bash
# Script de instalación automática para VPS
# Ejecutar como root: bash vps_setup.sh

echo "🚀 Instalando Delfos Trading Bot en VPS..."

# 1. Actualizar sistema
echo "📦 Actualizando sistema..."
apt update && apt upgrade -y

# 2. Instalar dependencias
echo "🔧 Instalando Python y Git..."
apt install python3 python3-pip git -y

# 3. Instalar librerías Python
echo "📚 Instalando librerías Python..."
pip3 install python-binance python-dotenv pandas numpy scikit-learn

# 4. Clonar repositorio
echo "📥 Clonando repositorio..."
cd /root
git clone https://github.com/Gauss169/proyecto-delfos.git
cd proyecto-delfos

# 5. Crear directorio de logs
mkdir -p pipeline/logs

# 6. Configurar credenciales
echo ""
echo "⚠️  IMPORTANTE: Configura tus credenciales de Binance"
echo "Edita el archivo: nano deployment/.env"
echo ""
echo "Añade:"
echo "BINANCE_API_KEY=tu_api_key"
echo "BINANCE_SECRET=tu_secret_key"
echo ""
read -p "Presiona Enter cuando hayas configurado las credenciales..."

# 7. Copiar .env al lugar correcto
cp deployment/.env pipeline/.env

# 8. Crear script de inicio
cat > /root/start_bot.sh << 'EOF'
#!/bin/bash
cd /root/proyecto-delfos/pipeline
nohup python3 bot.py > logs/bot.log 2>&1 &
echo "Bot iniciado. Ver logs: tail -f /root/proyecto-delfos/pipeline/logs/bot.log"
EOF

chmod +x /root/start_bot.sh

# 9. Crear script de detención
cat > /root/stop_bot.sh << 'EOF'
#!/bin/bash
pkill -f bot.py
echo "Bot detenido"
EOF

chmod +x /root/stop_bot.sh

# 10. Crear servicio systemd para auto-inicio
cat > /etc/systemd/system/delfos-bot.service << EOF
[Unit]
Description=Delfos Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/proyecto-delfos/pipeline
ExecStart=/usr/bin/python3 /root/proyecto-delfos/pipeline/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 11. Habilitar servicio
systemctl daemon-reload
systemctl enable delfos-bot.service

echo ""
echo "✅ Instalación completada!"
echo ""
echo "📋 Comandos útiles:"
echo "  Iniciar bot:    systemctl start delfos-bot"
echo "  Detener bot:    systemctl stop delfos-bot"
echo "  Ver estado:     systemctl status delfos-bot"
echo "  Ver logs:       journalctl -u delfos-bot -f"
echo "  O usar:         tail -f /root/proyecto-delfos/pipeline/logs/bot.log"
echo ""
echo "🚀 Para iniciar el bot ahora: systemctl start delfos-bot"
