import os
import pandas as pd
import numpy as np
import plotly.express as px
import time
import unicodedata
import streamlit as st

# Inițializăm memoria chat-ului și starea analizei
if "istoric_chat" not in st.session_state:
    st.session_state.istoric_chat = []
if "analiza_vizibila" not in st.session_state:
    st.session_state.analiza_vizibila = False

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="CareSurge AI | Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --- FUNCȚIE PENTRU ELIMINAREA DIACRITICELOR ---
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKD', text)
    text_fara_diacritice = "".join([c for c in text if not unicodedata.combining(c)])
    return text_fara_diacritice.lower().strip()

# --- ÎNCĂRCARE DATE ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, '..', 'data', 'spitale.csv')
    
    if not os.path.exists(csv_path):
        csv_path = 'spitale.csv'
        
    df = pd.read_csv(csv_path)
    df['oras'] = df['oras'].astype(str).str.strip()
    df['nume'] = df['nume'].astype(str).str.strip()
    
    df['oras_search'] = df['oras'].apply(normalize_text)
    return df

df_spitale = load_data()

# --- STYLE (CSS MINIMAL) ---
st.markdown("""
    <style>
    /* Stilul general al cardului */
    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 10px 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Micsorăm fontul valorii principale (ex: Gastroenterologie, 82%) */
    [data-testid="stMetricValue"] {
        font-size: 1.4rem !important; 
        word-wrap: break-word !important; 
        white-space: normal !important; 
        line-height: 1.2 !important; 
    }
    
    /* Ajustăm și textul gri de deasupra (titlul cardului) pentru proporție */
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
    }
    
    /* Stil pentru Tab-uri ca să arate mai premium */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 10px;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: INPUT DATE ---
with st.sidebar:
    st.header("📍 Selecție Locație")
    st.markdown("Caută unitatea medicală pentru a evalua riscul de suprasolicitare.", help="Folosește denumirea orașului fără diacritice dacă dorești o căutare rapidă.")
    st.divider()
    
    def reseteaza_analiza():
        st.session_state.analiza_vizibila = False
        
    # Folosim placeholder în loc să aglomerăm eticheta
    oras_introdus = st.text_input("Oraș:", placeholder="ex: Bucuresti, Cluj, Iasi", on_change=reseteaza_analiza).strip()
    
    spital_selectat = None
    lat_curent = None
    lon_curent = None
    oras_afisare = ""

    if oras_introdus:
        oras_cautare = normalize_text(oras_introdus)
        df_filtrat = df_spitale[df_spitale['oras_search'] == oras_cautare]
        
        if not df_filtrat.empty:
            lista_spitale = sorted(df_filtrat['nume'].unique().tolist())
            spital_selectat = st.selectbox("Unitate Medicală:", lista_spitale, on_change=reseteaza_analiza)
            
            oras_afisare = df_filtrat.iloc[0]['oras']
            
            if spital_selectat:
                spital_info = df_filtrat[df_filtrat['nume'] == spital_selectat].iloc[0]
                lat_curent = spital_info['lat']
                lon_curent = spital_info['long']
        else:
            st.warning(f"Nu am găsit rezultate pentru '{oras_introdus}'.")
    
    st.divider()
    buton_activ = spital_selectat is not None
    # type="primary" face butonul să aibă culoarea principală a temei, ieșind în evidență
    predict_btn = st.button("🔍 Generează Raport de Risc", use_container_width=True, disabled=not buton_activ, type="primary")

# Dacă s-a apăsat butonul, salvăm starea în memorie
if predict_btn:
    st.session_state.analiza_vizibila = True

# --- HEADER APLICAȚIE (ECRAN PRINCIPAL) ---
if spital_selectat:
    st.title(f"🏥 {spital_selectat}")
    st.markdown(f"**📍 Locație:** {oras_afisare} | **Status:** Așteptare date contextuale")
    st.divider()
else:
    # ECRAN DE START (Când nu e nimic selectat)
    st.title("👋 Bine ai venit în CareSurge AI")
    st.markdown("""
    **Platforma Geospațială de Triaj Predictiv On-Demand**
    
    Acest sistem sprijină deciziile manageriale medicale prin combinarea datelor istorice cu factori de risc externi (ex: condiții meteo extreme, evenimente de risc).
    
    👉 **Cum funcționează:**
    1. Introdu orașul în meniul din stânga.
    2. Selectează unitatea medicală dorită.
    3. Generează raportul pentru a vedea analiza inteligentă pe departamente.
    """)
    st.info("Aștept selecția ta pentru a începe procesarea datelor...")

# --- LOGICĂ AFISARE REZULTATE ---
if st.session_state.analiza_vizibila:
    
    # Spinner-ul stă deasupra tab-urilor ca să arate că toată aplicația lucrează
    if predict_btn:
        with st.spinner('Se preiau datele meteo și se rulează modelul ML...'):
            time.sleep(1.5) 
            
    risc = 82 if normalize_text(oras_introdus) in ["constanta", "brasov", "bucuresti"] else 38

    # --- CREAREA CELOR 2 TAB-URI ---
    tab_dashboard, tab_simulator = st.tabs(["📊 Dashboard Principal", "🤖 Simulator What-If"])

    # ====== TAB 1: DASHBOARD PRINCIPAL ======
    with tab_dashboard:
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Scor Risc General", f"{risc}%", "+12%" if risc > 50 else "-2%")
        col2.metric("Departament Critic", "Ortopedie" if risc > 50 else "Gastroenterologie")
        col3.metric("Context Local", "Alertă Risc" if risc > 50 else "Stabil")
        col4.metric("Personal Necesar", "+3 Medici" if risc > 50 else "Optim")

        st.divider()

        col_chart, col_explain = st.columns([2, 1])


    

    # ====== TAB 2: SIMULATOR WHAT-IF ======
    with tab_simulator:
        st.markdown("#### Testează planurile de răspuns la criză")
        st.markdown("Interacționează cu Agentul AI pentru a evalua rapid cum ar face față spitalul în situații extreme (ex: inundații, accidente multiple, lipsă bruscă de personal).")
        st.divider()
        
        # Container pentru istoricul chat-ului (ca să nu se întindă urât)
        chat_container = st.container()
        with chat_container:
            for mesaj in st.session_state.istoric_chat:
                with st.chat_message(mesaj["rol"]):
                    st.markdown(mesaj["text"])

        # Căsuța de input a chat-ului
        scenariu = st.chat_input("Ex: Ce se întâmplă dacă diseară are loc un accident în lanț pe autostradă?")

        if scenariu:
            # Salvăm și afișăm întrebarea
            st.session_state.istoric_chat.append({"rol": "user", "text": scenariu})
            
            # Simulăm un răspuns AI în funcție de input
            raspuns_ai = f"**Analiză de impact pentru {spital_selectat}:**\n\nPe baza scenariului introdus (*\"{scenariu}\"*), modelul nostru prezice o epuizare a resurselor de la secția Primiri Urgențe în aproximativ **45 de minute**. \n\n👉 **Recomandare:** Activarea planului alb (suplimentare personal de gardă) și blocarea tuturor intervențiilor chirurgicale non-critice programate pentru următoarele 12 ore."
            st.session_state.istoric_chat.append({"rol": "assistant", "text": raspuns_ai})
            
            # Reîncărcăm pagina pentru a afișa mesajele în tab-ul corect
            st.rerun()