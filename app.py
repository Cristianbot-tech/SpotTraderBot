import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="CRYPTOSCALPER BOT PRO",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── VARIABLES DE ENTORNO ───────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
APP_PASSWORD     = os.environ.get("APP_PASSWORD", "CRYPTOSCALPER123")

# ─── LOGO EMBEBIDO ──────────────────────────────────────────────────────────
LOGO_B64 = "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"

# ─── INIT SESSION STATE ──────────────────────────────────────────────────────
def init_state():
    defaults = {
        "auth": False,
        "bot_activo": False,
        "pagina": "HOME",
        "ultima_senal": "",
        "en_posicion": False,
        "precio_entrada": 0.0,
        "historial": [],
        "capital": 30.0,
        "capital_inicial": 30.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── HELPERS ────────────────────────────────────────────────────────────────
def enviar_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}, timeout=5)
    except Exception:
        pass

def calcular_rsi(series, periodo=6):
    delta    = series.diff()
    ganancia = delta.where(delta > 0, 0).rolling(window=periodo).mean()
    perdida  = -delta.where(delta < 0, 0).rolling(window=periodo).mean()
    rs = ganancia / perdida
    return 100 - (100 / (1 + rs))

# ─── CSS GLOBAL ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background: #080808 !important; color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }
#MainMenu { display: none !important; }

/* NAV */
.cs-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 16px; border-bottom: 1px solid #1e1e1e;
    background: rgba(8,8,8,0.97); position: sticky; top: 0; z-index: 999;
}
.cs-nav-logo { display: flex; align-items: center; gap: 10px; }
.cs-nav-name { font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #fff; }
.cs-nav-name span { color: #e82929; }
.cs-nav-logo img { width: 44px; height: 44px; object-fit: contain; border-radius: 8px; }

/* STATUS BADGE NAV */
.cs-nav-status {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(232,41,41,0.10); border: 1px solid rgba(232,41,41,0.30);
    color: #e82929; padding: 5px 12px; border-radius: 100px; font-size: 11px;
    font-weight: 700; letter-spacing: 1px;
}
.cs-pulse { width: 7px; height: 7px; background: #e82929; border-radius: 50%; animation: cspulse 1.4s infinite; display: inline-block; }
@keyframes cspulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:.3;transform:scale(.7);} }

/* HERO */
.cs-hero { padding: 40px 20px 36px; text-align: center; position: relative; overflow: hidden; }
.cs-hero::before { content: ''; position: absolute; top: -80px; left: 50%; transform: translateX(-50%); width: 420px; height: 420px; background: radial-gradient(circle, rgba(232,41,41,0.10) 0%, transparent 70%); pointer-events: none; }
.cs-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(232,41,41,0.10); border: 1px solid rgba(232,41,41,0.30); color: #e82929; padding: 7px 16px; border-radius: 100px; font-size: 12px; font-weight: 600; letter-spacing: 1px; margin-bottom: 24px; }
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
.cs-feat-tag { color: #e82929; font-size: 11px; letter-spacing: 3px; font-weight: 700; text-transform: uppercase; margin-bottom: 12px; display:block; }
.cs-feat-h2 { font-family: 'Rajdhani', sans-serif; font-size: 30px; font-weight: 700; color: #fff; margin-bottom: 10px; }
.cs-feat-p { color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 24px; }
.cs-fcard { background: #101010; border: 1px solid #1e1e1e; border-radius: 18px; padding: 24px; margin-bottom: 14px; }
.cs-ficon { width: 52px; height: 52px; background: linear-gradient(135deg,rgba(232,41,41,.2),rgba(232,41,41,.04)); border: 1px solid rgba(232,41,41,.3); border-radius: 13px; display: flex; align-items: center; justify-content: center; font-size: 21px; margin-bottom: 16px; }
.cs-fcard h3 { font-family: 'Rajdhani', sans-serif; font-size: 21px; font-weight: 700; margin-bottom: 8px; color: #fff; }
.cs-fcard p { color: #666; font-size: 13px; line-height: 1.7; }

/* SEÑALES */
.cs-signal-buy  { background: rgba(0,230,118,.08); border: 1px solid rgba(0,230,118,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #00e676; margin: 16px 0; }
.cs-signal-sell { background: rgba(232,41,41,.08); border: 1px solid rgba(232,41,41,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #e82929; margin: 16px 0; }
.cs-signal-wait { background: rgba(255,167,38,.08); border: 1px solid rgba(255,167,38,.3); border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #ffa726; margin: 16px 0; }
.cs-signal-tp   { background: rgba(0,230,118,.15); border: 2px solid #00e676; border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #00e676; margin: 16px 0; }
.cs-signal-sl   { background: rgba(232,41,41,.15); border: 2px solid #e82929; border-radius: 12px; padding: 16px; text-align: center; font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #e82929; margin: 16px 0; }

/* MT5 LIVE */
.mt5-quote-bar { background: #111; border-bottom: 1px solid #1e1e1e; padding: 8px 14px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; }
.mt5-symbol { font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #fff; }
.mt5-price-main { font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 600; color: #fff; }
.mt5-price-up   { color: #00e676; }
.mt5-price-dn   { color: #e82929; }
.mt5-quote-item { text-align: center; }
.mt5-quote-lbl  { font-size: 9px; color: #555; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }
.mt5-quote-val  { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ccc; font-weight: 600; }
.mt5-rp-section { border-bottom: 1px solid #1e1e1e; padding: 12px; }
.mt5-rp-title { font-size: 9px; color: #555; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; font-weight: 700; }
.mt5-rp-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.mt5-rp-key { font-size: 10px; color: #666; }
.mt5-rp-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ccc; font-weight: 600; }
.mt5-indicator-bar { height: 6px; background: #1e1e1e; border-radius: 3px; overflow: hidden; margin-top: 4px; margin-bottom: 8px; }
.mt5-indicator-fill { height: 100%; border-radius: 3px; transition: width .3s; }

/* Solo botón BUY (spot — solo compramos) */
.mt5-trade-btn-wrap { padding: 12px; }
.mt5-btn-buy {
    background: linear-gradient(135deg, #00b894, #00e676);
    color: #000; padding: 14px; border-radius: 6px; width: 100%;
    text-align: center; font-family: 'Rajdhani', sans-serif;
    font-size: 18px; font-weight: 700; cursor: pointer; border: none;
}
.mt5-btn-sub { font-size: 9px; font-weight: 400; display: block; opacity: 0.8; }

.mt5-capital-progress { padding: 12px; border-bottom: 1px solid #1e1e1e; }
.mt5-cap-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.mt5-cap-label { font-size: 9px; color: #555; letter-spacing: 1px; text-transform: uppercase; }
.mt5-progress-outer { height: 6px; background: #1e1e1e; border-radius: 3px; overflow: hidden; }
.mt5-progress-inner { height: 100%; border-radius: 3px; transition: width .5s; }

.mt5-terminal { background: #0a0a0a; border-top: 2px solid #1e1e1e; font-family: 'JetBrains Mono', monospace; }
.mt5-term-tabs { display: flex; background: #111; border-bottom: 1px solid #1e1e1e; }
.mt5-term-tab { padding: 8px 16px; font-size: 10px; font-weight: 600; color: #555; letter-spacing: 1px; text-transform: uppercase; cursor: pointer; border-right: 1px solid #1e1e1e; border-bottom: 2px solid transparent; }
.mt5-term-tab.active { color: #e82929; border-bottom: 2px solid #e82929; }
.mt5-term-body { padding: 0; max-height: 180px; overflow-y: auto; }
.mt5-term-row { display: grid; grid-template-columns: 90px 80px 1fr 60px 60px 60px; padding: 7px 12px; border-bottom: 1px solid #141414; font-size: 10px; color: #888; align-items: center; }
.mt5-term-row:hover { background: #141414; }
.mt5-term-header { display: grid; grid-template-columns: 90px 80px 1fr 60px 60px 60px; padding: 5px 12px; background: #0f0f0f; font-size: 9px; color: #444; letter-spacing: 1px; text-transform: uppercase; border-bottom: 1px solid #1e1e1e; position: sticky; top: 0; }

/* HISTORIAL */
.cs-hist-header { background: #0f0f0f; padding: 16px 20px; border-bottom: 1px solid #1e1e1e; display: flex; align-items: center; justify-content: space-between; }
.cs-hist-balance { font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #4da6ff; }
.cs-hist-balance-lbl { font-size: 10px; color: #666; letter-spacing: 1px; text-transform: uppercase; }
.cs-hist-resumen { display: grid; grid-template-columns: 1fr 1fr 1fr; background: #101010; border-bottom: 1px solid #1e1e1e; }
.cs-hist-stat { padding: 14px 12px; text-align: center; border-right: 1px solid #1e1e1e; }
.cs-hist-stat:last-child { border-right: none; }
.cs-hist-stat-num { font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; }
.cs-hist-stat-lbl { font-size: 9px; color: #666; letter-spacing: 1px; text-transform: uppercase; margin-top: 3px; }
.cs-hist-seccion { padding: 12px 16px 6px; background: #0a0a0a; }
.cs-hist-seccion-titulo { font-size: 11px; font-weight: 700; color: #888; letter-spacing: 1px; text-transform: uppercase; }
.cs-hist-trade { background: #0f0f0f; border-bottom: 1px solid #141414; padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; }
.cs-hist-trade:hover { background: #141414; }
.cs-hist-par { font-weight: 700; font-size: 14px; color: #fff; margin-bottom: 3px; }
.cs-hist-tipo { font-size: 12px; font-weight: 600; color: #4da6ff; }
.cs-hist-precios { font-size: 11px; color: #555; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
.cs-hist-ganancia { font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; }
.cs-hist-tag { font-size: 10px; padding: 2px 8px; border-radius: 4px; font-weight: 700; margin-top: 4px; display: inline-block; }

/* Streamlit overrides */
.stButton > button { background: #e82929 !important; color: #fff !important; border: none !important; border-radius: 10px !important; font-weight: 700 !important; box-shadow: 0 0 20px rgba(232,41,41,0.3) !important; }
.stButton > button:hover { background: #c0392b !important; }
[data-testid="stSelectbox"] > div > div { background: #101010 !important; border: 1px solid #1e1e1e !important; color: #fff !important; border-radius: 10px !important; }
[data-testid="stNumberInput"] > div > div { background: #101010 !important; border: 1px solid #1e1e1e !important; border-radius: 10px !important; }
[data-testid="stMetric"] { background: #101010 !important; border: 1px solid #1e1e1e !important; border-radius: 12px !important; padding: 16px !important; }
[data-testid="stMetricValue"] { color: #fff !important; font-family: 'Rajdhani', sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ─── LOGIN ───────────────────────────────────────────────────────────────────
if not st.session_state.auth:
    logo_html = f'<img src="data:image/jpeg;base64,{LOGO_B64}" style="width:110px;margin-bottom:16px;border-radius:12px;">'
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
        clave = st.text_input("", placeholder="Introduce contraseña", type="password")
        entrar = st.form_submit_button("ENTRAR")
    if entrar:
        if clave == APP_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# ─── NAV ────────────────────────────────────────────────────────────────────
bot_status = "🟢 ACTIVO" if st.session_state.bot_activo else "⚪ INACTIVO"
bot_badge_color = "#00e676" if st.session_state.bot_activo else "#555"

st.markdown(
    f'<div class="cs-nav">'
    f'<div class="cs-nav-logo">'
    f'<img src="data:image/jpeg;base64,{LOGO_B64}">'
    f'<div class="cs-nav-name">CRYPTO<span>SCALPER</span></div>'
    f'</div>'
    f'<div style="display:flex;align-items:center;gap:8px;">'
    f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{bot_badge_color};">{bot_status}</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# ─── MENU ────────────────────────────────────────────────────────────────────
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    if st.button("🏠 HOME", use_container_width=True, key="btn_home"):
        st.session_state.pagina = "HOME"
with col_m2:
    if st.button("⚡ LIVE", use_container_width=True, key="btn_live"):
        st.session_state.pagina = "LIVE"
with col_m3:
    if st.button("📋 HISTORIAL", use_container_width=True, key="btn_hist"):
        st.session_state.pagina = "HISTORIAL"

pagina = st.session_state.pagina
capital_actual  = st.session_state.capital
capital_inicial = st.session_state.capital_inicial

# ═══════════════════════════════════════════════════════════════════════════════
# HOME
# ═══════════════════════════════════════════════════════════════════════════════
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
        '<div class="cs-icon-item"><div class="cs-icon-box">🤖</div><div class="cs-icon-lbl">IA<br>Integrada</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">⚡</div><div class="cs-icon-lbl">Ejecucion<br>Ultra Rapida</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">🛡️</div><div class="cs-icon-lbl">Gestion<br>de Riesgo</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    hist       = st.session_state.historial
    total_trades = len(hist)
    ganados    = len([t for t in hist if t["resultado"] == "TP"])
    wr_real    = round((ganados / total_trades) * 100) if total_trades > 0 else 0
    cap_disp   = f"{capital_actual:.2f}"

    st.markdown(
        '<div class="cs-stats">'
        f'<div class="cs-stat"><div class="cs-stat-num">{total_trades}</div><div class="cs-stat-lbl">Trades Ejecutados</div></div>'
        f'<div class="cs-stat"><div class="cs-stat-num">{cap_disp} <span class="acc">USDT</span></div><div class="cs-stat-lbl">Capital Actual</div></div>'
        '<div class="cs-stat"><div class="cs-stat-num">99.9<span class="acc">%</span></div><div class="cs-stat-lbl">Uptime</div></div>'
        f'<div class="cs-stat"><div class="cs-stat-num">{wr_real}<span class="acc">%</span></div><div class="cs-stat-lbl">Win Rate Real</div></div>'
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
            '<div class="cs-trade"><span class="cs-arr">></span>'
            '<span class="cs-time">' + t[0] + '</span>'
            '<span class="cs-pair">' + t[1] + '</span>'
            '<span class="cs-tag ' + tag_cls + '">' + t[2] + '</span>'
            '<span class="cs-pnl ' + pnl_cls + '">' + t[3] + '</span></div>'
        )

    st.markdown(
        '<div class="cs-section">'
        '<div class="cs-sec-badge"><span class="cs-pulse"></span> LIVE FEED</div>'
        '<div class="cs-sec-h2">Mira el bot trabajando</div>'
        '<div class="cs-sec-desc">Trades cerrados en vivo de CRYPTOSCALPER.</div>'
        '<div class="cs-terminal"><div class="cs-term-head">'
        '<span class="cs-dot cs-dr"></span><span class="cs-dot cs-dy"></span><span class="cs-dot cs-dg"></span>'
        '<span class="cs-stream-lbl">STREAMING</span></div>' + rows + '</div></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-features"><div style="text-align:center;margin-bottom:26px;">'
        '<div class="cs-feat-tag">TECNOLOGIA</div>'
        '<div class="cs-feat-h2">Todo lo que necesitas para operar</div>'
        '<div class="cs-feat-p">Herramientas de trading algoritmico accesibles para todos.</div>'
        '</div>'
        '<div class="cs-fcard"><div class="cs-ficon">📊</div><h3>Estrategia Triple Filtro</h3><p>EMA7/18 + RSI(6) + Volumen. Los 3 deben confirmar antes de dar senal.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">🛡️</div><h3>TP y SL Automatico</h3><p>Take Profit 1.4% y Stop Loss 0.7%. El bot avisa cuando alcanzas tu objetivo.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">💰</div><h3>Reinversion Automatica</h3><p>El capital crece con cada ganancia. Cada trade usa el saldo acumulado completo.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📡</div><h3>Alertas Telegram</h3><p>Notificacion instantanea cuando hay senal de compra, TP o SL activado.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📋</div><h3>Historial Profesional</h3><p>Registro estilo MetaTrader con entrada, salida, P&L y estadisticas en tiempo real.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">🔒</div><h3>Acceso Seguro</h3><p>Login con contrasena y variables de entorno protegidas en Render.</p></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div style="text-align:center;padding:26px 20px;border-top:1px solid #1e1e1e;color:#666;font-size:12px;">'
        '<div>2026 CRYPTOSCALPER BOT PRO. Todos los derechos reservados.</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════════════════════════
# LIVE TRADING — MetaTrader 5 Style
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "LIVE":

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])
    with ctrl1:
        crypto = st.selectbox("Par", ["BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","DOGE/USDT","BNB/USDT"], key="sel_crypto")
    with ctrl2:
        tp = st.number_input("TP %", value=1.4, key="inp_tp")
    with ctrl3:
        sl = st.number_input("SL %", value=0.7, key="inp_sl")
    with ctrl4:
        timeframe = st.selectbox("TF", ["1min","5min","15min","1hour"], key="sel_tf")

    bc1, bc2, bc3, bc4 = st.columns(4)
    with bc1:
        if st.button("▶ INICIAR", use_container_width=True, key="btn_iniciar"):
            st.session_state.bot_activo = True
            enviar_telegram(f"🤖 CRYPTOSCALPER iniciado\nPar: {crypto} | TP: {tp}% | SL: {sl}%")
    with bc2:
        if st.button("⏹ DETENER", use_container_width=True, key="btn_detener"):
            st.session_state.bot_activo = False
            st.session_state.en_posicion = False
            enviar_telegram("⏹ CRYPTOSCALPER detenido.")
    with bc3:
        if st.button("✅ MARCAR COMPRADO", use_container_width=True, key="btn_comprado"):
            st.session_state.en_posicion = True
    with bc4:
        if st.button("❌ CERRAR POSICIÓN", use_container_width=True, key="btn_cerrar"):
            st.session_state.en_posicion = False
            st.session_state.precio_entrada = 0.0

    if not st.session_state.bot_activo:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">'
            '<div style="font-size:40px;margin-bottom:12px;">⏸</div>'
            'Bot detenido — pulsa INICIAR para comenzar.</div>',
            unsafe_allow_html=True
        )
    else:
        st_autorefresh(interval=60000, limit=None, key="autorefresh")
        market = crypto.replace("/", "")
        url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={timeframe}&limit=50"
        try:
            response = requests.get(url, timeout=10)
            data_raw = response.json()

            opens, highs, lows, closes, volumes = [], [], [], [], []
            for candle in data_raw["data"]:
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
            precio_prev   = closes[-2]
            ema7          = df["EMA7"].iloc[-1]
            ema18         = df["EMA18"].iloc[-1]
            rsi           = df["RSI"].iloc[-1]
            vol_actual    = df["volume"].iloc[-1]
            vol_promedio  = df["VOL_MA"].iloc[-1]
            cambio        = precio_actual - precio_prev
            cambio_pct    = (cambio / precio_prev) * 100
            soporte       = df["low"].tail(20).min()
            resistencia   = df["high"].tail(20).max()
            maximo_24h    = df["high"].max()
            minimo_24h    = df["low"].min()

            filtro_ema     = ema7 > ema18
            filtro_rsi     = 52 < rsi < 68
            filtro_volumen = vol_actual > vol_promedio

            capital_op     = st.session_state.capital
            precio_color   = "mt5-price-up" if cambio >= 0 else "mt5-price-dn"
            signo_cambio   = "▲" if cambio >= 0 else "▼"
            precio_tp_disp = precio_actual * (1 + tp / 100)
            precio_sl_disp = precio_actual * (1 - sl / 100)

            # ── QUOTE BAR ──────────────────────────────────────────────────
            st.markdown(
                f'<div class="mt5-quote-bar">'
                f'<div><div class="mt5-symbol">{crypto}</div>'
                f'<div style="font-size:10px;color:#555;">CoinEx Spot • {timeframe}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">PRECIO</div>'
                f'<div class="mt5-price-main {precio_color}">{precio_actual:,.4f} <span style="font-size:14px;">{signo_cambio} {abs(cambio_pct):.2f}%</span></div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">MAX</div><div class="mt5-quote-val">{maximo_24h:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">MIN</div><div class="mt5-quote-val">{minimo_24h:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">SOPORTE</div><div class="mt5-quote-val" style="color:#00e676;">{soporte:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">RESIST.</div><div class="mt5-quote-val" style="color:#e82929;">{resistencia:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">CAPITAL</div><div class="mt5-quote-val" style="color:#4da6ff;">{capital_op:.2f} USDT</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )

            col_chart, col_right = st.columns([4, 1])

            with col_right:
                # Capital progress
                progreso    = min((capital_op / 200.0) * 100, 100)
                color_prog  = "#00e676" if capital_op >= capital_inicial else "#e82929"
                ganancia_u  = capital_op - capital_inicial
                signo_g     = "+" if ganancia_u >= 0 else ""

                st.markdown(
                    f'<div class="mt5-capital-progress">'
                    f'<div class="mt5-cap-row"><span class="mt5-cap-label">CAPITAL</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{color_prog};">{capital_op:.2f} USDT</span></div>'
                    f'<div class="mt5-progress-outer"><div class="mt5-progress-inner" style="width:{progreso:.1f}%;background:{color_prog};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;margin-top:4px;">'
                    f'<span style="font-size:9px;color:#555;">30</span><span style="font-size:9px;color:#555;">200 USDT</span></div>'
                    f'<div style="margin-top:8px;font-size:10px;color:#666;">P&L: <span style="color:{color_prog};font-weight:700;">{signo_g}{ganancia_u:.2f} USDT</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Indicadores
                rsi_pct   = min(rsi, 100)
                rsi_color = "#00e676" if filtro_rsi else ("#e82929" if rsi > 68 else "#ffa726")
                ema_color = "#00e676" if filtro_ema else "#e82929"
                vol_color = "#00e676" if filtro_volumen else "#e82929"
                vol_pct   = min((vol_actual / vol_promedio * 50) if vol_promedio > 0 else 50, 100)

                st.markdown(
                    f'<div class="mt5-rp-section"><div class="mt5-rp-title">INDICADORES</div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 7</span><span class="mt5-rp-val">{ema7:,.4f}</span></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 18</span><span class="mt5-rp-val">{ema18:,.4f}</span></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">RSI(6)</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{rsi_color};">{rsi:.1f}</span></div>'
                    f'<div class="mt5-indicator-bar"><div class="mt5-indicator-fill" style="width:{rsi_pct:.0f}%;background:{rsi_color};"></div></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">Vol/MA</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{vol_color};">{(vol_actual/vol_promedio):.2f}x</span></div>'
                    f'<div class="mt5-indicator-bar"><div class="mt5-indicator-fill" style="width:{vol_pct:.0f}%;background:{vol_color};"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Filtros
                def frow(ok, label):
                    ico = "✓" if ok else "✗"
                    c   = "#00e676" if ok else "#e82929"
                    return f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="color:{c};font-size:12px;font-weight:700;">{ico}</span><span style="font-size:10px;color:#888;">{label}</span></div>'

                st.markdown(
                    '<div class="mt5-rp-section"><div class="mt5-rp-title">FILTROS</div>'
                    + frow(filtro_ema, "EMA 7 > EMA 18")
                    + frow(filtro_rsi, f"RSI 52–68 ({rsi:.0f})")
                    + frow(filtro_volumen, "Vol > Media")
                    + '</div>',
                    unsafe_allow_html=True
                )

                # Solo botón BUY (spot)
                st.markdown(
                    f'<div class="mt5-trade-btn-wrap">'
                    f'<div style="font-size:9px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px;">ENTRADA SPOT</div>'
                    f'<div class="mt5-btn-buy">BUY<span class="mt5-btn-sub">TP {precio_tp_disp:,.4f} | SL {precio_sl_disp:,.4f}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_chart:
                # Señal principal
                if st.session_state.en_posicion:
                    if st.session_state.precio_entrada == 0.0:
                        st.session_state.precio_entrada = precio_actual

                    entrada       = st.session_state.precio_entrada
                    ganancia_pct  = ((precio_actual - entrada) / entrada) * 100
                    precio_tp_pos = entrada * (1 + tp / 100)
                    precio_sl_pos = entrada * (1 - sl / 100)
                    color_pnl     = "#00e676" if ganancia_pct >= 0 else "#e82929"
                    ganancia_usdt_pos = capital_op * ganancia_pct / 100

                    if precio_actual >= precio_tp_pos:
                        st.markdown('<div class="cs-signal-tp">✅ TAKE PROFIT — VENDE AHORA</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "TP":
                            st.session_state.ultima_senal = "TP"
                            nuevo_capital = round(capital_op * (1 + tp / 100), 4)
                            st.session_state.capital = nuevo_capital
                            st.session_state.historial.insert(0, {
                                "fecha": datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par": crypto, "tipo": "COMPRA",
                                "entrada": round(entrada, 4),
                                "salida": round(precio_actual, 4),
                                "pnl": round(ganancia_pct, 2),
                                "resultado": "TP",
                                "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_capital,
                            })
                            st.session_state.en_posicion = False
                            st.session_state.precio_entrada = 0.0
                            enviar_telegram(
                                f"✅ TAKE PROFIT\nPar: {crypto}\nGanancia: +{ganancia_pct:.2f}%\n"
                                f"Capital nuevo: {nuevo_capital:.2f} USDT\nVENDE AHORA"
                            )

                    elif precio_actual <= precio_sl_pos:
                        st.markdown('<div class="cs-signal-sl">🛑 STOP LOSS — VENDE AHORA</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "SL":
                            st.session_state.ultima_senal = "SL"
                            nuevo_capital = round(capital_op * (1 - sl / 100), 4)
                            st.session_state.capital = nuevo_capital
                            st.session_state.historial.insert(0, {
                                "fecha": datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par": crypto, "tipo": "COMPRA",
                                "entrada": round(entrada, 4),
                                "salida": round(precio_actual, 4),
                                "pnl": round(ganancia_pct, 2),
                                "resultado": "SL",
                                "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_capital,
                            })
                            st.session_state.en_posicion = False
                            st.session_state.precio_entrada = 0.0
                            enviar_telegram(
                                f"🛑 STOP LOSS\nPar: {crypto}\nPerdida: {ganancia_pct:.2f}%\n"
                                f"Capital nuevo: {nuevo_capital:.2f} USDT\nVENDE AHORA"
                            )
                    else:
                        st.markdown(
                            f'<div class="cs-signal-wait">EN POSICION — P&L: '
                            f'<span style="color:{color_pnl};">{ganancia_pct:+.2f}% ({ganancia_usdt_pos:+.2f} USDT)</span></div>',
                            unsafe_allow_html=True
                        )
                else:
                    if filtro_ema and filtro_rsi and filtro_volumen:
                        st.markdown('<div class="cs-signal-buy">⚡ SEÑAL: COMPRA AHORA</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "COMPRA":
                            st.session_state.ultima_senal = "COMPRA"
                            enviar_telegram(
                                f"⚡ SEÑAL DE COMPRA\nPar: {crypto}\nPrecio: {precio_actual:.4f}\n"
                                f"Capital: {capital_op:.2f} USDT\nTP: {precio_tp_disp:.4f} | SL: {precio_sl_disp:.4f}"
                            )
                    else:
                        st.markdown('<div class="cs-signal-wait">⏳ ESPERANDO SEÑAL...</div>', unsafe_allow_html=True)

                # Gráfico
                fig = make_subplots(
                    rows=3, cols=1, shared_xaxes=True,
                    row_heights=[0.60, 0.20, 0.20], vertical_spacing=0.01
                )
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["open"], high=df["high"],
                    low=df["low"], close=df["close"],
                    increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
                    decreasing=dict(line=dict(color="#e82929"), fillcolor="#e82929"),
                    name="Precio"
                ), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"],  mode="lines",
                    name="EMA 7",  line=dict(color="#e82929", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA18"], mode="lines",
                    name="EMA 18", line=dict(color="#ffa726", width=1.5)), row=1, col=1)

                if st.session_state.en_posicion and st.session_state.precio_entrada > 0:
                    fig.add_hline(y=st.session_state.precio_entrada * (1 + tp / 100),
                        line_color="#00e676", line_dash="dash", line_width=1,
                        annotation_text=f"TP {tp}%", row=1, col=1)
                    fig.add_hline(y=st.session_state.precio_entrada * (1 - sl / 100),
                        line_color="#e82929", line_dash="dash", line_width=1,
                        annotation_text=f"SL {sl}%", row=1, col=1)
                    fig.add_hline(y=st.session_state.precio_entrada,
                        line_color="#4da6ff", line_dash="dot", line_width=1,
                        annotation_text="Entrada", row=1, col=1)

                fig.add_hline(y=soporte,     line_dash="dot", line_color="#00e676",
                    annotation_text="Soporte",  row=1, col=1)
                fig.add_hline(y=resistencia, line_dash="dot", line_color="#e82929",
                    annotation_text="Resist.",  row=1, col=1)

                fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],
                    fill="tozeroy", fillcolor="rgba(232,41,41,0.05)",
                    line=dict(color="#e82929", width=1), name="RSI(6)"
                ), row=2, col=1)
                fig.add_hline(y=52, line_color="#333", line_width=0.5, row=2, col=1)
                fig.add_hline(y=68, line_color="#333", line_width=0.5, row=2, col=1)

                colors_vol = ["#00e676" if c >= o else "#e82929"
                    for c, o in zip(df["close"], df["open"])]
                fig.add_trace(go.Bar(x=df.index, y=df["volume"],
                    marker_color=colors_vol, name="Vol", opacity=0.7), row=3, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["VOL_MA"],
                    mode="lines", line=dict(color="#ffa726", width=1), name="Vol MA"
                ), row=3, col=1)

                fig.update_layout(
                    height=520, paper_bgcolor="#080808", plot_bgcolor="#0c0c0c",
                    xaxis=dict(showgrid=False, color="#333"),
                    xaxis2=dict(showgrid=False, color="#333"),
                    xaxis3=dict(showgrid=False, color="#333"),
                    yaxis=dict(showgrid=True, gridcolor="#141414", color="#555"),
                    yaxis2=dict(showgrid=True, gridcolor="#141414", color="#555", title="RSI"),
                    yaxis3=dict(showgrid=True, gridcolor="#141414", color="#555", title="Vol"),
                    xaxis_rangeslider_visible=False,
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#666"), orientation="h", y=1.02),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)

            # Terminal
            hist_reciente = st.session_state.historial[:8]
            rows_term = ""
            if hist_reciente:
                rows_term += (
                    '<div class="mt5-term-header">'
                    '<span>FECHA</span><span>PAR</span><span>TIPO</span>'
                    '<span>ENTRADA</span><span>SALIDA</span><span>P&L</span>'
                    '</div>'
                )
                for t in hist_reciente:
                    pnl_color = "#00e676" if t["pnl"] >= 0 else "#e82929"
                    signo = "+" if t["pnl"] >= 0 else ""
                    rows_term += (
                        f'<div class="mt5-term-row">'
                        f'<span>{t["fecha"]}</span>'
                        f'<span style="color:#fff;font-weight:700;">{t["par"]}</span>'
                        f'<span style="color:#4da6ff;">{t["tipo"]}</span>'
                        f'<span>{t["entrada"]}</span>'
                        f'<span>{t["salida"]}</span>'
                        f'<span style="color:{pnl_color};font-weight:700;">{signo}{t["pnl"]}%</span>'
                        f'</div>'
                    )
            else:
                rows_term = '<div style="padding:20px;color:#444;text-align:center;font-size:12px;">Sin operaciones cerradas aun.</div>'

            st.markdown(
                '<div class="mt5-terminal">'
                '<div class="mt5-term-tabs">'
                '<div class="mt5-term-tab active">📋 Historial</div>'
                '<div class="mt5-term-tab">📡 Senales</div>'
                '<div class="mt5-term-tab">💰 Capital</div>'
                '</div>'
                '<div class="mt5-term-body">' + rows_term + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            st.success(f"🟢 Bot activo: {crypto} | TP: {tp}% | SL: {sl}% | Capital: {capital_op:.2f} USDT")

        except Exception as e:
            st.error(f"Error al obtener datos: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# HISTORIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "HISTORIAL":
    historial = st.session_state.historial

    if historial:
        total     = len(historial)
        ganadores = len([t for t in historial if t["resultado"] == "TP"])
        win_rate  = round((ganadores / total) * 100)
        pnl_total = round(sum([t["pnl"] for t in historial]), 2)
        cap_actual = st.session_state.capital
        color_wr   = "#00e676" if win_rate >= 50 else "#e82929"
        color_pnl  = "#00e676" if pnl_total >= 0 else "#e82929"
        pnl_str    = ("+" if pnl_total >= 0 else "") + str(pnl_total) + "%"
        ganancia_usdt_total = round(cap_actual - st.session_state.capital_inicial, 2)
        signo_usdt = "+" if ganancia_usdt_total >= 0 else ""

        st.markdown(
            f'<div class="cs-hist-header">'
            f'<div><div class="cs-hist-balance-lbl">CAPITAL ACTUAL</div>'
            f'<div class="cs-hist-balance">{cap_actual:.2f} USDT</div>'
            f'<div style="font-size:11px;color:{"#00e676" if ganancia_usdt_total>=0 else "#e82929"};">'
            f'{signo_usdt}{ganancia_usdt_total:.2f} USDT desde inicio</div></div>'
            f'<div style="text-align:right;"><div class="cs-hist-balance-lbl">WIN RATE</div>'
            f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:{color_wr};">{win_rate}%</div>'
            f'<div style="font-size:11px;color:{color_pnl};">P&L: {pnl_str}</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="cs-hist-resumen">'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num">{total}</div><div class="cs-hist-stat-lbl">Trades</div></div>'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#00e676;">{ganadores}</div><div class="cs-hist-stat-lbl">Ganados</div></div>'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#e82929;">{total - ganadores}</div><div class="cs-hist-stat-lbl">Perdidos</div></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="cs-hist-seccion"><div class="cs-hist-seccion-titulo">Posiciones cerradas</div></div>', unsafe_allow_html=True)

        trades_html = ""
        for t in historial:
            es_tp       = t["resultado"] == "TP"
            color_gan   = "#00e676" if t["pnl"] >= 0 else "#e82929"
            pnl_display = ("+" if t["pnl"] >= 0 else "") + str(t["pnl"]) + "%"
            tag_color   = "rgba(0,230,118,0.15)" if es_tp else "rgba(232,41,41,0.15)"
            tag_text    = "#00e676" if es_tp else "#e82929"
            cap_usado   = t.get("capital_usado", "—")
            cap_nuevo   = t.get("capital_nuevo", "—")
            trades_html += (
                f'<div class="cs-hist-trade"><div style="flex:1;">'
                f'<div class="cs-hist-par">{t["par"]} <span class="cs-hist-tipo">buy</span></div>'
                f'<div class="cs-hist-precios">{t["entrada"]} → {t["salida"]}</div>'
                f'<div style="font-size:10px;color:#444;margin-top:2px;">Cap: {cap_usado} → {cap_nuevo} USDT • {t["fecha"]}</div>'
                f'</div><div style="text-align:right;">'
                f'<div class="cs-hist-ganancia" style="color:{color_gan};">{pnl_display}</div>'
                f'<div class="cs-hist-tag" style="background:{tag_color};color:{tag_text};">{t["resultado"]}</div>'
                f'</div></div>'
            )
        st.markdown(trades_html, unsafe_allow_html=True)

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🗑 Limpiar historial", use_container_width=True):
                st.session_state.historial = []
                st.rerun()
        with col_r2:
            if st.button("🔄 Resetear capital a 30 USDT", use_container_width=True):
                st.session_state.capital = 30.0
                st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:80px 20px;font-size:15px;">'
            '<div style="font-size:40px;margin-bottom:16px;">📋</div>'
            '<div>No hay trades aun.</div>'
            '<div style="font-size:13px;margin-top:8px;">Los trades aparecen aqui cuando el bot detecta TP o SL.</div>'
            '</div>',
            unsafe_allow_html=True
        )
