import streamlit as st
import yfinance as yf
import pandas as pd

# Podešavanje stranice
st.set_page_config(page_title="Pančevo Stress Monitor", page_icon="📈")

st.title("🛡️ Finansijski Stress Monitor v1.0")
st.markdown("Prati signale 'Velikog preloma' u realnom vremenu.")

# Funkcija za povlačenje podataka
@st.cache_data(ttl=3600)
def get_data():
    gold = yf.Ticker("GC=F").history(period="1y")['Close']
    silver = yf.Ticker("SI=F").history(period="1y")['Close']
    tnx = yf.Ticker("^TNX").history(period="1y")['Close'] # 10Y Yield
    irx = yf.Ticker("^IRX").history(period="1y")['Close'] # 13W Yield (zamena za 2Y)
    return gold, silver, tnx, irx

try:
    gold, silver, tnx, irx = get_data()
    
    # 1. Gold/Silver Ratio
    gs_ratio = gold.iloc[-1] / silver.iloc[-1]
    
    # 2. Yield Curve (10Y - 3M)
    yield_spread = tnx.iloc[-1] - irx.iloc[-1]

    # Kolone za metriku
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Gold/Silver Ratio", f"{gs_ratio:.2f}", 
                  delta="- Opasno" if gs_ratio > 85 else "Normalno", delta_color="inverse")
        
    with col2:
        st.metric("Yield Curve Spread", f"{yield_spread:.2f}%", 
                  delta="RECESIJA" if yield_spread < 0 else "OK")

    st.divider()

    # Analiza i preporuka
    st.subheader("📊 Analiza Rizika")
    if gs_ratio > 85 or yield_spread < 0:
        st.error("🚨 VISOK RIZIK: Istorijski parametri ukazuju na nestabilnost sistema.")
        st.write("**Savet:** Razmisli o prebacivanju dela kapitala u fizičko zlato. Nekretnine u Pančevu mogu postati nelikvidne.")
    else:
        st.success("✅ SISTEM STABILAN: Parametri su u granicama normale.")

    # Grafikon zlata
    st.subheader("Cena zlata (zadnjih godinu dana)")
    st.line_chart(gold)

except Exception as e:
    st.error(f"Greška pri učitavanju podataka: {e}")

st.caption("Podaci se ažuriraju automatski sa Yahoo Finance.")