import shutil
import os

source_dir = r"c:\Users\emima\OneDrive\Escritorio\proyecto delfos - copia\gb_low"
target_dir = r"c:\Users\emima\OneDrive\Escritorio\proyecto delfos - copia\delfos-production\pipeline\models"

os.makedirs(target_dir, exist_ok=True)

files_to_copy = [
    'gb_low_model.pkl',
    'gb_low_columns.pkl',
    'umbral_gb_low_columns.pkl'
]

for file in files_to_copy:
    source = os.path.join(source_dir, file)
    target = os.path.join(target_dir, file)
    
    if os.path.exists(source):
        shutil.copy2(source, target)
        print(f"✅ Copiado: {file}")
    else:
        print(f"❌ No encontrado: {file}")

print("\n✅ Modelos copiados a la carpeta de producción")
