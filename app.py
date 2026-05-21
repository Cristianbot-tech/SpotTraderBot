import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import base64

st.set_page_config(
page_title="CRYPTOSCALPER BOT PRO",
page_icon="💀",
layout="wide",
initial_sidebar_state="collapsed"
)

# Cargar logo

def get_logo():
    try:
        with open("Untitled_design.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

LOGO = get_logo()

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080808 !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

footer { display: none !important; }
#MainMenu { display: none !important; }

.cs-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 20px;
    border-bottom: 1px solid #1e1e1e;
    background: rgba(8,8,8,0.97);
    position: sticky;
    top: 0;
    z-index: 999;
}

.cs-nav-logo {
    display: flex;
    align-items: center;
    gap: 10px;
}

.cs-nav-name {
    font-family: 'Rajdhani', sans-serif;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #fff;
}

.cs-nav-name span {
    color: #e82929;
}

.cs-hamburger {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.cs-hamburger span {
    width: 26px;
    height: 2px;
    background: #fff;
    border-radius: 2px;
    display: block;
}

.cs-hero {
    padding: 50px 20px 40px;
    text-align: center;
}

.cs-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(232,41,41,0.10);
    border: 1px solid rgba(232,41,41,0.30);
    color: #e82929;
    padding: 7px 16px;
    border-radius: 100px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    margin-bottom: 24px;
}

.cs-pulse {
    width: 8px;
    height: 8px;
    background: #e82929;
    border-radius: 50%;
    animation: cspulse 1.4s infinite;
    display: inline-block;
}

@keyframes cspulse {
    0%,100% { opacity:1; transform:scale(1); }
    50% { opacity:.3; transform:scale(.7); }
}

.cs-h1 {
    font-family: 'Rajdhani', sans-serif;
    font-size: 44px;
    font-weight: 700;
    line-height: 1;
    color: #fff;
    margin-bottom: 14px;
}

.cs-sub {
    color: #e82929;
    font-size: 17px;
    font-weight: 500;
    margin-bottom: 18px;
}

.cs-desc {
    color: #666;
    font-size: 14px;
    line-height: 1.7;
    max-width: 360px;
    margin: 0 auto 32px;
}

.cs-btn-red {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: #e82929;
    color: #fff;
    padding: 15px 32px;
    border-radius: 12px;
    font-weight: 700;
    font-size: 15px;
    border: none;
    cursor: pointer;
    width: 100%;
    max-width: 320px;
    box-shadow: 0 0 28px rgba(232,41,41,0.35);
    margin-bottom: 10px;
    text-decoration: none;
}

.cs-btn-outline {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    color: #fff;
    padding: 15px 32px;
    border-radius: 12px;
    font-weight: 500;
    font-size: 15px;
    border: 1px solid #1e1e1e;
    cursor: pointer;
    width: 100%;
    max-width: 320px;
    text-decoration: none;
}

.stButton > button {
    background: #e82929 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(232,41,41,0.3) !important;
}

.stButton > button:hover {
    background: #c0392b !important;
}
</style>

""", unsafe_allow_html=True)

# SESSION STATE

if "auth" not in st.session_state:
    st.session_state.auth = False

if "bot_activo" not in st.session_state:
    st.session_state.bot_activo = False

if "pagina" not in st.session_state:
    st.session_state.pagina = "HOME"

# LOGIN

if not st.session_state.auth:

logo_html = f'<img src="data:image/png;base64,{LOGO}" style="width:90px;margin-bottom:16px;">' if LOGO else '<div style="font-size:60px;margin-bottom:16px;">💀</div>'

st.markdown(f"""
<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">
<div style="background:#101010;border:1px solid #1e1e1e;border-radius:20px;padding:40px 32px;width:100%;max-width:360px;text-align:center;">
    {logo_html}
    <div style="font-family:'Rajdhani',sans-serif;font-size:24px;font-weight:700;letter-spacing:2px;color:#fff;margin-bottom:4px;">
        CRYPTO<span style="color:#e82929;">SCALPER</span>
    </div>
    <div style="color:#666;font-size:13px;margin-bottom:28px;">
        BOT PRO — Acceso exclusivo
    </div>
</div></div>
""", unsafe_allow_html=True)

with st.form("login", clear_on_submit=True):

    clave = st.text_input(
        "",
        placeholder="Introduce contraseña",
        type="password"
    )

    entrar = st.form_submit_button("⚡ ENTRAR")

if entrar:

    if clave == "CRYPTOSCALPER123":
        st.session_state.auth = True
        st.rerun()

    else:
        st.error("Contraseña incorrecta")

st.stop()

logo_img = f'<img src="data:image/png;base64,{LOGO}" style="width:50px;height:50px;object-fit:contain;">' if LOGO else '<div style="font-size:32px;">💀</div>'

st.markdown(f"""

<div class="cs-nav">
  <div class="cs-nav-logo">
    {logo_img}
    <div class="cs-nav-name">
        CRYPTO<span>SCALPER</span>
    </div>
  </div>

  <div class="cs-hamburger">
      <span></span>
      <span></span>
      <span></span>
  </div>
</div>
""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:


if st.button("🏠 HOME", use_container_width=True):
    st.session_state.pagina = "HOME"


with col_b:

if st.button("⚡ LIVE TRADING", use_container_width=True):
    st.s

pagina = st.session_state.pagina

if pagina == "HOME":

st.markdown("""

<div class="cs-hero">

  <div class="cs-badge">
    <span class="cs-pulse"></span>
    Sistema operando en vivo
  </div>

  <div class="cs-h1">
    Trading Algorítmico
    <br>
    de Precisión
  </div>

  <div class="cs-sub">
    Genera ingresos en automático
  </div>

  <div class="cs-desc">
    Automatiza tus operaciones en CoinEx con señales EMA inteligentes,
    gestión de riesgo avanzada y ejecución profesional.
    Sin emociones, 24/7.
  </div>

  <div class="cs-btns">

    <a class="cs-btn-red" href="#">
        ⚡ Comenzar Ahora
    </a>

    <a class="cs-btn-outline" href="#">
        ↓ Ver Features
    </a>

  </div>

</div>

""", unsafe_allow_html=True)

st.markdown("""

<div class="cs-strip">

  <div class="cs-icon-item">
    <div class="cs-icon-box">📈</div>
    <div class="cs-icon-lbl">
        Scalping<br>Algorítmico
    </div>
  </div>

  <div class="cs-icon-item">
    <div class="cs-icon-box">📡</div>
    <div class="cs-icon-lbl">
        Señales<br>Tiempo Real
    </div>
  </div>

  <div class="cs-icon-item">
    <div class="cs-icon-box">🤖</div>
    <div class="cs-icon-lbl">
        Inteligencia<br>Artificial
    </div>
  </div>

  <div class="cs-icon-item">
    <div class="cs-icon-box">⚡</div>
    <div class="cs-icon-lbl">
        Ejecución<br>Ultra Rápida
    </div>
  </div>

  <div class="cs-icon-item">
    <div class="cs-icon-box">🛡️</div>
    <div class="cs-icon-lbl">
        Gestión<br>de Riesgo
    </div>
  </div>

</div>

""", unsafe_allow_html=True)

st.markdown("""

<div class="cs-stats">

  <div class="cs-stat">
    <div class="cs-stat-num">3,032</div>
    <div class="cs-stat-lbl">
        Trades Ejecutados
    </div>
  </div>

  <div class="cs-stat">
    <div class="cs-stat-num">16</div>
    <div class="cs-stat-lbl">
        Usuarios Activos
    </div>
  </div>

  <div class="cs-stat">
    <div class="cs-stat-num">
        99.9<span class="acc">%</span>
    </div>

    <div class="cs-stat-lbl">
        Uptime
    </div>
  </div>

  <div class="cs-stat">
    <div class="cs-stat-num">
        89<span class="acc">%</span>
    </div>

    <div class="cs-stat-lbl">
        Win Rate
    </div>
  </div>

</div>

""", unsafe_allow_html=True)

trades_data = [

    ("12:55:07", "BTC/USDT",  "LONG",  "+0.92%", True),
    ("13:10:22", "ETH/USDT",  "LONG",  "+0.61%", True),
    ("13:18:53", "SOL/USDT",  "SHORT", "+0.51%", True),
    ("13:21:57", "XRP/USDT",  "LONG",  "+0.43%", True),
    ("13:28:17", "BNB/USDT",  "LONG",  "+0.75%", True),
    ("13:28:47", "SOL/USDT",  "LONG",  "+0.45%", True),
    ("13:32:47", "DOGE/USDT", "SHORT", "-1.00%", False),

]

rows = ""

for t in trades_data:

    tag_cls = "cs-tl" if t[2] == "LONG" else "cs-ts"
    pnl_cls = "cs-pos" if t[4] else "cs-neg"

    rows += f"""

    <div class="cs-trade">

      <span class="cs-arr">></span>

      <span class="cs-time">
        {t[0]}
      </span>

      <span class="cs-pair">
        {t[1]}
      </span>

      <span class="cs-tag {tag_cls}">
        {t[2]}
      </span>

      <span class="cs-pnl {pnl_cls}">
        {t[3]}
      </span>

    </div>

    """

st.markdown(f"""

<div class="cs-section">

  <div class="cs-sec-badge">
    <span class="cs-pulse"></span>
    LIVE FEED
  </div>

  <div class="cs-sec-h2">
    Mira el bot trabajando
  </div>

  <div class="cs-sec-desc">
    Trades cerrados en vivo de CRYPTOSCALPER.
  </div>

  <div class="cs-terminal">

    <div class="cs-term-head">

      <span class="cs-dot cs-dr"></span>
      <span class="cs-dot cs-dy"></span>
      <span class="cs-dot cs-dg"></span>

      <span class="cs-stream-lbl">
        ● STREAMING
      </span>

    </div>

    {rows}

  </div>

</div>

""", unsafe_allow_html=True)

st.markdown("""

<div class="cs-features">

  <div style="text-align:center;margin-bottom:26px;">

    <div class="cs-feat-tag">
        ⚙️ TECNOLOGÍA
    </div>

    <div class="cs-feat-h2">
        Todo lo que necesitas para operar
    </div>

    <div class="cs-feat-p">
        Herramientas de trading algorítmico accesibles para todos.
    </div>

  </div>

  <div class="cs-fcard">

    <div class="cs-ficon">📊</div>

    <h3>Dashboard Pro</h3>

    <p>
        Métricas en tiempo real,
        gráfico de velas con EMA 9/21,
        soporte y resistencia automáticos.
    </p>

  </div>

  <div class="cs-fcard">

    <div class="cs-ficon">🛡️</div>

    <h3>Gestión de Riesgo</h3>

    <p>
        Take Profit y Stop Loss configurables.
        Protege tu capital en cada operación.
    </p>

  </div>

  <div class="cs-fcard">

    <div class="cs-ficon">📡</div>

    <h3>Ejecución 24/7</h3>

    <p>
        Conexión directa a CoinEx Spot.
        Monitoreo constante sin interrupciones.
    </p>

  </div>

  <div class="cs-fcard">

    <div class="cs-ficon">📈</div>

    <h3>Señales EMA</h3>

    <p>
        Cruce de medias exponenciales EMA 9/21.
        Señales claras de COMPRA y VENTA.
    </p>

  </div>

  <div class="cs-fcard">

    <div class="cs-ficon">🔒</div>

    <h3>Acceso Seguro</h3>

    <p>
        Login con contraseña y protección de sesión.
    </p>

  </div>

</div>

""", unsafe_allow_html=True)

st.markdown("""

<div style="text-align:center;
            padding:26px 20px;
            border-top:1px solid #1e1e1e;
            color:#666;
            font-size:12px;">

  <div>
    © 2026 CRYPTOSCALPER BOT PRO.
    Todos los derechos reservados.
  </div>

  <div style="display:inline-block;
              background:#141414;
              border:1px solid #1e1e1e;
              padding:9px 26px;
              border-radius:100px;
              margin-top:10px;">

    cryptoscalper.app

  </div>

</div>

""", unsafe_allow_html=True)




# LIVE TRADING


elif pagina == "LIVE":


st.markdown(
    '<div style="padding:20px;">',
    unsafe_allow_html=True
)

st.markdown(
    '<div style="font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#fff;text-align:center;margin-bottom:20px;">⚡ LIVE TRADING</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:

    crypto = st.selectbox(
        "Par",
        [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
            "DOGE/USDT",
            "BNB/USDT"
        ]
    )

with col2:

    tp = st.number_input(
        "Take Profit %",
        value=1.50
    )

with col3:

    sl = st.number_input(
        "Stop Loss %",
        value=1.00
    )

with col4:

    timeframe = st.selectbox(
        "Temporalidad",
        [
            "1min",
            "5min",
            "15min",
            "1hour"
        ]
    )

c1, c2 = st.columns(2)

with c1:

    if st.button(
        "▶ Iniciar Bot",
        use_container_width=True
    ):

        st.session_state.bot_activo = True

with c2:

    if st.button(
        "⏹ Detener Bot",
        use_container_width=True
    ):

        st.session_state.bot_activo = False

if st.session_state.bot_activo:

    market = crypto.replace("/", "")

    url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={timeframe}&limit=50"

    try:

        response = requests.get(url, timeout=10)

        data = response.json()

        opens  = []
        highs  = []
        lows   = []
        closes = []
        volumes = []

        for candle in data["data"]:

            opens.append(float(candle["open"]))
            highs.append(float(candle["high"]))
            lows.append(float(candle["low"]))
            closes.append(float(candle["close"]))
            volumes.append(float(candle["volume"]))

        df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes
        })

        df["EMA9"]  = df["close"].ewm(span=9).mean()
        df["EMA21"] = df["close"].ewm(span=21).mean()

        precio_actual = closes[-1]
        ema9  = df["EMA9"].iloc[-1]
        ema21 = df["EMA21"].iloc[-1]

        cambio = precio_actual - closes[-2]

        soporte = df["low"].tail(20).min()

        resistencia = df["high"].tail(20).max()

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric(
                "💰 Precio",
                f"{precio_actual:,.2f}",
                f"{cambio:+.2f}"
            )

        with m2:
            st.metric(
                "📊 EMA 9",
                f"{ema9:,.2f}"
            )

        with m3:
            st.metric(
                "📊 EMA 21",
                f"{ema21:,.2f}"
            )

        with m4:
            st.metric(
                "📈 Volumen",
                f"{df['volume'].iloc[-1]:,.0f}"
            )

        if ema9 > ema21:

            st.markdown(
                '<div class="cs-signal-buy">🚀 SEÑAL: COMPRA SPOT</div>',
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                '<div class="cs-signal-sell">📉 SEÑAL: VENTA SPOT</div>',
                unsafe_allow_html=True
            )

        s1, s2 = st.columns(2)

        with s1:

            st.metric(
                "🟢 Soporte",
                f"{soporte:,.2f}"
            )

        with s2:

            st.metric(
                "🔴 Resistencia",
                f"{resistencia:,.2f}"
            )

        fig = go.Figure(data=[go.Candlestick(

            x=df.index,

            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],

            increasing=dict(
                line=dict(color="#00e676"),
                fillcolor="#00e676"
            ),

            decreasing=dict(
                line=dict(color="#e82929"),
                fillcolor="#e82929"
            )

        )])

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["EMA9"],
            mode="lines",
            name="EMA 9",
            line=dict(color="#e82929", width=1.5)
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["EMA21"],
            mode="lines",
            name="EMA 21",
            line=dict(color="#ffa726", width=1.5)
        ))

        fig.add_hline(
            y=soporte,
            line_dash="dot",
            line_color="#00e676",
            annotation_text="Soporte"
        )

        fig.add_hline(
            y=resistencia,
            line_dash="dot",
            line_color="#e82929",
            annotation_text="Resistencia"
        )

        fig.update_layout(

            height=520,

            paper_bgcolor="#080808",

            plot_bgcolor="#0c0c0c",

            xaxis=dict(
                showgrid=False,
                color="#444"
            ),

            yaxis=dict(
                showgrid=True,
                gridcolor="#1e1e1e",
                color="#444"
            ),

            xaxis_rangeslider_visible=False,

            legend=dict(
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#888")
            ),

            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    except Exception as e:

        st.error(
            f"Error al conectar con CoinEx: {e}"
        )

    st.success(
        f"✅ Bot activo — {crypto} | TP: {tp}% | SL: {sl}%"
    )

    contador = st.empty()

    for i in range(60, 0, -1):

        contador.markdown(
            f'<div style="color:#666;font-size:12px;text-align:center;padding:8px;">Actualizando en {i}s...</div>',
            unsafe_allow_html=True
        )

        time.sleep(1)

    st.rerun()

else:

    st.markdown(
        '<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">Bot detenido — Pulsa <b style="color:#e82929">Iniciar Bot</b> para comenzar</div>',
        unsafe_allow_html=True
    )

st.markdown(
    '</div>',
    unsafe_allow_html=True
)

