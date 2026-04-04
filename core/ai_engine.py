import pandas as pd
import numpy as np
import os
from prophet import Prophet

def get_training_data():
    # 1. Stabilirea căilor către fișiere
    base_path = os.path.dirname(__file__) 
    path_admisie = os.path.abspath(os.path.join(base_path, '..', 'data', 'admission_data.csv'))
    path_meteo = os.path.abspath(os.path.join(base_path, '..', 'data', 'meteo.csv'))
    
    print("⏳ Se încarcă fișierele...")

    # 2. PROCESARE DATE SPITAL (Admission Data)
    df_raw = pd.read_csv(path_admisie)
    
    # Rezolvăm problema formatului mixt: 2017 (M/D/Y) vs 2018-2019 (D/M/Y)
    # Mai întâi transformăm brut ca să putem detecta anul
    temp_dates = pd.to_datetime(df_raw['D.O.A'], format='mixed', dayfirst=True)

    # Grupăm pacienții pe zi (numărăm rândurile pentru fiecare 'ds')
    df_daily = df_raw.groupby('ds').size().reset_index(name='y')

    # 3. PROCESARE DATE METEO
    df_meteo = pd.read_csv(path_meteo)
    df_meteo['ds'] = pd.to_datetime(df_meteo['datetime'])
    
    # Selectăm doar data și temperatura medie (coloana 'temp' din meteo.csv)
    df_meteo = df_meteo[['ds', 'temp']].rename(columns={'temp': 'Temperatura'})

    # 4. ÎMBINARE (MERGE)
    # "Lipim" temperatura de datele spitalului folosind coloana comună 'ds'
    df_final = pd.merge(df_daily, df_meteo, on='ds', how='left')

    # 5. CURĂȚARE FINALĂ ȘI SORTARE
    df_final = df_final.sort_values('ds')
    
    # Umplem eventualele goluri de temperatură (Forward Fill)
    df_final['Temperatura'] = df_final['Temperatura'].ffill()
    
    # Dacă tot mai avem NaN (ex: prima zi nu are meteo), punem o medie generală
    df_final['Temperatura'] = df_final['Temperatura'].fillna(df_final['Temperatura'].mean())

    print(f"✅ Procesare completă. Avem {len(df_final)} zile de antrenament.")
    return df_final

def antreneaza_si_prezice(df_train, temp_viitor):
    """
    Antrenează Prophet și face o predicție bazată pe o temperatură dată.
    """
    # Configurare model
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.add_regressor('Temperatura')
    
    # Antrenare
    model.fit(df_train)
    
    # Creăm un rând pentru "mâine" (sau o dată viitoare)
    future_date = df_train['ds'].max() + pd.Timedelta(days=1)
    future_df = pd.DataFrame({'ds': [future_date], 'Temperatura': [temp_viitor]})
    
    # Predicție
    forecast = model.predict(future_df)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

# ==========================================
# TESTARE FLUX COMPLET
# ==========================================
if __name__ == "__main__":
    try:
        # Pasul 1: Obținem datele curate
        date_pregatite = get_training_data()
        print("\n📊 Primele 5 rânduri din setul de date combinat:")
        print(date_pregatite.head())

        # Pasul 2: Facem o predicție de test pentru o zi cu 0 grade (iarnă)
        print("\n🔮 Calculăm predicția pentru o zi de iarnă (0°C)...")
        predictie = antreneaza_si_prezice(date_pregatite, 0)
        
        numar_prezis = round(predictie['yhat'].values[0], 2)
        print(f"✅ Rezultat: Se estimează un număr de {numar_prezis} pacienți.")

    except Exception as e:
        print(f"❌ A apărut o eroare: {e}")