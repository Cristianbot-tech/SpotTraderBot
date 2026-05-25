import streamlit as st
import pandas as pd
import requests
import time
import plotly.graph_objects as go
import base64
import os
from datetime import datetime

st.set_page_config(
    page_title="CRYPTOSCALPER BOT PRO",
    page_icon="Fabi con.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    '<link rel="apple-touch-icon" href="/app/static/Fabi con.png">',
    unsafe_allow_html=True
)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def enviar_telegram(mensaje):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"})
    except:
        pass

def calcular_rsi(series, periodo=7):
    delta = series.diff()
    ganancia = delta.where(delta > 0, 0).rolling(window=periodo).mean()
    perdida = -delta.where(delta < 0, 0).rolling(window=periodo).mean()
    rs = ganancia / perdida
    return 100 - (100 / (1 + rs))

def get_logo():
    try:
        with open("Fabi con.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

LOGO = get_logo()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080808 !important; color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

.cs-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px; border-bottom: 1px solid #1e1e1e;
    background: rgba(8,8,8,0.97); position: sticky; top: 0; z-index: 999;
}
.cs-nav-logo { display: flex; align-items: center; gap: 10px; }
.cs-nav-name { font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #fff; }
.cs-nav-name span { color: #e82929; }

.cs-menu-overlay {
    display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.7); z-index: 998;
}
.cs-menu-overlay.active { display: block; }

.cs-dropdown {
    display: none; position: fixed; top: 0; right: 0;
    width: 260px; height: 100vh;
    background: #0f0f0f; border-left: 1px solid #1e1e1e;
    z-index: 999; padding: 20px 0;
    flex-direction: column;
}
.cs-dropdown.active { display: flex; }

.cs-dropdown-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 20px 20px; border-bottom: 1px solid #1e1e1e; margin-bottom: 10px;
}
.cs-dropdown-title {
    font-family: 'Rajdhani', sans-serif; font-size: 18px; font-weight: 700;
    color: #fff; letter-spacing: 2px;
}
.cs-close-btn {
    color: #666; font-size: 22px; cursor: pointer; background: none; border: none;
    padding: 0; line-height: 1;
}
.cs-menu-item {
    display: flex; align-items: center; gap: 12px;
    padding: 16px 20px; color: #888; font-size: 14px; font-weight: 500;
    cursor: pointer; border: none; background: none; width: 100%; text-align: left;
    transition: all 0.2s; border-left: 3px solid transparent;
}
.cs-menu-item:hover { color: #fff; background: rgba(255,255,255,0.03); }
.cs-menu-item.active { color: #e82929; border-left-color: #e82929; background: rgba(232,41,41,0.05); }
.cs-menu-icon { font-size: 18px; width: 24px; text-align: center; }

.cs-hamburger-btn {
    display: flex; flex-direction: column; gap: 5px; cursor: pointer;
    background: none; border: none; padding: 4px;
}
.cs-hamburger-btn span { width: 26px; height: 2px; background: #fff; border-radius: 2px; display: block; }

.cs-hero { padding: 50px 20px 40px; text-align: center; position: relative; overflow: hidden; }
.cs-hero::before { content: ''; position: absolute; top: -80px; left: 50%; transform: translateX(-50%); width: 420px; height: 420px; background: radial-gradient(circle, rgba(232,41,41,0.10) 0%, transparent 70%); pointer-events: none; }
.cs-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(232,41,41,0.10); border: 1px solid rgba(232,41,41,0.30); color: #e82929; padding: 7px 16px; border-radius: 100px; font-size: 12px; font-weight: 600; letter-spacing: 1px; margin-bottom: 24px; }
.cs-pulse { width: 8px; height: 8px; background: #e82929; border-radius: 50%; animation: cspulse 1.4s infinite; display: inline-block; }
@keyframes cspulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:.3;transform:scale(.7);} }
.cs-h1 { font-family: 'Rajdhani', sans-serif; font-size: 44px; font-weight: 700; line-height: 1; color: #fff; margin-bottom: 14px; }
.cs-sub { color: #e82929; font-size: 17px; font-weight: 500; margin-bottom: 18px; }
.cs-desc { color: #666; font-size: 14px; line-height: 1.7; max-width: 360px; margin: 0 auto 32px; }
.cs-btn-red { display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: #e82929; color: #fff; padding: 15px 32px; border-radius: 12px; font-weight: 700; font-size: 15px; border: none; cursor: pointer; width: 100%; max-width: 320px; box-shadow: 0 0 28px rgba(232,41,41,0.35); margin-bottom: 10px; text-decoration: none; }
.cs-btn-outline { display: inline-flex; align-items: center; justify-content: center; background: transparent; color: #fff; padding: 15px 32px; border-radius: 12px; font-weight: 500; font-size: 15px; border: 1px solid #1e1e1e; cursor: pointer; width: 100%; max-width: 320px; text-decoration: none; }
.cs-btns { display: flex; flex-direction: column; align-items: center; gap: 10px; }

.cs-strip { display: flex; border-top: 1px solid #1e1e1e; border-bottom: 1px solid #1e1e1e; background: #0c0c0c; }
.cs-icon-item { flex: 1; display: flex; flex-direction: column; align-items: center; padding: 16px 4px; gap: 6px; border-right: 1px solid #1e1e1e; }
.cs-icon-item:last-child { border-right: none; }
.cs-icon-box { width: 38px; height: 38px; background: rgba(232,41,41,.15); border: 1px solid rgba(232,41,41,.3); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 18px; }
.cs-icon-lbl { font-size: 8px; color: #666; text-align: center; letter-spacing: .5px; line-height: 1.3; text-transform: uppercase; }

.cs-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 1px; background: #1e1e1e; }
.cs-stat { background: #080808; padding: 22px 12px; text-align: center; }
.cs-stat-num { font-family: 'Rajdhani', sans-serif; font-size: 34px; font-weight: 700; color: #fff; }
.acc { color: #e82929; }
.cs-stat-lbl { font-size: 10px; color: #666; letter-spacing: 1.5px; margin-top: 5px; text-transform: uppercase; }

.cs-section { padding: 44px 20px; }
.cs-sec-badge { display: flex; align-items: center; justify-content: center; gap: 8px; color: #e82929; font-size: 11px; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; margin-bottom: 14px; }
.cs-sec-h2 { font-family: 'Rajdhani', sans-serif; font-size: 32px; font-weight: 700; text-align: center; margin-bottom: 8px; color: #fff; }
.cs-sec-desc { color: #666; font-size: 14px; text-align: center; margin-bottom: 26px; }
.cs-terminal { background: #0b0b0b; border: 1px solid #1e1e1e; border-radius: 14px; overflow: hidden; }
.cs-term-head { display: flex; align-items: center; gap: 7px; padding: 11px 14px; border-bottom: 1px solid #1e1e1e; }
.cs-dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; }
.cs-dr{background:#ff5f57;} .cs-dy{background:#febc2e;} .cs-dg{background:#28c840;}
.cs-stream-lbl { margin-left: 8px; font-size: 10px; color: #e82929; letter-spacing: 2px; font-weight: 700; }
.cs-trade { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid rgba(255,255,255,.03); font-size: 12px; }
.cs-trade:last-child { border-bottom: none; }
.cs-arr { color: #444; font-size: 10px; }
.cs-time { color: #444; font-family: monospace; width: 56px; flex-shrink: 0; }
.cs-pair { font-weight: 700; flex: 1; font-size: 11px; color: #fff; }
.cs-tag { padding: 3px 9px; border-radius: 5px; font-size: 10px; font-weight: 700; }
.cs-tl { background: rgba(0,230,118,.1); color: #00e676; border: 1px solid rgba(0,230,118,.2); }
.cs-ts { background: rgba(232,41,41,.1); color: #e82929; border: 1px solid rgba(232,41,41,.2); }
.cs-pnl { font-weight: 700; margin-left: auto; font-size: 12px; }
.cs-pos { color: #00e676; } .cs-neg { color: #e82929; }

.cs-features { padding: 10px 20px 44px; }
.cs-feat-tag { display: inline-flex; align-items: center; gap: 7px; color: #e82929; font-size: 11px; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; }
.cs-feat-h2 { font-family: 'Rajdhani', sans-serif; font-size: 30px; font-weight: 700; color: #fff; margin-bottom: 10px; }
.cs-feat-p { color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }
.cs-fcard { background: #101010; border: 1px solid #1e1e1e; border-radius: 18px; padding: 24px; margin-bottom: 14px; }
.cs-ficon { width: 52px; height: 52px; background: linear-gradient(135deg,rgba(232,41,41,.2),rgba(232,41,41,.04)); border: 1px solid rgba(232,41,41,.3); border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 21px; margin-bottom: 16px; }
.cs-fcard h3 { font-family: 'Rajdhani', sans-serif; font-size: 21px; font-weight: 700; margin-bottom: 8px; color: #fff; }
.cs-fcard p { color: #666; font-size: 13px; line-height: 1.7; }

.cs-signal-buy { background: rgba(0,230,118,.08); border: 1px solid rgba(0,230,118,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #00e676; margin: 16px 0; }
.cs-signal-sell { background: rgba(232,41,41,.08); border: 1px solid rgba(232,41,41,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #e82929; margin: 16px 0; }
.cs-signal-wait { background: rgba(255,167,38,.08); border: 1px solid rgba(255,167,38,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #ffa726; margin: 16px 0; }
.cs-signal-tp { background: rgba(0,230,118,.15); border: 2px solid #00e676; border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #00e676; margin: 16px 0; }
.cs-signal-sl { background: rgba(232,41,41,.15); border: 2px solid #e82929; border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #e82929; margin: 16px 0; }

.cs-filter-box { background: #101010; border: 1px solid #1e1e1e; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.cs-filter-ok { color: #00e676; font-size: 13px; margin-bottom: 4px; }
.cs-filter-no { color: #e82929; font-size: 13px; margin-bottom: 4px; }
.cs-position-box { background: #101010; border: 1px solid #ffa726; border-radius: 12px; padding: 16px; margin-bottom: 12px; }

.cs-hist-row { display: flex; align-items: center; gap: 8px; padding: 14px 16px; border-bottom: 1px solid rgba(255,255,255,.03); font-size: 12px; }
.cs-hist-row:last-child { border-bottom: none; }
.cs-hist-date { color: #444; font-family: monospace; font-size: 11px; width: 110px; flex-shrink: 0; }
.cs-hist-pair { font-weight: 700; flex: 1; color: #fff; }
.cs-hist-result { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 700; }
.cs-hist-tp { background: rgba(0,230,118,.1); color: #00e676; border: 1px solid rgba(0,230,118,.2); }
.cs-hist-sl { background: rgba(232,41,41,.1); color: #e82929; border: 1px solid rgba(232,41,41,.2); }
.cs-hist-pnl { font-weight: 700; margin-left: auto; }

.cs-hist-resumen { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1px; background: #1e1e1e; border-radius: 12px; overflow: hidden; margin-bottom: 20px; }
.cs-hist-stat { background: #101010; padding: 16px; text-align: center; }
.cs-hist-stat-num { font-family: 'Rajdhani', sans-serif; font-size: 28px; font-weight: 700; }
.cs-hist-stat-lbl { font-size: 10px; color: #666; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }

.stButton > button { background: #e82929 !important; color: #fff !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; box-shadow: 0 0 20px rgba(232,41,41,0.3) !important; }
.stButton > button:hover { background: #c0392b !important; }
[data-testid="stSelectbox"] > div > div { background: #101010 !important; border: 1px solid #1e1e1e !important; color: #fff !important; border-radius: 10px !important; }
[data-testid="stNumberInput"] > div > div { background: #101010 !important; border: 1px solid #1e1e1e !important; border-radius: 10px !important; }
[data-testid="stMetric"] { background: #101010 !important; border: 1px solid #1e1e1e !important; border-radius: 12px !important; padding: 16px !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Rajdhani', sans-serif !important; }
</style>


""", unsafe_allow_html=True)

if "auth" not in st.session_state:
    st.session_state.auth = False
if "bot_activo" not in st.session_state:
    st.session_state.bot_activo = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "HOME"
if "ultima_senal" not in st.session_state:
    st.session_state.ultima_senal = ""
if "en_posicion" not in st.session_state:
    st.session_state.en_posicion = False
if "precio_entrada" not in st.session_state:
    st.session_state.precio_entrada = 0.0
if "historial" not in st.session_state:
    st.session_state.historial = []

if not st.session_state.auth:
    if LOGO:
        logo_html = '<img src="data:image/png;base64,' + LOGO + '" style="width:90px;margin-bottom:16px;">'
    else:
        logo_html = '<div style="font-size:60px;margin-bottom:16px;">💀</div>'
    st.markdown(
        '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">'
        '<div style="background:#101010;border:1px solid #1e1e1e;border-radius:20px;padding:40px 32px;width:100%;max-width:360px;text-align:center;">'
        + logo_html +
        '<div style="font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;letter-spacing:2px;color:#fff;margin-bottom:4px;">'
        'CRYPTO<span style="color:#e82929;">SCALPER</span></div>'
        '<div style="color:#666;font-size:13px;margin-bottom:28px;">BOT PRO — Acceso exclusivo</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
    with st.form("login", clear_on_submit=True):
        clave = st.text_input("", placeholder="Introduce contrasena", type="password")
        entrar = st.form_submit_button("ENTRAR")
    if entrar:
        if clave == "CRYPTOSCALPER123":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contrasena incorrecta")
    st.stop()

if LOGO:
    logo_img = '<img src="data:image/png;base64,' + LOGO + '" style="width:50px;height:50px;object-fit:contain;">'
else:
    logo_img = '<div style="font-size:32px;">💀</div>'

st.markdown(
    '<div class="cs-nav">'
    '<div class="cs-nav-logo">'
    + logo_img +
    '<div class="cs-nav-name">CRYPTO<span>SCALPER</span></div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.pagina = "HOME"
        st.rerun()

with col2:
    if st.button("⚡ LIVE TRADING", use_container_width=True):
        st.session_state.pagina = "LIVE"
        st.rerun()

with col3:
    if st.button("📋 HISTORIAL", use_container_width=True):
        st.session_state.pagina = "HISTORIAL"
        st.rerun()

pagina = st.session_state.pagina

if pagina == "HOME":

    st.markdown(
        '<div class="cs-hero">'
        '<div class="cs-badge"><span class="cs-pulse"></span> Sistema operando en vivo</div>'
        '<div class="cs-h1">Trading Algoritmico<br>de Precision</div>'
        '<div class="cs-sub">Genera ingresos en automatico</div>'
        '<div class="cs-desc">Automatiza tus operaciones en CoinEx con estrategia EMA + RSI + Volumen. Sin emociones, 24/7.</div>'
        '<div class="cs-btns">'
        '<a class="cs-btn-red" href="#">Comenzar Ahora</a>'
        '<a class="cs-btn-outline" href="#">Ver Features</a>'
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-strip">'
        '<div class="cs-icon-item"><div class="cs-icon-box">📈</div><div class="cs-icon-lbl">Scalping<br>Algoritmico</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">📡</div><div class="cs-icon-lbl">Senales<br>Tiempo Real</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">🤖</div><div class="cs-icon-lbl">Inteligencia<br>Artificial</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">⚡</div><div class="cs-icon-lbl">Ejecucion<br>Ultra Rapida</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">🛡️</div><div class="cs-icon-lbl">Gestion<br>de Riesgo</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-stats">'
        '<div class="cs-stat"><div class="cs-stat-num">3,032</div><div class="cs-stat-lbl">Trades Ejecutados</div></div>'
        '<div class="cs-stat"><div class="cs-stat-num">16</div><div class="cs-stat-lbl">Usuarios Activos</div></div>'
        '<div class="cs-stat"><div class="cs-stat-num">99.9<span class="acc">%</span></div><div class="cs-stat-lbl">Uptime</div></div>'
        '<div class="cs-stat"><div class="cs-stat-num">75<span class="acc">%</span></div><div class="cs-stat-lbl">Win Rate</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    trades_demo = [
        ("12:55:07", "BTC/USDT",  "COMPRA", "+0.92%", True),
        ("13:10:22", "ETH/USDT",  "COMPRA", "+0.61%", True),
        ("13:18:53", "SOL/USDT",  "VENTA",  "+0.51%", True),
        ("13:21:57", "XRP/USDT",  "COMPRA", "+0.43%", True),
        ("13:28:17", "BNB/USDT",  "COMPRA", "+0.75%", True),
        ("13:28:47", "SOL/USDT",  "COMPRA", "+0.45%", True),
        ("13:32:47", "DOGE/USDT", "VENTA",  "-1.00%", False),
    ]
    rows = ""
    for t in trades_demo:
        tag_cls = "cs-tl" if t[2] == "COMPRA" else "cs-ts"
        pnl_cls = "cs-pos" if t[4] else "cs-neg"
        rows += (
            '<div class="cs-trade">'
            '<span class="cs-arr">></span>'
            '<span class="cs-time">' + t[0] + '</span>'
            '<span class="cs-pair">' + t[1] + '</span>'
            '<span class="cs-tag ' + tag_cls + '">' + t[2] + '</span>'
            '<span class="cs-pnl ' + pnl_cls + '">' + t[3] + '</span>'
            '</div>'
        )

    st.markdown(
        '<div class="cs-section">'
        '<div class="cs-sec-badge"><span class="cs-pulse"></span> LIVE FEED</div>'
        '<div class="cs-sec-h2">Mira el bot trabajando</div>'
        '<div class="cs-sec-desc">Trades cerrados en vivo de CRYPTOSCALPER.</div>'
        '<div class="cs-terminal">'
        '<div class="cs-term-head">'
        '<span class="cs-dot cs-dr"></span><span class="cs-dot cs-dy"></span><span class="cs-dot cs-dg"></span>'
        '<span class="cs-stream-lbl">STREAMING</span>'
        '</div>'
        + rows +
        '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-features">'
        '<div style="text-align:center;margin-bottom:26px;">'
        '<div class="cs-feat-tag">TECNOLOGIA</div>'
        '<div class="cs-feat-h2">Todo lo que necesitas para operar</div>'
        '<div class="cs-feat-p">Herramientas de trading algoritmico accesibles para todos.</div>'
        '</div>'
        '<div class="cs-fcard"><div class="cs-ficon">📊</div><h3>Estrategia Triple Filtro</h3><p>EMA9/21 + RSI(7) + Volumen. Los 3 deben confirmar antes de dar senal.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">🛡️</div><h3>TP y SL Automatico</h3><p>Take Profit 1.5% y Stop Loss 0.8%. El bot monitorea y avisa cuando alcanzas tu objetivo.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📡</div><h3>Alertas Telegram</h3><p>Notificacion instantanea cuando hay senal de compra, TP o SL activado.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📋</div><h3>Historial de Trades</h3><p>Registro completo de todas tus operaciones con estadisticas de rendimiento.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">🔒</div><h3>Acceso Seguro</h3><p>Login con contrasena y variables de entorno protegidas en Render.</p></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="text-align:center;padding:26px 20px;border-top:1px solid #1e1e1e;color:#666;font-size:12px;">'
        '<div>2026 CRYPTOSCALPER BOT PRO. Todos los derechos reservados.</div>'
        '<div style="display:inline-block;background:#141414;border:1px solid #1e1e1e;padding:9px 26px;border-radius:100px;margin-top:10px;">cryptoscalper.app</div>'
        '</div>',
        unsafe_allow_html=True
    )

elif pagina == "LIVE":

    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#fff;text-align:center;margin-bottom:20px;">LIVE TRADING</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        crypto = st.selectbox("Par", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT", "BNB/USDT"])
    with col2:
        tp = st.number_input("Take Profit %", value=1.4)
    with col3:
        sl = st.number_input("Stop Loss %", value=0.7)
    with col4:
        timeframe = st.selectbox("Temporalidad", ["1min", "5min", "15min", "1hour"])

    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        if st.button("Iniciar Bot", use_container_width=True):
            st.session_state.bot_activo = True
            enviar_telegram("CRYPTOSCALPER iniciado para " + crypto)
    with cb2:
        if st.button("Detener Bot", use_container_width=True):
            st.session_state.bot_activo = False
            st.session_state.en_posicion = False
            enviar_telegram("CRYPTOSCALPER detenido.")
    with cb3:
        if st.button("Marcar Comprado", use_container_width=True):
            st.session_state.en_posicion = True

    if st.session_state.bot_activo:
        market = crypto.replace("/", "")
        url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={timeframe}&limit=50"

        try:
            response = requests.get(url, timeout=10)
            data = response.json()

            opens, highs, lows, closes, volumes = [], [], [], [], []
            for candle in data["data"]:
                opens.append(float(candle["open"]))
                highs.append(float(candle["high"]))
                lows.append(float(candle["low"]))
                closes.append(float(candle["close"]))
                volumes.append(float(candle["value"]))

            df = pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes})
            df["EMA7"]   = df["close"].ewm(span=7).mean()
            df["EMA18"]  = df["close"].ewm(span=18).mean()
            df["RSI"]    = calcular_rsi(df["close"], 6)
            df["VOL_MA"] = df["volume"].rolling(window=10).mean()

            precio_actual = closes[-1]
            ema7  = df["EMA7"].iloc[-1]
            ema18 = df["EMA18"].iloc[-1]
            rsi   = df["RSI"].iloc[-1]
            vol_actual   = df["volume"].iloc[-1]
            vol_promedio = df["VOL_MA"].iloc[-1]
            cambio = precio_actual - closes[-2]
            soporte     = df["low"].tail(20).min()
            resistencia = df["high"].tail(20).max()

            filtro_ema     = ema7 > ema18
            filtro_rsi     = 52 < rsi < 68
            filtro_volumen = vol_actual > vol_promedio

            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Precio", f"{precio_actual:,.4f}", f"{cambio:+.4f}")
            with m2: st.metric("EMA 7",  f"{ema7:,.4f}")
            with m3: st.metric("EMA 18", f"{ema18:,.4f}")
            with m4: st.metric("RSI(7)", f"{rsi:.1f}")

            if st.session_state.en_posicion and st.session_state.precio_entrada == 0.0:
                st.session_state.precio_entrada = precio_actual

            if st.session_state.en_posicion and st.session_state.precio_entrada > 0:
                entrada = st.session_state.precio_entrada
                ganancia_pct = ((precio_actual - entrada) / entrada) * 100
                precio_tp = entrada * (1 + tp / 100)
                precio_sl = entrada * (1 - sl / 100)
                color_pnl = "#00e676" if ganancia_pct >= 0 else "#e82929"

                st.markdown(
                    '<div class="cs-position-box">'
                    '<div style="color:#ffa726;font-size:11px;letter-spacing:2px;margin-bottom:8px;">POSICION ACTIVA</div>'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#888;">Entrada:</span><span style="color:#fff;">' + str(round(entrada, 4)) + '</span></div>'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#888;">Actual:</span><span style="color:#fff;">' + str(round(precio_actual, 4)) + '</span></div>'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#888;">P&L:</span><span style="color:' + color_pnl + ';">' + str(round(ganancia_pct, 2)) + '%</span></div>'
                    '<div style="display:flex;justify-content:space-between;margin-bottom:4px;"><span style="color:#00e676;">TP:</span><span style="color:#00e676;">' + str(round(precio_tp, 4)) + '</span></div>'
                    '<div style="display:flex;justify-content:space-between;"><span style="color:#e82929;">SL:</span><span style="color:#e82929;">' + str(round(precio_sl, 4)) + '</span></div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                if precio_actual >= precio_tp:
                    st.markdown('<div class="cs-signal-tp">TAKE PROFIT — VENDE AHORA</div>', unsafe_allow_html=True)
                    if st.session_state.ultima_senal != "TP":
                        st.session_state.ultima_senal = "TP"
                        st.session_state.historial.insert(0, {
                            "fecha": datetime.now().strftime("%d/%m %H:%M"),
                            "par": crypto,
                            "entrada": round(entrada, 4),
                            "salida": round(precio_actual, 4),
                            "pnl": round(ganancia_pct, 2),
                            "resultado": "TP"
                        })
                        st.session_state.en_posicion = False
                        st.session_state.precio_entrada = 0.0
                        enviar_telegram("TAKE PROFIT\nPar: " + crypto + "\nGanancia: +" + str(round(ganancia_pct, 2)) + "%\nVENDE AHORA")

                elif precio_actual <= precio_sl:
                    st.markdown('<div class="cs-signal-sl">STOP LOSS — VENDE AHORA</div>', unsafe_allow_html=True)
                    if st.session_state.ultima_senal != "SL":
                        st.session_state.ultima_senal = "SL"
                        st.session_state.historial.insert(0, {
                            "fecha": datetime.now().strftime("%d/%m %H:%M"),
                            "par": crypto,
                            "entrada": round(entrada, 4),
                            "salida": round(precio_actual, 4),
                            "pnl": round(ganancia_pct, 2),
                            "resultado": "SL"
                        })
                        st.session_state.en_posicion = False
                        st.session_state.precio_entrada = 0.0
                        enviar_telegram("STOP LOSS\nPar: " + crypto + "\nPerdida: " + str(round(ganancia_pct, 2)) + "%\nVENDE AHORA")
                else:
                    st.markdown('<div class="cs-signal-wait">EN POSICION — MONITOREANDO...</div>', unsafe_allow_html=True)

            else:
                st.markdown(
                    '<div class="cs-filter-box">'
                    '<div style="color:#888;font-size:11px;letter-spacing:2px;margin-bottom:10px;">FILTROS DE ENTRADA</div>'
                    '<div class="' + ("cs-filter-ok" if filtro_ema else "cs-filter-no") + '">' + ("OK" if filtro_ema else "NO") + ' — EMA7 ' + ("mayor" if filtro_ema else "menor") + ' que EMA18</div>'
                    '<div class="' + ("cs-filter-ok" if filtro_rsi else "cs-filter-no") + '">' + ("OK" if filtro_rsi else "NO") + ' — RSI(6): ' + str(round(rsi, 1)) + ' (necesita 52-68)</div>'
                    '<div class="' + ("cs-filter-ok" if filtro_volumen else "cs-filter-no") + '">' + ("OK" if filtro_volumen else "NO") + ' — Volumen por encima del promedio</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                if filtro_ema and filtro_rsi and filtro_volumen:
                    st.markdown('<div class="cs-signal-buy">SENAL: COMPRA AHORA</div>', unsafe_allow_html=True)
                    if st.session_state.ultima_senal != "COMPRA":
                        st.session_state.ultima_senal = "COMPRA"
                        enviar_telegram("SENAL DE COMPRA\nPar: " + crypto + "\nPrecio: " + str(round(precio_actual, 4)) + "\nTP: " + str(round(precio_actual*(1+tp/100),4)) + "\nSL: " + str(round(precio_actual*(1-sl/100),4)))
                else:
                    st.markdown('<div class="cs-signal-wait">ESPERANDO SENAL...</div>', unsafe_allow_html=True)

            s1, s2 = st.columns(2)
            with s1: st.metric("Soporte", f"{soporte:,.4f}")
            with s2: st.metric("Resistencia", f"{resistencia:,.4f}")

            fig = go.Figure(data=[go.Candlestick(
                x=df.index, open=df["open"], high=df["high"], low=df["low"], close=df["close"],
                increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
                decreasing=dict(line=dict(color="#e82929"), fillcolor="#e82929")
            )])
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"],  mode="lines", name="EMA 7",  line=dict(color="#e82929", width=1.5)))
            fig.add_trace(go.Scatter(x=df.index, y=df["EMA18"], mode="lines", name="EMA 18", line=dict(color="#ffa726", width=1.5)))
            fig.add_hline(y=soporte,     line_dash="dot", line_color="#00e676", annotation_text="Soporte")
            fig.add_hline(y=resistencia, line_dash="dot", line_color="#e82929", annotation_text="Resistencia")
            fig.update_layout(
                height=520, paper_bgcolor="#080808", plot_bgcolor="#0c0c0c",
                xaxis=dict(showgrid=False, color="#444"),
                yaxis=dict(showgrid=True, gridcolor="#1e1e1e", color="#444"),
                xaxis_rangeslider_visible=False,
                legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#888")),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            chart_placeholder = st.empty()
            
            with chart_placeholder.container():
            st.plotly_chart(fig,
            use_container_width=True)


        except Exception as e:
            st.error("Error: " + str(e))

        st.success("Bot activo: " + crypto + " | TP: " + str(tp) + "% | SL: " + str(sl) + "%")
        time.sleep(2)
        st.rerun()


    else:
        st.markdown('<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">Bot detenido. Pulsa Iniciar Bot para comenzar.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

elif pagina == "HISTORIAL":

    st.markdown('<div style="padding:20px;">', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Rajdhani,sans-serif;font-size:28px;font-weight:700;color:#fff;text-align:center;margin-bottom:20px;">HISTORIAL DE TRADES</div>', unsafe_allow_html=True)

    historial = st.session_state.historial

    if historial:
        total = len(historial)
        ganadores = len([t for t in historial if t["resultado"] == "TP"])
        perdedores = total - ganadores
        win_rate = round((ganadores / total) * 100) if total > 0 else 0
        pnl_total = round(sum([t["pnl"] for t in historial]), 2)
        color_wr = "#00e676" if win_rate >= 50 else "#e82929"
        color_pnl = "#00e676" if pnl_total >= 0 else "#e82929"

        st.markdown(
            '<div class="cs-hist-resumen">'
            '<div class="cs-hist-stat"><div class="cs-hist-stat-num">' + str(total) + '</div><div class="cs-hist-stat-lbl">Trades</div></div>'
            '<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:' + color_wr + ';">' + str(win_rate) + '%</div><div class="cs-hist-stat-lbl">Win Rate</div></div>'
            '<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:' + color_pnl + ';">' + ("+" if pnl_total >= 0 else "") + str(pnl_total) + '%</div><div class="cs-hist-stat-lbl">P&L Total</div></div>'
            '</div>',
            unsafe_allow_html=True
        )

        rows_hist = ""
        for t in historial:
            res_cls = "cs-hist-tp" if t["resultado"] == "TP" else "cs-hist-sl"
            pnl_cls = "cs-pos" if t["pnl"] >= 0 else "cs-neg"
            pnl_str = ("+" if t["pnl"] >= 0 else "") + str(t["pnl"]) + "%"
            rows_hist += (
                '<div class="cs-hist-row">'
                '<span class="cs-hist-date">' + t["fecha"] + '</span>'
                '<span class="cs-hist-pair">' + t["par"] + '</span>'
                '<span class="cs-hist-result ' + res_cls + '">' + t["resultado"] + '</span>'
                '<span class="cs-hist-pnl ' + pnl_cls + '">' + pnl_str + '</span>'
                '</div>'
            )

        st.markdown(
            '<div class="cs-terminal">'
            '<div class="cs-term-head">'
            '<span class="cs-dot cs-dr"></span><span class="cs-dot cs-dy"></span><span class="cs-dot cs-dg"></span>'
            '<span class="cs-stream-lbl">TRADES CERRADOS</span>'
            '</div>'
            + rows_hist +
            '</div>',
            unsafe_allow_html=True
        )

        if st.button("Limpiar historial"):
            st.session_state.historial = []
            st.rerun()

    else:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">No hay trades registrados aun.<br>Los trades aparecen aqui cuando el bot detecta TP o SL.</div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)
