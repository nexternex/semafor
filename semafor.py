import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. OSNOVNA PODEŠAVANJA
st.set_page_config(page_title="Pančevo Sentinel 2026", layout="wide")

# 2. POMOĆNA FUNKCIJA ZA PODATKE
@st.cache_data(ttl=3600)
def fetch_all():
    # Uzimamo Zlato, Srebro i Kurs EUR/USD
    gold = yf.Ticker("GC=F").history(period="max")['Close']
    silver = yf.Ticker("SI=F").history(period="max")['Close']
    eurusd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
    
    live_gold_price = gold.iloc[-1]
    live_gram_eur = (live_gold_price / eurusd) / 31.1035
    ratio = live_gold_price / silver.iloc[-1]
    
    # Istorija Pančeva
    hist_data = {
        'Godina': [2000, 2008, 2012, 2019, 2023, 2026],
        'Cena_m2': [300, 850, 700, 900, 1450, 1850],
        'Gram_EUR': [10, 20, 42, 44, 60, live_gram_eur]
    }
    df = pd.DataFrame(hist_data)
    df['Stan_u_Zlatu'] = (df['Cena_m2'] * 55) / df['Gram_EUR']
    
    return gold, df, ratio, live_gram_eur

# 3. GLAVNI PROGRAM
try:
    gold_data, df_hist, gs_ratio, live_gram = fetch_all()

    st.title("🛡️ Pančevo Economic Sentinel")
    st.write(f"Osveženo: {pd.Timestamp.now().strftime('%d.%m.%2026. %H:%M')}")

    # STRES SEKCIJA
    col1, col2, col3 = st.columns(3)
    col1.metric("Gold/Silver Ratio", f"{gs_ratio:.2f}")
    col2.metric("Zlato (EUR/g)", f"{live_gram:.2f} €")
    
    status = "🔴 RIZIK" if gs_ratio > 80 else "🟢 OK"
    col3.metric("Status Sistema", status)

    # KALKULATOR I GRAFIKON
    st.divider()
    c_left, c_right = st.columns([1, 2])
    
    with c_left:
        st.subheader("🏠 Kalkulator")
        m2_cena = st.number_input("Cena kvadrata (€):", value=1850)
        kvadratura = st.slider("Površina stana:", 20, 120, 55)
        ukupno = m2_cena * kvadratura
        u_gramima = ukupno / live_gram
        st.write(f"Vrednost stana: **{ukupno:,.0f} €**")
        st.write(f"U zlatu: **{u_gramima:.2f} g**")

    with c_right:
        fig_hist = go.Figure(go.Bar(x=df_hist['Godina'], y=df_hist['Stan_u_Zlatu'], marker_color='orange'))
        fig_hist.update_layout(title="Potrebno grama zlata za stan (Pančevo)", template="plotly_dark", height=300)
        st.plotly_chart(fig_hist, use_container_width=True)

    # VELIKI GRAFIKON ZLATA
    st.subheader("📈 Dugoročni trend zlata (USD/oz)")
    fig_gold = go.Figure(go.Scatter(x=gold_data.index, y=gold_data.values, line=dict(color='gold')))
    fig_gold.update_layout(template="plotly_dark")
    st.plotly_chart(fig_gold, use_container_width=True)

except Exception as e:
    st.error(f"Greška: {e}")
