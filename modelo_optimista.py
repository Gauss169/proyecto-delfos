import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix
import os
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc

# Crear carpeta si no existe
output_dir = "gb_high"
os.makedirs(output_dir, exist_ok=True)


sol = pd.read_csv('sol_dinamicas.csv')
btc = pd.read_csv('btc_dinamicas.csv')
eth = pd.read_csv('eth_dinamicas.csv')
xrp = pd.read_csv('xrp_dinamicas.csv')

sol['cripto'] = 'SOL'
btc['cripto'] = 'BTC'
eth['cripto'] = 'ETH'
xrp['cripto'] = 'XRP'

data = pd.concat([sol, btc, eth, xrp], ignore_index=True)

corte = data['high_return'].median()
data['target_high'] = data['target_high'].apply(lambda x: 1 if x < corte else 0)

data = data.dropna()

# 🔹 One Hot Encoding
data = pd.get_dummies(data, columns=['cripto'], prefix='cripto')

df = data.drop(columns={'date','open','high','close','low','target_low'})


X = df.drop(columns='target_high')
y = df['target_high']

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

gb_high = GradientBoostingClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=4,
    random_state=42
)

gb_high.fit(X_train, y_train)

# Guardar modelo
model_path = os.path.join(output_dir, "gb_high_model.pkl")

with open(model_path, "wb") as f:
    pickle.dump(gb_high, f)

print(f"Modelo guardado en: {model_path}")

y_prob = gb_high.predict_proba(X_test)[:, 1]

with open("gb_high/gb_high_columns.pkl", "wb") as f:
    pickle.dump(X.columns.tolist(), f)


# Reporte

def evaluar_umbral(y_true, y_prob, umbral, output_dir="gb_high"):
    # Crear carpeta si no existe

    y_pred = (y_prob >= umbral).astype(int)

    cm = confusion_matrix(y_true, y_pred)
    cr = classification_report(y_true, y_pred)

    file_path = os.path.join(output_dir, f"evaluacion_umbral_{umbral}.txt")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"UMBRAL = {umbral}\n\n")
        f.write("CONFUSION MATRIX\n")
        f.write(str(cm))
        f.write("\n\nCLASSIFICATION REPORT\n")
        f.write(cr)

    print(f"Informe guardado en: {file_path}")

    

evaluar_umbral(y_test, y_prob, 0.25)
evaluar_umbral(y_test, y_prob, 0.4)
evaluar_umbral(y_test, y_prob, 0.5)
evaluar_umbral(y_test, y_prob, 0.75)
evaluar_umbral(y_test, y_prob, 0.77)
evaluar_umbral(y_test, y_prob, 0.85)
evaluar_umbral(y_test, y_prob, 0.95)


# Importancia de cripto



# Importancias
importancias = pd.Series(
    gb_high.feature_importances_,
    index=X.columns
).sort_values(ascending=False)

# Importancias de cripto (one-hot)
importancias_cripto = importancias[importancias.index.str.startswith('cripto_')]

# Guardar informe
file_path = os.path.join(output_dir, "importancia_variables_gb_high.txt")

with open(file_path, "w", encoding="utf-8") as f:
    f.write("IMPORTANCIA DE VARIABLES - GRADIENT BOOSTING (HIGH)\n\n")
    f.write("TOP VARIABLES GLOBALES\n")
    f.write(importancias.to_string())
    f.write("\n\nIMPORTANCIA VARIABLES CRIPTO (ONE HOT)\n")
    f.write(importancias_cripto.to_string())

print(f"Informe guardado en: {file_path}")


# Curva ROC
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc



# Calcular ROC
fpr, tpr, thresholds = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

# Dibujar
plt.figure()
plt.plot(fpr, tpr, label=f'ROC curve (AUC = {roc_auc:.3f})')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random')

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Gradient Boosting')
plt.legend()

# Guardar imagen
file_path = os.path.join(output_dir, "ROC_gb_high.png")
plt.savefig(file_path, dpi=300, bbox_inches='tight')

plt.show()

print(f"ROC guardada en: {file_path}")


# Monitoring

df_eval = pd.DataFrame({
    'y_true': y_test.values,
    'y_prob': y_prob
})

df_eval['decile'] = pd.qcut(
    df_eval['y_prob'],
    10,
    labels=False,
    duplicates='drop'
)

# Ordenar: decil 0 = mayor probabilidad
df_eval['decile'] = 9 - df_eval['decile']

deciles = (
    df_eval
    .groupby('decile')
    .agg(
        total=('y_true', 'count'),
        positivos=('y_true', 'sum'),
        score_mean=('y_prob', 'mean')
    )
    .reset_index()
)

deciles['tasa_positivos'] = deciles['positivos'] / deciles['total']

# Global
tasa_global = df_eval['y_true'].mean()

# Uplift
deciles['uplift'] = deciles['tasa_positivos'] / tasa_global

deciles['positivos_acum'] = deciles['positivos'].cumsum()
deciles['total_acum'] = deciles['total'].cumsum()

deciles['tasa_acum'] = deciles['positivos_acum'] / deciles['total_acum']
deciles['uplift_acum'] = deciles['tasa_acum'] / tasa_global

# Separar positivos y negativos
df_eval['negativos'] = 1 - df_eval['y_true']

ks_table = (
    df_eval
    .groupby('decile')
    .agg(
        pos=('y_true', 'sum'),
        neg=('negativos', 'sum')
    )
    .sort_index()
    .reset_index()
)

# Acumulados
ks_table['pos_acum'] = ks_table['pos'].cumsum()
ks_table['neg_acum'] = ks_table['neg'].cumsum()

# Normalizar
ks_table['tpr'] = ks_table['pos_acum'] / ks_table['pos'].sum()
ks_table['fpr'] = ks_table['neg_acum'] / ks_table['neg'].sum()

# KS
ks_table['ks'] = ks_table['tpr'] - ks_table['fpr']
ks_value = ks_table['ks'].abs().max()



# Guardar CSV dentro de la carpeta
deciles.to_csv(
    os.path.join(output_dir, "Monitoring.csv"),
    index=False
)


prod = data[data['cripto_SOL'] == True].reset_index().copy()

prod_features = prod[X.columns]
prod['predict'] = gb_high.predict_proba(prod_features)[:, 1]

prod['actual_high'] = prod['high_return'].shift(-1)

prod['actual_close'] = prod['close_return'].shift(-1)


umbrales_high = np.linspace(1,1.05,11)
umbrales_decision = np.linspace(0,1,21)

dic_c = {}
n = len(prod)
for umbral_high in umbrales_high:
    for umbral_decision in umbrales_decision:
      c = 1
      for i in range(n-1):
        actual_high = prod.loc[prod.index[i], 'actual_high']
        actual_close = prod.loc[prod.index[i], 'actual_close']
        pred = prod.loc[prod.index[i], 'predict']
        if pred > umbral_decision:
          if actual_high > umbral_high:
            c *= umbral_high
          else:
            c*= 0.97
        dic_c[(umbral_high, umbral_decision)] = c

umbral_max, umbral_min = max(dic_c, key=dic_c.get), min(dic_c, key=dic_c.get)

# Desempeño



umbral_high = umbral_max[0]


resultados = []

for j in range(1, 6):
    prod_date = prod[
        (prod['date'] > f'202{j}-01-01') &
        (prod['date'] < f'202{j+1}-01-01')
    ].reset_index(drop=True)

    n = len(prod_date)
    c = 1

    for i in range(n - 1):
        actual_high = prod_date.loc[i, 'actual_high']
        actual_close = prod_date.loc[i, 'actual_close']
        pred = prod_date.loc[i, 'predict']

        if pred < umbral_max[1]:
          if actual_high > umbral_high:
            c *= umbral_high
          else:
            c*= actual_close

    resultados.append({
        'year_start': f'202{j}-01-01',
        'year_end': f'202{j+1}-01-01',
        'capital_final': c
    })

# Convertir a DataFrame
df_resultados = pd.DataFrame(resultados)


umbral_max = list(umbral_max)

with open("gb_high/umbral_gb_high_columns.pkl", "wb") as f:
    pickle.dump(umbral_max, f)



# Guardar CSV
file_path = os.path.join(output_dir, "backtest_gb_high.csv")
df_resultados.to_csv(file_path, index=False)

print(f"Resultados guardados en: {file_path}")
