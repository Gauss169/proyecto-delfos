import os
import shutil
import sys

def setup_project():
    print("🚀 Configurando proyecto Delfos Trading Bot...")
    print()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    print("1️⃣ Creando directorios necesarios...")
    dirs_to_create = [
        os.path.join(base_dir, 'pipeline', 'logs'),
        os.path.join(base_dir, 'pipeline', 'models'),
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"   ✅ {dir_path}")
    
    print()
    print("2️⃣ Verificando archivo .env...")
    env_example = os.path.join(base_dir, 'deployment', '.env.example')
    env_file = os.path.join(base_dir, 'deployment', '.env')
    
    if not os.path.exists(env_file):
        print("   ⚠️  No existe archivo .env")
        print(f"   📝 Copiando {env_example} a {env_file}")
        shutil.copy(env_example, env_file)
        print()
        print("   ⚠️  IMPORTANTE: Edita deployment/.env con tus credenciales de Binance")
        print("   No olvides añadir:")
        print("      - BINANCE_API_KEY")
        print("      - BINANCE_SECRET")
    else:
        print("   ✅ Archivo .env encontrado")
    
    print()
    print("3️⃣ Verificando modelos ML...")
    models_dir = os.path.join(base_dir, 'pipeline', 'models')
    required_models = [
        'gb_low_model.pkl',
        'gb_low_columns.pkl',
        'umbral_gb_low_columns.pkl'
    ]
    
    all_models_present = True
    for model_file in required_models:
        model_path = os.path.join(models_dir, model_file)
        if os.path.exists(model_path):
            print(f"   ✅ {model_file}")
        else:
            print(f"   ❌ {model_file} - NO ENCONTRADO")
            all_models_present = False
    
    if not all_models_present:
        print()
        print("   ⚠️  Algunos modelos no están presentes.")
        print("   Ejecuta: python scripts/copy_models.py")
        print("   O entrena nuevos modelos en notebooks/model_training.ipynb")
    
    print()
    print("4️⃣ Verificando dependencias...")
    try:
        import pandas
        import numpy
        import sklearn
        from binance.client import Client
        print("   ✅ Todas las dependencias principales instaladas")
    except ImportError as e:
        print(f"   ❌ Falta dependencia: {e}")
        print("   Ejecuta: pip install -r requirements.txt")
    
    print()
    print("=" * 60)
    print("✅ Setup completado!")
    print()
    print("📋 Próximos pasos:")
    print()
    print("1. Editar deployment/.env con tus credenciales de Binance")
    print("2. Verificar que los modelos ML estén en pipeline/models/")
    print("3. Probar el bot localmente:")
    print("   cd pipeline")
    print("   python bot.py")
    print()
    print("4. Para deployment en la nube, consulta:")
    print("   deployment/CLOUD_DEPLOYMENT.md")
    print()
    print("5. Para desarrollar nuevos modelos:")
    print("   cd notebooks")
    print("   jupyter notebook")
    print("=" * 60)

if __name__ == "__main__":
    setup_project()
