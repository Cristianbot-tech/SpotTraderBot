import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
st.set_page_config(
    page_title="CRYPTOSCALPER",
    page_icon="favicon.png",
    layout="wide"
)

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:

    with st.form("login"):

        clave = st.text_input(
            "Introduce contraseña",
            type="password"
        )

        entrar = st.form_submit_button("ENTRAR")

    if entrar:

        if clave == "CRYPTOSCALPER123":
            st.session_state.auth = True
            st.rerun()

        else:
            st.error("Contraseña incorrecta")

    st.stop()

st.markdown(
    """
    <h1 style='color:red; text-align:center;'>
        CRYPTOSCALPER
    </h1>
    """,
    unsafe_allow_html=True
)
pagina = st.radio(
    "",
    ["HOME", "LIVE TRADING"],
    horizontal=True
)
st.markdown(
    """
    <h3 style='color:white; text-align:center;'>
        BOT PRO
    </h3>
    """,
    unsafe_allow_html=True
)
if pagina == "HOME":

    st.markdown("""
    <style>

    .main-title{
        font-size:90px;
        font-weight:900;
        color:white;
        line-height:0.9;
    }

    .red{
        color:#ff2b2b;
        text-shadow:0px 0px 20px red;
    }

    .subtitle{
        color:#888;
        font-size:22px;
        margin-top:30px;
    }

    .card{
        background:#111;
        padding:30px;
        border-radius:20px;
        margin-top:30px;
        border:1px solid #222;
        box-shadow:0px 0px 20px rgba(255,0,0,0.2);
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-title">
        TRADING
        <br>
        <span class="red">
            ALGORÍTMICO
        </span>
        <br>
        DE PRECISIÓN
    </div>

    <div class="subtitle">
        Sistema avanzado de trading con inteligencia artificial,
        señales premium y ejecución profesional en tiempo real.
    </div>
    """, unsafe_allow_html=True)

  st.markdown(
    """
    <div class="card">

        <div style="
            color:#ff2b2b;
            font-size:26px;
            font-weight:bold;
            margin-bottom:20px;
        ">
            LIVE PERFORMANCE
        </div>

        <div style="
            color:white;
            font-size:60px;
            font-weight:900;
        ">
            +324%
        </div>

        <div style="
            color:gray;
            font-size:18px;
        ">
            PROFIT TOTAL
        </div>

    </div>
    """,
    unsafe_allow_html=True
)
if pagina == "LIVE TRADING":        
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        crypto = st.selectbox(
            "Selecciona par",
            ["BTC/USDT", "ETH/USDT", "SOL/USDT",  "XRP/USDT", "DOGE/USDT", "BILL/USDT", "POL/USDT", "ONDO/USDT"]
        )
    
    with col2:
        tp = st.number_input("Take Profit %", value=1.50)
    
    with col3:
        sl = st.number_input("Stop Loss %", value=1.00)
    
    with col4:
       if "bot_activo" not in st.session_state: 
        st.session_state.bot_activo = False
           
       if st.button("Iniciar Bot", key="btn_iniciar"):
            st.session_state.bot_activo = True
    
       if st.button("Detener Bot", key="btn_detener"):
            st.session_state.bot_activo = False
        
    panel = st.empty()
    top1, top2 = st.columns(2)
    
    with top1:
        timeframe = st.selectbox(
            "Temporalidad",
            ["1min", "5min", "15min", "1hour"],
            index=0
        )
    
    with top2:
    
        volumen_box = st.empty()
    
    if st.session_state.bot_activo:
        market = crypto.replace("/", "")
        url = (
            f"https://api.coinex.com/v2/spot/kline"
            f"?market={market}&period={timeframe}&limit=50"
        )
        response = requests.get(url)
        data = response.json()
    
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []
    
        for candle in data["data"]:
            opens.append(float(candle["open"]))
            highs.append(float(candle["high"]))
            lows.append(float(candle["low"]))
            closes.append(float(candle["close"]))
            volumes.append(float(candle["volume"]))
        precio_actual = closes[-1]
        df = pd.DataFrame({
            "open": opens[-100:],
            "high": highs[-100:],
            "low": lows[-100:],
            "close": closes[-100:],
            "volume": volumes[-100:]
        })
        df["EMA9"] = df["close"].ewm(span=9).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean() 
        volumen_box.metric(
            "📊 Volumen",
             round(df["volume"].iloc[-1], 2)
        )
    
        precio_actual = closes[-1]
        ema9 = df["EMA9"].iloc[-1]
        ema21 = df["EMA21"].iloc[-1]
    
        soporte = df['low'].tail(20).min()
        resistencia = df['high'].tail(20).max()
       
        with st.container():
    
           fig = go.Figure(data=[go.Candlestick(
               x=df.index,
               open=df['open'],
               high=df['high'],
               low=df['low'],
               close=df['close'],
               name='BTC/USDT',
    
               increasing=dict(
                   line=dict(color='lime'),
                   fillcolor='lime'
               ),
    
               decreasing=dict(
                   line=dict(color='red'),
                   fillcolor='red'
               )
    
           )])
    
           fig.add_trace(go.Scatter(
               x=df.index,
               y=df['EMA9'],
               mode='lines',
               name='EMA 9'
           ))
    
           fig.add_trace(go.Scatter(
               x=df.index,
               y=df['EMA21'],
               mode='lines',
               name='EMA 21'
           ))
           fig.add_hline(
               y=soporte,
               line_dash="dot",
               line_color="green",
               annotation_text="Soporte"
           )
    
           fig.add_hline(
               y=resistencia,
               line_dash="dot",
               line_color="red",
               annotation_text="Resistencia"
           )
           fig.update_layout(
               height=700,
               xaxis_rangeslider_visible=False
           )
    
           st.plotly_chart(fig, use_container_width=True)
    
           with panel.container():
    
               cambio = precio_actual - closes[-2]
    
               st.metric(
                   "💰 Precio actual",
                   round(precio_actual, 2),
                   round(cambio, 2)
               )
               col1, col2, col3 = st.columns(3)
    
               with col1:
                   st.write("EMA 9:",round(ema9, 2))
    
               with col2:
                   st.write("EMA 21:",round(ema21, 2))
    
               with col3:
                   contador = st.empty()
    
                   if ema9 > ema21:
                       st.success("🚀COMPRA SPOT")
    
                   elif ema9 < ema21:
                       st.error("📉VENTA SPOT")
    
                   st.success(f"Bot iniciado para {crypto}")
                   for i in range(60, 0, -1):
                       contador.write(i)
                       time.sleep(1)
                   st.rerun()
