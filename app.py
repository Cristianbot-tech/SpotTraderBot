import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CRYPTOSCALPER BOT PRO", layout="wide", page_icon="💀")

# Estilo oscuro tipo trading terminal
st.markdown("""
<style>
    .stApp { background-color: #0a0a0a; color: #e0e0e0; }
    .stButton>button { width: 100%; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

# Login
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 CRYPTOSCALPER BOT PRO")
    with st.form("login"):
        clave = st.text_input("Contraseña", type="password")
        if st.form_submit_button("ENTRAR"):
            if clave == "CRYPTOSCALPER123":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# Sidebar
st.sidebar.title("💀 CRYPTOSCALPER BOT PRO")
pagina = st.sidebar.radio("Menú", ["🏠 Home", "⚡ Live Trading"])

if pagina == "🏠 Home":
    st.title("🏠 Home")
    st.image("logo.png", width=400)
    st.success("Página de Presentación")

else:
    # ====================== LIVE TRADING ======================
    st.title("⚡ LIVE TRADING")

    # Controles superiores
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1.2, 1.2])

    with col1:
        crypto = st.selectbox("Par", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT"], key="par_live")

    with col2:
        timeframe = st.selectbox("Temporalidad", ["1min", "5min", "15min", "1hour"], index=1)

    with col3:
        tp = st.number_input("TP %", value=1.50, step=0.1)

    with col4:
        sl = st.number_input("SL %", value=1.00, step=0.1)

    with col5:
        if "bot_activo" not in st.session_state:
            st.session_state.bot_activo = False
        if st.button("▶ Iniciar Bot", type="primary"):
            st.session_state.bot_activo = True
        if st.button("⛔ Detener Bot", type="secondary"):
            st.session_state.bot_activo = False

    # Layout principal: Gráfico + Panel de Operaciones
    main_col, side_col = st.columns([3.5, 1.2])

    with main_col:
        # Gráfico
        market = crypto.replace("/", "")
        url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={timeframe}&limit=120"

        try:
            response = requests.get(url)
            data = response.json().get("data", [])

            df = pd.DataFrame(data, columns=["time", "open", "close", "high", "low", "volume"])
            df = df.astype(float).tail(100)

            df["EMA9"] = df["close"].ewm(span=9).mean()
            df["EMA21"] = df["close"].ewm(span=21).mean()

            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df["open"], high=df["high"], 
                                        low=df["low"], close=df["close"], name="Precio"))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA9"], name="EMA 9", line=dict(color="#00ff00")))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA21"], name="EMA 21", line=dict(color="#ff0000")))

            fig.update_layout(
                height=620,
                template="plotly_dark",
                xaxis_rangeslider_visible=False,
                margin=dict(l=10, r=10, t=30, b=10),
                legend=dict(x=0.01, y=0.98)
            )
            st.plotly_chart(fig, use_container_width=True)

            # Volumen debajo del gráfico
            st.subheader("Volumen")
            st.bar_chart(df["volume"], use_container_width=True)

        except Exception as e:
            st.error(f"Error al cargar gráfico: {e}")

    # ==================== PANEL DERECHO (Operaciones) ====================
    with side_col:
        st.subheader("Operaciones")
        
        precio_actual = df["close"].iloc[-1] if 'df' in locals() else 0
        st.metric("Precio Actual", f"{precio_actual:.2f}")

        st.divider()
        
        if st.button("🟢 COMPRA SPOT", type="primary", use_container_width=True):
            st.success(f"✅ Orden de COMPRA enviada en {crypto}")
        
        if st.button("🔴 VENTA SPOT", type="secondary", use_container_width=True):
            st.error(f"✅ Orden de VENTA enviada en {crypto}")

        st.divider()
        
        st.write("**Take Profit**")
        st.write(f"{tp}% → ${precio_actual * (1 + tp/100):.2f}")
        
        st.write("**Stop Loss**")
        st.write(f"{sl}% → ${precio_actual * (1 - sl/100):.2f}")

        st.divider()
        st.info("**Estado del Bot:** " + ("🟢 Activo" if st.session_state.bot_activo else "🔴 Detenido"))
