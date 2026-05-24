import sys
import os

pipeline_dir = os.path.join(os.path.dirname(__file__), '..', 'pipeline')
sys.path.insert(0, pipeline_dir)
os.chdir(pipeline_dir)

from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET, TRADING_CONFIG
from predictor import predict

def test_prediction():
    print("🧪 Probando predicción del modelo...")
    print()
    
    try:
        client = Client(BINANCE_API_KEY, BINANCE_SECRET)
        
        symbol = TRADING_CONFIG['symbol']
        print(f"📊 Símbolo: {symbol}")
        print()
        
        print("⏳ Obteniendo datos históricos y generando predicción...")
        pred, pred_bool, openday, virtual_close = predict(client, symbol)
        
        print()
        print("=" * 60)
        print("✅ RESULTADOS DE LA PREDICCIÓN")
        print("=" * 60)
        print()
        print(f"Probabilidad de compra: {pred:.4f} ({pred*100:.2f}%)")
        print(f"Decisión: {'🟢 COMPRAR' if pred_bool else '🔴 NO COMPRAR'}")
        print(f"Precio de apertura estimado: ${openday:.4f}")
        print(f"Precio objetivo (virtual close): ${virtual_close:.4f}")
        print()
        
        if pred_bool:
            print("💡 El modelo recomienda COMPRAR en la próxima ejecución")
            print(f"   Se creará una orden de venta a ~${virtual_close:.4f}")
        else:
            print("💡 El modelo NO recomienda comprar en este momento")
        
        print()
        print("=" * 60)
        
        current_price = client.get_symbol_ticker(symbol=symbol)['price']
        print(f"📈 Precio actual de mercado: ${float(current_price):.4f}")
        print("=" * 60)
        
    except Exception as e:
        print()
        print("❌ ERROR al generar predicción:")
        print(f"   {type(e).__name__}: {e}")
        print()
        print("Posibles causas:")
        print("  - Credenciales de Binance incorrectas")
        print("  - Modelos ML no encontrados en pipeline/models/")
        print("  - Problema de conexión a internet")
        print("  - Configuración incorrecta en config.py")
        return False
    
    return True

if __name__ == "__main__":
    success = test_prediction()
    sys.exit(0 if success else 1)
