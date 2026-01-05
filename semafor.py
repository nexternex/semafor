import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Pančevo Gold-Housing Analytics", layout="wide")

# 1. ISTORIJSKI PODACI (Pančevo prosek 55m2)
data_pancevo = {
    'Godina': [2000, 2008, 2012, 2019, 2023, 2026],
    'Cena_m2_EUR': [300, 850, 700, 900, 1450, 1850],
    'Cena_Zlato_Gram_EUR': [10, 20, 42, 44, 60, 125] # 2026 je procena/live
}
df_hist = pd.DataFrame(data_pancevo)
df_hist['Stan_55m2_Zlato_Gram'] = (df_hist['Cena_m2_EUR'] * 55) / df_hist['Cena_Zlato_Gram_EUR']

# 2. FUNKCIJA ZA LIVE PODATKE
@st.cache_data(ttl=3600)
def get_live_gold():
    gold_usd = yf.Ticker("GC=F").history(period="max")['Close']
    eur_usd = yf.Ticker("EURUSD=X").history(period="max")['Close']
    # Konverzija u EUR po gramu (gruba procena za istoriju)
    gold_eur_gram = (gold_usd / 31.1035) / 1.08 # fiksiran kurs za grafikon radi stabilnosti
    return gold_eur_gram

st.title("📈 Analiza: Pančevo vs Zlato (2000 - 2026)")

try:
    live_gold = get_live_gold()

    # --- GRAFIKON 1: VREDNOST ZLATA OD 2000. ---
    st.subheader("1. Kretanje cene zlata (EUR/gram) od 2000. godine")
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=live_gold.index, y=live_gold.values, name="Cena zlata (EUR/g)", line=dict(color='gold', width=3)))
    fig1.update_layout(template="plotly_dark", xaxis_title="Godina", yaxis_title="EUR po gramu")
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # --- GRAFIKON 2: ODNOS CENA (STANOVI U ZLATU) ---
    st.subheader("2. Koliko grama zlata je potrebno za stan od 55m² u Pančevu?")
    
    fig2 = go.Figure()
    # Linija za gramažu
    fig2.add_trace(go.Bar(x=df_hist['Godina'], y=df_hist['Stan_55m2_Zlato_Gram'], 
                          name="Grami zlata za stan", marker_color='orange'))
    
    fig2.update_layout(template="plotly_dark", xaxis_title="Godina", yaxis_title="Grami zlata (ukupno)")
    st.plotly_chart(fig2, use_container_width=True)

    # --- ANALITIKA ---
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"""
        **Zanimljivost:**
        Najskuplji stanovi u Pančevu (u odnosu na zlato) bili su **2008. godine**. 
        Tada je za stan trebalo preko **2.300 grama** zlata.
        """)
    with col2:
        danas_grami = df_hist['Stan_55m2_Zlato_Gram'].iloc[-1]
        st.warning(f"""
        **Trenutno stanje (2026):**
        Iako je cena u evrima rekordna, za isti stan ti treba oko **{danas_grami:.0f} grama** zlata. 
        To je skoro **3 puta manje** nego 2008!
        """)

except Exception as e:
    st.error(f"Greška: {e}")

st.write("Savet: Ako linija zlata na prvom grafikonu postane vertikalna, to je signal za 'Veliko resetovanje'.")
