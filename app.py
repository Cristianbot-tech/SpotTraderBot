import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import time

st.set_page_config(
    page_title="CRYPTOSCALPER BOT PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== LOGIN ====================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 CRYPTOSCALPER BOT PRO")
    with st.form("login"):
        clave = st.text_input("Introduce contraseña", type="password")
        if st.form_submit_button("ENTRAR"):
            if clave == "CRYPTOSCALPER123":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
    st.stop()

# ==================== NAVEGACIÓN CON SIDEBAR ====================
st.sidebar.title("📍 Navegación")
pagina = st.sidebar.radio("Ir a:", 
    ["🏠 Home", "⚡ Live Trading", "⚙️ Settings", "🧠 AI Analytics"])

# ==================== PÁGINAS ====================

if pagina == "🏠 Home":
    st.title("🏠 Dashboard General - CRYPTOSCALPER BOT PRO")
    st.success("¡Bienvenido al Dashboard!")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Win Rate", "78.4%", "↑ 3%")
    with col2:
        st.metric("Profit Total", "$12,458", "↑ $1,245")
    with col3:
        st.metric("Operaciones", "247", "↑ 18")
    with col4:
        st.metric("Drawdown", "-4.8%", "↓ 0.5%")
    
    st.info("Esta es la página Home. La iremos mejorando.")

elif pagina == "⚡ Live Trading":
    st.title("⚡ LIVE TRADING")
    
    # Aquí pegamos tu código anterior del gráfico
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        crypto = st.selectbox("Selecciona par", 
            ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BILL/USDT", "POL/USDT", "ONDO/USDT"])
    with col2:
        tp = st.number_input("Take Profit %", value=1.50)
    with col3:
        sl = st.number_input("Stop Loss %", value=1.00)
    with col4:
        if "bot_activo" not in st.session_state:
            st.session_state.bot_activo = False
        if st.button("Iniciar Bot", type="primary"):
            st.session_state.bot_activo = True
        if st.button("Detener Bot", type="secondary"):
            st.session_state.bot_activo = False

    # === Tu código del gráfico (adaptado) ===
    timeframe = st.selectbox("Temporalidad", ["1min", "5min", "15min", "1hour"])
    
    market = crypto.replace("/", "")
    url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={timeframe}&limit=100"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        opens = [float(c["open"]) for c in data.get("data", [])]
        highs = [float(c["high"]) for c in data.get("data", [])]
        lows = [float(c["low"]) for c in data.get("data", [])]
        closes = [float(c["close"]) for c in data.get("data", [])]

        df = pd.DataFrame({
            "open": opens[-100:],
            "high": highs[-100:],
            "low": lows[-100:],
            "close": closes[-100:]
        })

        df["EMA9"] = df["close"].ewm(span=9).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()

        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"]))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA9"], mode='lines', name='EMA 9', line=dict(color='lime')))
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA21"], mode='lines', name='EMA 21', line=dict(color='red')))

        fig.update_layout(height=650, title=f"{crypto} - {timeframe}")
        st.plotly_chart(fig, use_container_width=True)

        precio = closes[-1]
        ema9 = round(df["EMA9"].iloc[-1], 4)
        ema21 = round(df["EMA21"].iloc[-1], 4)

        if ema9 > ema21:
            st.success("🟢 SEÑAL DE COMPRA")
        else:
            st.error("🔴 SEÑAL DE VENTA")

    except Exception as e:
        st.error(f"Error: {e}")

elif pagina == "⚙️ Settings":
    st.title("⚙️ Configuración")
    st.write("Aquí pondremos API Keys, gestión de riesgo, etc.")

elif pagina == "🧠 AI Analytics":
    st.title("🧠 AI Analytics")
    st.write("Backtesting, predicciones y análisis IA.")
