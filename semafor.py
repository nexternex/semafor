import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Pančevo Sentinel 2026 - Ultra", layout="wide")

@st.cache_data(ttl=3600)
def get_advanced_data():
    # Povlačenje podataka: Zlato, Srebro, Bakar (Copper), EUR/USD
    tickers = {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Copper': 'HG=F',
        'EURUSD': 'EURUSD=X'
    }
    
    raw_data = {}
    for name, sym in tickers.items():
        raw_data[name] = yf.Ticker(sym).history(period="5y")['Close']
    
    # Proračuni
    gs_ratio = raw_data['Gold'] / raw_data['Silver']
    copper_gold_ratio = raw_data['Copper'] / (raw_data['Gold'] / 100) # Normalizovano radi pregleda
    live_gram_eur = (raw_data['Gold'].iloc[-1] / raw_data['EURUSD'].iloc[-1]) / 31.1035
    
    return raw_data, gs_ratio, copper_gold_ratio, live_gram_eur

try:
    data, gs_ratio, cg_ratio, live_gram = get_advanced_data()

    st.title("🛡️ Pančevo Sentinel: Totalni Market Monitor")
    st.markdown(f"**Analiza rizika za Pančevo i globalna tržišta** | {pd.Timestamp.now().strftime('%d.%m.%2026.')}")

    # --- SEKCIJA 1: ALARMI (MARKERI) ---
    col1, col2, col3, col4 = st.columns(4)
    
    curr_gs = gs_ratio.iloc[-1]
    curr_cg = cg_ratio.iloc[-1]
    
    col1.metric("Gold/Silver Ratio", f"{curr_gs:.2f}", delta="ALARM" if curr_gs > 85 else "OK", delta_color="inverse")
    col2.metric("Copper/Gold Ratio", f"{curr_cg:.2f}", delta="PAD INDUSTRIJE" if curr_cg < cg_ratio.mean() else "OK", delta_color="inverse")
    col3.metric("Zlato (EUR/g)", f"{live_gram:.2f} €")
    
    # Izračunavanje ukupnog nivoa stresa (0-100)
    stress_score = 0
    if curr_gs > 80: stress_score += 40
    if curr_gs > 90: stress_score += 20
    if curr_cg < cg_ratio.mean(): stress_score += 40
    
    col4.metric("Market Stress Index", f"{stress_score}%", delta="KRITIČNO" if stress_score > 70 else "PRATI")

    st.divider()

    # --- SEKCIJA 2: GRAFIKONI SA KRITIČNIM MARKERIMA ---
    st.subheader("📊 Vizuelni Markeri Rizika")
    
    tab1, tab2 = st.tabs(["Gold/Silver (Strah)", "Copper/Gold (Recesija)"])
    
    with tab1:
        fig_gs = go.Figure()
        fig_gs.add_trace(go.Scatter(x=gs_ratio.index, y=gs_ratio.values, name="GSR Ratio", line=dict(color='orange')))
        # Dodavanje kritične linije (Marker)
        fig_gs.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="CRVENA ZONA (85)")
        fig_gs.update_layout(template="plotly_dark", height=400, title="Istorijski Gold/Silver Ratio")
        st.plotly_chart(fig_gs, use_container_width=True)
        st.caption("Kada je narandžasta linija iznad isprekidane crvene, tržište je u stanju ekstremnog straha.")

    with tab2:
        fig_cg = go.Figure()
        fig_cg.add_trace(go.Scatter(x=cg_ratio.index, y=cg_ratio.values, name="Dr. Copper/Gold", line=dict(color='cyan')))
        fig_cg.update_layout(template="plotly_dark", height=400, title="Bakar/Zlato (Indikator privredne aktivnosti)")
        st.plotly_chart(fig_cg, use_container_width=True)
        st.caption("Pad ove linije znači da industrija (Bakar) slabi, dok zlato preuzima primat. To je klasičan uvod u pad nekretnina.")

    st.divider()

    # --- SEKCIJA 3: LOKALNI KALKULATOR (PANČEVO) ---
    st.header("🏠 Pančevo Real-Value Tracker")
    c_left, c_right = st.columns([1, 1])
    
    with c_left:
        cena_m2 = st.number_input("Trenutna cena kvadrata u Pančevu (€):", value=1850)
        kvadrata = st.slider("Veličina stana:", 20, 150, 55)
        ukupno_eur = cena_m2 * kvadrata
        u_zlatu = ukupno_eur / live_gram
        
        st.write(f"Vrednost u evrima: **{ukupno_eur:,.0f} €**")
        st.write(f"Vrednost u zlatu: **{u_zlatu:.2f} grama**")
        
    with c_right:
        # Analiza u odnosu na 'Dr. Bakra'
        st.info(f"""
        **Analiza za Pančevo:**
        Trenutno je tržište pod pritiskom. Dok god je **GSR iznad 80**, 
        investiranje u nove kvadrate nosi rizik od brze korekcije. 
        Zadrži likvidnost u zlatu dok se GSR ne vrati ispod 70.
        """)

except Exception as e:
    st.error(f"Greška pri ažuriranju markera: {e}")
