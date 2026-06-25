import mysql.connector
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib
matplotlib.use("Agg")

# Connexion MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="sales_datamart"
)

query = "SELECT * FROM sales_fact;"
df = pd.read_sql(query, conn)

print("✅ Connexion réussie, aperçu des données :")
print(df.head())

# Nettoyage des dates
df['date_id'] = pd.to_datetime(df['date_id'], errors='coerce')
df = df.dropna(subset=['date_id'])

# Agrégation mensuelle
monthly_sales = df.groupby(df['date_id'].dt.to_period('M'))['total_amount'].sum()
monthly_sales.index = monthly_sales.index.to_timestamp()
monthly_sales = monthly_sales.asfreq('M')

print("Taille de la série :", len(monthly_sales))

# Choix du modèle selon la taille
if len(monthly_sales) >= 6:
    try:
        model = SARIMAX(monthly_sales, order=(0,1,0))
        model_fit = model.fit(disp=False)
        forecast = model_fit.forecast(steps=6)
        print("Prévisions SARIMAX :", forecast)
    except Exception as e:
        print("⚠️ Erreur SARIMAX :", e)
        forecast = monthly_sales.rolling(window=3).mean().dropna()
else:
    print("⚠️ Série trop courte, utilisation d'une moyenne mobile.")
    forecast = monthly_sales.rolling(window=3).mean().dropna()

# Sauvegarde graphique
plt.figure(figsize=(10,5))
plt.plot(monthly_sales, label="Historique")
plt.plot(forecast, label="Prévisions", color="red")
plt.legend()
plt.title("Prévisions des ventes mensuelles")
plt.savefig("forecast.png")
plt.close()

# Export CSV
forecast.to_csv("forecast.csv", header=True)
