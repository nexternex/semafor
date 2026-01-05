import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. KONFIGURACIJA I STIL
st.set_page_config(page_title="Pančevo Sentinel 2026", layout="wide", page_icon="🛡️")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #3e445b; }
    </style>
    """, unsafe_allow_name=True)

# 2. PODACI I PRORAČUNI
@st.cache_data(ttl=3600)
def get_all_data():
    # Live Berza
    gold = yf.Ticker("GC=F").history(period="max")['Close']
    silver = yf.Ticker("SI=F").history(period="max")['Close']
    eurusd = yf.Ticker("EURUSD=X").history(period="max")['Close']
    
    # Proračun cene grama u EUR (trenutno)
    current_gold_eur_gram = (gold.iloc[-1] / eurusd.iloc[-1]) / 31.1035
    gs_ratio = gold.iloc[-1] / silver.iloc[-1]
    
    # Istorija Pančeva (55m2 stan)
    hist_data = {
        'Godina': [2000, 2008, 2012, 2019, 2023, 2026],
        'Cena_m2_EUR': [300, 850, 700, 900, 1450, 1850],
        'Zlato_Gram_EUR': [10, 20, 42, 44, 60, current_gold_eur_gram]
    }
    df = pd.DataFrame(hist_data)
    df['Stan_u_Zlatu_g'] = (df['Cena_m2_EUR'] * 55) / df['Zlato_Gram_EUR']
    
    return gold, df, gs_ratio, current_gold_eur_gram

try:
    gold_series, df_hist, gs_ratio, live_gram = get_all_data()

    st.title("🛡️ Pančevo Economic Sentinel v2.0")
    st.subheader(f"Analiza tržišta i stres indikatori — {pd.Timestamp.now().strftime('%d.%m.%2026.')}")

    # --- SEKCIJA 1: STRES TEST (DASHBOARD) ---
    st.header("🚦 Globalni Stres Indikatori")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Gold/Silver Ratio", f"{gs_ratio:.2f}", 
                  delta="Kritično (>85)" if gs_ratio > 85 else "Stabilno", delta_color="inverse")
    with c2:
        st.metric("Zlato (EUR/gram)", f"{live_gram:.2f} €", delta="Rast poverenja" if live_gram > 100 else "Normalno")
    with c3:
        status = "🔴 VISOK RIZIK" if gs_ratio > 85 else "🟢 STABILNO"
        st.metric("Status Sistema", status)

    if gs_ratio > 85:
        st.error("🚨 Upozorenje: Visok Gold/Silver ratio istorijski prethodi krahu berze i nekretnina.")

    st.divider()

    # --- SEKCIJA 2: KALKULATOR PANČEVO ---
    st.header("🏢 Kalkulator: Moja nekretnina u zlatu")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        kvadrat = st.number_input("Cena kvadrata u Pančevu (€):", value=1850)
        m2 = st.slider("Površina stana:", 20, 150, 55)
        ukupno_eur = kvadrat * m2
        u_zlatu = ukupno_eur / live_gram
        
        st.write(f"### Ukupno: **{ukupno_eur:,.0f} €**")
        st.write(f"### U zlatu: **{u_zlatu:.2f} grama**")
    
    with col_b:
        # Grafik poređenja gramaže kroz istoriju
        fig_bar = go.Figure(go.Bar(
            x=df_hist['Godina'], y=df_hist['Stan_u_Zlatu_g'],
            marker_color=['#ffd700' if g == 2026 else '#3e445b' for g in df_hist['Godina']]
        ))
        fig_bar.update_layout(title="Grama zlata potrebnih za stan (Pančevo)", template="plotly_dark", height=300)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # --- SEKCIJA 3: ISTORIJSKI GRAFIKON ZLATA ---
    st.header("📈 Istorijski trend zlata (Max)")
    fig_gold = go.Figure(go.Scatter(x=gold_series.index, y=gold_series.values, line=dict(color='gold', width=2)))
    fig_gold.update_layout(template="plotly_dark", xaxis_title="Godina", yaxis_title="Cena u USD (Unca)")
    st.plotly_chart(fig_gold, use_container_width=True)

    # --- ZAKLJUČAK ---
    st.info(f"""
    **Rezime analize:** Trenutno je za stan u Pančevu potrebno **{u_zlatu:.0f}g** zlata. 
    Poređenja radi, 2008. godine ti je trebalo **2.337g**. 
    Ovo znači da su nekretnine izgubile **{((2337-u_zlatu)/2337)*100:.1f}%** svoje realne vrednosti u odnosu na zlato.
    """)

except Exception as e:
    st.error(f"Došlo je do greške pri učitavanju: {e}")
    st.info("Proveri da li su 'yfinance', 'pandas' i 'plotly' u tvom requirements.txt fajlu.")
