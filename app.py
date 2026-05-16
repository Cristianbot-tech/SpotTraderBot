import streamlit as st
import pandas as pd
import requests
import time
# import plotly.graph_objects as go
st.title("SpotTraderBot 🚀")

st.write("Bot de trading spot para CoinEx")

crypto = st.selectbox(
    "Selecciona una criptomoneda",
    ["BTC/USDT", "ETH/USDT", "SOL/USDT", "DOGE/USDT", "XRP/USDT", "BILL/USDT", "POL/USDT", "ONDO/USDT"]
)

tp = st.number_input("Take Profit %", value=1.5)

sl = st.number_input("Stop Loss %", value=1.0)

    panel = st.empty()
    grafico = st.empty()

    if "bot_activo" not in st.session_state: 
        st.session_state.bot_activo = False

    if st.button("Iniciar Bot"):
        st.session_state.bot_activo = True

    if st.session_state.bot_activo:
    while True:
        url = f"https://api.coinex.com/v2/spot/kline?market={crypto.replace('/','')}&period=1min&limit=50"

        response = requests.get(url)
        data = response.json()

        opens = []
        highs = []
        lows = []
        closes = []

        for candle in data["data"]:
            opens.append(float(candle["open"]))
            highs.append(float(candle["high"]))
            lows.append(float(candle["low"]))
            closes.append(float(candle["close"]))
        precio_actual = closes[-1]
        df = pd.DataFrame({
            "open": opens[-100:],
            "high": highs[-100:],
            "low": lows[-100:],
            "close": closes[-100:]
        })
        df["EMA9"] = df["close"].ewm(span=9).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()

        ema9 = df["EMA9"].iloc[-1]
        ema21 = df["EMA21"].iloc[-1]
        with grafico.container():
            st.line_chart(
                df[["close", "EMA9", "EMA21"]],
                height=400
            )
        with panel.container():

            cambio = precio_actual - closes[-2]

            st.metric(
                "💰 Precio",
                round(precio_actual, 2),
                round(cambio, 2)
            )
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("EMA 9:", ema9)

            with col2:
                st.write("EMA 21:", ema21)

            with col3:
                contador = st.empty()

            if ema9 > ema21:
                st.success("COMPRA SPOT 🚀")

            elif ema9 < ema21:
                st.error("VENTA SPOT 📉")

            st.success(f"Bot iniciado para {crypto}")
        for i in range(60, 0, -1):
            contador.write(i)
            time.sleep(1)
        st.rerun()
