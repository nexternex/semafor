import streamlit as st
import yfinance as yf
import pandas as pd

# Podešavanja aplikacije
st.set_page_config(page_title="Pančevo Gold-House Tracker", page_icon="🏢")

@st.cache_data(ttl=3600)
def get_market_data():
    # Povlačenje unce zlata u EUR (GC=F je u USD, pretvaramo preko EURUSD=X)
    gold_usd = yf.Ticker("GC=F").history(period="1d")['Close'].iloc[-1]
    eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
    gold_eur_ounce = gold_usd / eur_usd
    gold_eur_gram = gold_eur_ounce / 31.1035
    
    # Srebro za ratio
    silver_usd = yf.Ticker("SI=F").history(period="1d")['Close'].iloc[-1]
    gs_ratio = gold_usd / silver_usd
    
    return gold_eur_ounce, gold_eur_gram, gs_ratio

st.title("🏢 Pančevo: Nekretnine vs Zlato")
st.markdown(f"**Datum:** {pd.Timestamp.now().strftime('%d.%m.%2026.')}")

try:
    g_ounce, g_gram, ratio = get_market_data()

    # --- SEKCIJA 1: KALKULATOR ZA PANČEVO ---
    st.header("🧮 Kalkulator Vrednosti")
    
    # Prosečne vrednosti za Pančevo 2026
    kvadrat_eur = st.number_input("Cena kvadrata u Pančevu (€):", value=1750)
    povrsina = st.slider("Površina stana (m2):", 20, 120, 55)
    
    ukupna_cena_eur = kvadrat_eur * povrsina
    potrebno_zlata_grama = ukupna_cena_eur / g_gram
    potrebno_zlata_unci = ukupna_cena_eur / g_ounce

    col1, col2, col3 = st.columns(3)
    col1.metric("Ukupno EUR", f"{ukupna_cena_eur:,.0f}€")
    col2.metric("Vrednost u zlatu", f"{potrebno_zlata_unci:.2f} oz")
    col3.metric("U gramima", f"{potrebno_zlata_grama:.0f} g")

    # --- SEKCIJA 2: STRES INDIKATORI ---
    st.divider()
    st.header("🚨 Stress Signali")
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Gold/Silver Ratio", f"{ratio:.2f}", delta="- Visok rizik" if ratio > 85 else "Normalno", delta_color="inverse")
    with c2:
        st.metric("Cena zlata (gram)", f"{g_gram:.2f} €")

    if
