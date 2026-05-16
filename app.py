import streamlit as st
import pandas as pd
import requests
st.title("TraderBotSpot")

st.write("Bot de trading spot para CoinEx")

crypto = st.selectbox(
    "Selecciona una criptomoneda",
    ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT", "XRP/USDT", "BILL/USDT", "POL/USDT", "ONDO/USDT"]
)

tp = st.number_input("Take Profit %", value=1.5)

sl = st.number_input("Stop Loss %", value=1.0)

if st.button("Iniciar Bot"):
    url = f"https://api.coinex.com/v2/spot/kline?market={crypto.replace('/','')}&period=1min&limit=50"

    response = requests.get(url)
    data = response.json()

    closes = []
    for candle in data["data"]:
        closes.append(float(candle["close"]))
    precio_actual = closes[-1]

    st.write("Precio actual:", precio_actual)

    df = pd.DataFrame(closes, columns=["close"])

    ema9 = df["close"].ewm(span=9).mean().iloc[-1]
    ema21 = df["close"].ewm(span=21).mean().iloc[-1]
    
    st.write("EMA 9:", ema9)
    st.write("EMA 21:", ema21)

    if ema9 > ema21:
        st.success("COMPRA SPOT 🚀")

    elif ema9 < ema21:
        st.error("VENTA SPOT 📉")
    st.success(f"Bot iniciado para {crypto}")
