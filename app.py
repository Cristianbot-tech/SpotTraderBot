import streamlit as st

st.title("TraderBotSpot")

st.write("Bot de trading spot para CoinEx")

crypto = st.selectbox(
    "Selecciona una criptomoneda",
    ["DOGE/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "BILL/USDT", "POL/USDT", "ONDO/UST"]
)

tp = st.number_input("Take Profit %", value=1.5)

sl = st.number_input("Stop Loss %", value=1.0)

if st.button("Iniciar Bot"):
    st.success(f"Bot iniciado para {crypto}")
