import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
import os
from datetime import datetime

st.set_page_config(
    page_title="CRYPTOSCALPER BOT PRO",
    page_icon="Fabi con.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── VARIABLES DE ENTORNO ───────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
APP_PASSWORD     = os.environ.get("APP_PASSWORD", "CRYPTOSCALPER123")

# ─── INIT SESSION STATE (todo de una sola vez para evitar reruns innecesarios)
def init_state():
    defaults = {
        "auth": False,
        "bot_activo": False,
        "pagina": "HOME",
        "ultima_senal": "",
        "en_posicion": False,
        "precio_entrada": 0.0,
        "historial": [],
        "capital": 30.0,          # capital inicial
        "capital_inicial": 30.0,  # referencia fija
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
    delta   = series.diff()
    ganancia = delta.where(delta > 0, 0).rolling(window=periodo).mean()
    perdida  = -delta.where(delta < 0, 0).rolling(window=periodo).mean()
    rs = ganancia / perdida
    return 100 - (100 / (1 + rs))

def get_logo():
    try:
        with open("Fabi con.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

LOGO = get_logo()

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
    padding: 12px 20px; border-bottom: 1px solid #1e1e1e;
    background: rgba(8,8,8,0.97); position: sticky; top: 0; z-index: 999;
}
.cs-nav-logo { display: flex; align-items: center; gap: 10px; }
.cs-nav-name { font-family: 'Rajdhani', sans-serif; font-size: 20px; font-weight: 700; letter-spacing: 2px; color: #fff; }
.cs-nav-name span { color: #e82929; }

/* CAPITAL BADGE */
.cs-capital-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(77,166,255,0.12); border: 1px solid rgba(77,166,255,0.35);
    color: #4da6ff; padding: 6px 14px; border-radius: 100px; font-size: 12px;
    font-weight: 700; letter-spacing: 1px; font-family: 'JetBrains Mono', monospace;
}
.cs-capital-gain { color: #00e676; }
.cs-capital-loss { color: #e82929; }

/* HERO */
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

/* FILTROS */
.cs-filter-box { background: #101010; border: 1px solid #1e1e1e; border-radius: 12px; padding: 16px; margin-bottom: 12px; }
.cs-filter-ok  { color: #00e676; font-size: 13px; margin-bottom: 4px; }
.cs-filter-no  { color: #e82929; font-size: 13px; margin-bottom: 4px; }
.cs-position-box { background: #101010; border: 1px solid #ffa726; border-radius: 12px; padding: 16px; margin-bottom: 12px; }

/* ═══════════════════════════════════════════════════════
   MT5-STYLE LIVE TRADING
═══════════════════════════════════════════════════════ */
.mt5-wrapper { background: #0d0d0d; min-height: 100vh; }

/* Toolbar MT5 */
.mt5-toolbar {
    display: flex; align-items: center; gap: 6px;
    background: #141414; border-bottom: 1px solid #222;
    padding: 6px 12px; flex-wrap: wrap;
}
.mt5-tb-group { display: flex; align-items: center; gap: 4px; padding-right: 10px; border-right: 1px solid #222; margin-right: 4px; }
.mt5-tb-group:last-child { border-right: none; }
.mt5-tb-btn {
    background: #1a1a1a; border: 1px solid #2a2a2a; color: #aaa;
    padding: 4px 10px; border-radius: 4px; font-size: 10px; font-weight: 600;
    letter-spacing: 0.5px; cursor: pointer; font-family: 'JetBrains Mono', monospace;
}
.mt5-tb-btn.active { background: #e82929; border-color: #e82929; color: #fff; }
.mt5-tb-sep { width: 1px; background: #222; height: 20px; }

/* Panel superior de cotización */
.mt5-quote-bar {
    background: #111; border-bottom: 1px solid #1e1e1e;
    padding: 8px 14px; display: flex; align-items: center;
    justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.mt5-symbol { font-family: 'Rajdhani', sans-serif; font-size: 22px; font-weight: 700; color: #fff; }
.mt5-price-main { font-family: 'JetBrains Mono', monospace; font-size: 26px; font-weight: 600; color: #fff; }
.mt5-price-up   { color: #00e676; }
.mt5-price-dn   { color: #e82929; }
.mt5-quote-item { text-align: center; }
.mt5-quote-lbl  { font-size: 9px; color: #555; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 2px; }
.mt5-quote-val  { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ccc; font-weight: 600; }

/* Layout principal: gráfico izq + panel der */
.mt5-main { display: flex; gap: 0; }
.mt5-chart-area { flex: 1; min-width: 0; }

/* Panel derecho MT5 */
.mt5-right-panel {
    width: 220px; flex-shrink: 0; background: #111;
    border-left: 1px solid #1e1e1e; display: flex; flex-direction: column;
}
.mt5-rp-section { border-bottom: 1px solid #1e1e1e; padding: 12px; }
.mt5-rp-title {
    font-size: 9px; color: #555; letter-spacing: 2px; text-transform: uppercase;
    margin-bottom: 10px; font-weight: 700;
}
.mt5-rp-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
.mt5-rp-key { font-size: 10px; color: #666; }
.mt5-rp-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ccc; font-weight: 600; }
.mt5-rp-val-green { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #00e676; font-weight: 700; }
.mt5-rp-val-red   { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #e82929; font-weight: 700; }
.mt5-rp-val-blue  { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #4da6ff; font-weight: 700; }

/* Botones BUY / SELL estilo MT5 */
.mt5-trade-btns { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; padding: 12px; }
.mt5-btn-buy {
    background: linear-gradient(135deg, #00b894, #00e676);
    color: #000; padding: 12px 6px; border-radius: 6px;
    text-align: center; font-family: 'Rajdhani', sans-serif;
    font-size: 16px; font-weight: 700; cursor: pointer; border: none;
}
.mt5-btn-sell {
    background: linear-gradient(135deg, #c0392b, #e82929);
    color: #fff; padding: 12px 6px; border-radius: 6px;
    text-align: center; font-family: 'Rajdhani', sans-serif;
    font-size: 16px; font-weight: 700; cursor: pointer; border: none;
}
.mt5-btn-sub { font-size: 9px; font-weight: 400; display: block; opacity: 0.8; }

/* Indicadores RSI / EMA en panel */
.mt5-indicator-bar { height: 6px; background: #1e1e1e; border-radius: 3px; overflow: hidden; margin-top: 4px; margin-bottom: 8px; }
.mt5-indicator-fill { height: 100%; border-radius: 3px; transition: width .3s; }

/* Terminal inferior MT5 */
.mt5-terminal {
    background: #0a0a0a; border-top: 2px solid #1e1e1e;
    font-family: 'JetBrains Mono', monospace;
}
.mt5-term-tabs {
    display: flex; background: #111; border-bottom: 1px solid #1e1e1e;
}
.mt5-term-tab {
    padding: 8px 16px; font-size: 10px; font-weight: 600; color: #555;
    letter-spacing: 1px; text-transform: uppercase; cursor: pointer;
    border-right: 1px solid #1e1e1e; border-bottom: 2px solid transparent;
}
.mt5-term-tab.active { color: #e82929; border-bottom: 2px solid #e82929; }
.mt5-term-body { padding: 0; max-height: 180px; overflow-y: auto; }
.mt5-term-row {
    display: grid; grid-template-columns: 90px 80px 1fr 60px 60px 60px;
    padding: 7px 12px; border-bottom: 1px solid #141414;
    font-size: 10px; color: #888; align-items: center;
}
.mt5-term-row:hover { background: #141414; }
.mt5-term-header {
    display: grid; grid-template-columns: 90px 80px 1fr 60px 60px 60px;
    padding: 5px 12px; background: #0f0f0f;
    font-size: 9px; color: #444; letter-spacing: 1px; text-transform: uppercase;
    border-bottom: 1px solid #1e1e1e; position: sticky; top: 0;
}

/* Capital progress bar */
.mt5-capital-progress { padding: 12px; border-bottom: 1px solid #1e1e1e; }
.mt5-cap-row { display: flex; justify-content: space-between; margin-bottom: 6px; }
.mt5-cap-label { font-size: 9px; color: #555; letter-spacing: 1px; text-transform: uppercase; }
.mt5-cap-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 700; }
.mt5-progress-outer { height: 6px; background: #1e1e1e; border-radius: 3px; overflow: hidden; }
.mt5-progress-inner { height: 100%; border-radius: 3px; transition: width .5s; }

/* HISTORIAL ─────────────────────────────────────────── */
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
.cs-hist-tipo { font-size: 12px; font-weight: 600; }
.cs-hist-tipo-compra { color: #4da6ff; }
.cs-hist-precios { font-size: 11px; color: #555; margin-top: 2px; font-family: 'JetBrains Mono', monospace; }
.cs-hist-fecha { font-size: 10px; color: #444; margin-top: 2px; }
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
        clave = st.text_input("", placeholder="Introduce contraseña", type="password")
        entrar = st.form_submit_button("ENTRAR")
    if entrar:
        if clave == APP_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# ─── NAV + CAPITAL BADGE ────────────────────────────────────────────────────
capital_actual  = st.session_state.capital
capital_inicial = st.session_state.capital_inicial
ganancia_cap    = capital_actual - capital_inicial
ganancia_pct_cap = (ganancia_cap / capital_inicial) * 100
color_cap = "cs-capital-gain" if ganancia_cap >= 0 else "cs-capital-loss"
signo_cap = "+" if ganancia_cap >= 0 else ""

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
    '<div class="cs-capital-badge">'
    '💰 <span class="' + color_cap + '">' + f'{capital_actual:.2f} USDT ({signo_cap}{ganancia_pct_cap:.1f}%)</span>'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)

# ─── MENU (sin rerun en cada botón — usamos query params para la página) ────
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

    # Estadísticas dinámicas desde historial real
    hist = st.session_state.historial
    total_trades = len(hist)
    ganados = len([t for t in hist if t["resultado"] == "TP"])
    wr_real = round((ganados / total_trades) * 100) if total_trades > 0 else 0
    cap_disp = f"{capital_actual:.2f}"

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
        '<div style="display:inline-block;background:#141414;border:1px solid #1e1e1e;padding:9px 26px;border-radius:100px;margin-top:10px;">cryptoscalper.app</div>'
        '</div>',
        unsafe_allow_html=True
    )

# ═══════════════════════════════════════════════════════════════════════════════
# LIVE TRADING — ESTILO MetaTrader 5
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "LIVE":

    # ── Controles en sidebar/columnas compactas ────────────────────────────
    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([2, 1, 1, 1])
    with ctrl1:
        crypto = st.selectbox("Par", ["BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","DOGE/USDT","BNB/USDT"], key="sel_crypto")
    with ctrl2:
        tp = st.number_input("TP %", value=1.4, key="inp_tp")
    with ctrl3:
        sl = st.number_input("SL %", value=0.7, key="inp_sl")
    with ctrl4:
        timeframe = st.selectbox("TF", ["1min","5min","15min","1hour"], key="sel_tf")

    # ── Botones de control ─────────────────────────────────────────────────
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

    # ── Estado del bot ─────────────────────────────────────────────────────
    if not st.session_state.bot_activo:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">'
            '<div style="font-size:40px;margin-bottom:12px;">⏸</div>'
            'Bot detenido — pulsa INICIAR para comenzar.</div>',
            unsafe_allow_html=True
        )
    else:
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

            # Capital usado en esta operación
            capital_op = st.session_state.capital

            # ── QUOTE BAR (barra de cotización MT5) ───────────────────────
            precio_color = "mt5-price-up" if cambio >= 0 else "mt5-price-dn"
            signo_cambio = "▲" if cambio >= 0 else "▼"

            st.markdown(
                f'<div class="mt5-quote-bar">'
                f'<div>'
                f'  <div class="mt5-symbol">{crypto}</div>'
                f'  <div style="font-size:10px;color:#555;">CoinEx Spot • {timeframe}</div>'
                f'</div>'
                f'<div class="mt5-quote-item">'
                f'  <div class="mt5-quote-lbl">PRECIO</div>'
                f'  <div class="mt5-price-main {precio_color}">{precio_actual:,.4f} <span style="font-size:14px;">{signo_cambio} {abs(cambio_pct):.2f}%</span></div>'
                f'</div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">MAX</div><div class="mt5-quote-val">{maximo_24h:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">MIN</div><div class="mt5-quote-val">{minimo_24h:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">SOPORTE</div><div class="mt5-quote-val" style="color:#00e676;">{soporte:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">RESIST.</div><div class="mt5-quote-val" style="color:#e82929;">{resistencia:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">CAPITAL OP.</div><div class="mt5-quote-val" style="color:#4da6ff;">{capital_op:.2f} USDT</div></div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # ── LAYOUT PRINCIPAL: Gráfico + Panel Derecho ─────────────────
            col_chart, col_right = st.columns([4, 1])

            with col_right:
                # ── Capital / P&L ────────────────────────────────────────
                progreso = min((capital_op / 200.0) * 100, 100)
                color_prog = "#00e676" if capital_op >= capital_inicial else "#e82929"
                ganancia_usdt = capital_op - capital_inicial
                signo_g = "+" if ganancia_usdt >= 0 else ""

                st.markdown(
                    f'<div class="mt5-capital-progress">'
                    f'  <div class="mt5-cap-row">'
                    f'    <span class="mt5-cap-label">CAPITAL</span>'
                    f'    <span class="mt5-cap-val" style="color:{color_prog};">{capital_op:.2f} USDT</span>'
                    f'  </div>'
                    f'  <div class="mt5-progress-outer">'
                    f'    <div class="mt5-progress-inner" style="width:{progreso:.1f}%;background:{color_prog};"></div>'
                    f'  </div>'
                    f'  <div style="display:flex;justify-content:space-between;margin-top:4px;">'
                    f'    <span style="font-size:9px;color:#555;">30 USDT</span>'
                    f'    <span style="font-size:9px;color:#555;">200 USDT</span>'
                    f'  </div>'
                    f'  <div style="margin-top:8px;font-size:10px;color:#666;">P&L Total: <span style="color:{color_prog};font-weight:700;">{signo_g}{ganancia_usdt:.2f} USDT</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # ── Indicadores ───────────────────────────────────────────
                rsi_pct   = min(rsi, 100)
                rsi_color = "#00e676" if filtro_rsi else ("#e82929" if rsi > 68 else "#ffa726")
                ema_color = "#00e676" if filtro_ema else "#e82929"
                vol_color = "#00e676" if filtro_volumen else "#e82929"
                vol_pct   = min((vol_actual / vol_promedio * 50) if vol_promedio > 0 else 50, 100)

                st.markdown(
                    f'<div class="mt5-rp-section">'
                    f'  <div class="mt5-rp-title">INDICADORES</div>'
                    f'  <div class="mt5-rp-row"><span class="mt5-rp-key">EMA 7</span><span class="mt5-rp-val">{ema7:,.4f}</span></div>'
                    f'  <div class="mt5-rp-row"><span class="mt5-rp-key">EMA 18</span><span class="mt5-rp-val">{ema18:,.4f}</span></div>'
                    f'  <div class="mt5-rp-row"><span class="mt5-rp-key">RSI(6)</span>'
                    f'    <span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{rsi_color};">{rsi:.1f}</span>'
                    f'  </div>'
                    f'  <div class="mt5-indicator-bar"><div class="mt5-indicator-fill" style="width:{rsi_pct:.0f}%;background:{rsi_color};"></div></div>'
                    f'  <div class="mt5-rp-row"><span class="mt5-rp-key">Vol / MA</span>'
                    f'    <span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{vol_color};">{(vol_actual/vol_promedio):.2f}x</span>'
                    f'  </div>'
                    f'  <div class="mt5-indicator-bar"><div class="mt5-indicator-fill" style="width:{vol_pct:.0f}%;background:{vol_color};"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # ── Filtros ───────────────────────────────────────────────
                def frow(ok, label):
                    ico = "✓" if ok else "✗"
                    c   = "#00e676" if ok else "#e82929"
                    return f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><span style="color:{c};font-size:12px;font-weight:700;">{ico}</span><span style="font-size:10px;color:#888;">{label}</span></div>'

                st.markdown(
                    '<div class="mt5-rp-section">'
                    '  <div class="mt5-rp-title">FILTROS</div>'
                    + frow(filtro_ema, "EMA 7 > EMA 18")
                    + frow(filtro_rsi, f"RSI 52–68 ({rsi:.0f})")
                    + frow(filtro_volumen, "Vol > Media")
                    + '</div>',
                    unsafe_allow_html=True
                )

                # ── Botones BUY / SELL estilo MT5 ─────────────────────────
                precio_tp_disp = precio_actual * (1 + tp / 100)
                precio_sl_disp = precio_actual * (1 - sl / 100)
                st.markdown(
                    f'<div class="mt5-trade-btns">'
                    f'  <div class="mt5-btn-buy">BUY<span class="mt5-btn-sub">TP {precio_tp_disp:,.4f}</span></div>'
                    f'  <div class="mt5-btn-sell">SELL<span class="mt5-btn-sub">SL {precio_sl_disp:,.4f}</span></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_chart:
                # ── Señal principal ───────────────────────────────────────
                if st.session_state.en_posicion:
                    if st.session_state.precio_entrada == 0.0:
                        st.session_state.precio_entrada = precio_actual

                    entrada      = st.session_state.precio_entrada
                    ganancia_pct = ((precio_actual - entrada) / entrada) * 100
                    precio_tp_pos = entrada * (1 + tp / 100)
                    precio_sl_pos = entrada * (1 - sl / 100)
                    color_pnl    = "#00e676" if ganancia_pct >= 0 else "#e82929"
                    ganancia_usdt_pos = capital_op * ganancia_pct / 100

                    # TP / SL
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
                            f'<div class="cs-signal-wait">'
                            f'EN POSICION — P&L: <span style="color:{color_pnl};">{ganancia_pct:+.2f}% ({ganancia_usdt_pos:+.2f} USDT)</span>'
                            f'</div>',
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

                # ── Gráfico MT5 (candlestick + volumen) ──────────────────
                fig = make_subplots(
                    rows=3, cols=1, shared_xaxes=True,
                    row_heights=[0.60, 0.20, 0.20], vertical_spacing=0.01
                )
                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["open"], high=df["high"],
                    low=df["low"], close=df["close"],
                    increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
                    decreasing=dict(line=dict(color="#e82929"), fillcolor="#e82929"),
                    name="Precio"
                ), row=1, col=1)
                # EMAs
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"],  mode="lines",
                    name="EMA 7",  line=dict(color="#e82929", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA18"], mode="lines",
                    name="EMA 18", line=dict(color="#ffa726", width=1.5)), row=1, col=1)

                # Líneas TP/SL si hay posición
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
                    annotation_text="Soporte",     row=1, col=1)
                fig.add_hline(y=resistencia, line_dash="dot", line_color="#e82929",
                    annotation_text="Resist.",     row=1, col=1)

                # RSI
                fig.add_trace(go.Scatter(x=df.index, y=df["RSI"],
                    fill="tozeroy", fillcolor="rgba(232,41,41,0.05)",
                    line=dict(color="#e82929", width=1), name="RSI(6)"
                ), row=2, col=1)
                fig.add_hline(y=52, line_color="#333", line_width=0.5, row=2, col=1)
                fig.add_hline(y=68, line_color="#333", line_width=0.5, row=2, col=1)

                # Volumen
                colors_vol = ["#00e676" if c >= o else "#e82929"
                    for c, o in zip(df["close"], df["open"])]
                fig.add_trace(go.Bar(
                    x=df.index, y=df["volume"],
                    marker_color=colors_vol, name="Vol", opacity=0.7
                ), row=3, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["VOL_MA"],
                    mode="lines", line=dict(color="#ffa726", width=1),
                    name="Vol MA"
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

            # ── Terminal inferior MT5 ─────────────────────────────────────
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
                rows_term = '<div style="padding:20px;color:#444;text-align:center;font-size:12px;">Sin operaciones cerradas aún.</div>'

            st.markdown(
                '<div class="mt5-terminal">'
                '  <div class="mt5-term-tabs">'
                '    <div class="mt5-term-tab active">📋 Historial</div>'
                '    <div class="mt5-term-tab">📡 Señales</div>'
                '    <div class="mt5-term-tab">💰 Capital</div>'
                '  </div>'
                '  <div class="mt5-term-body">' + rows_term + '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            # ── Status bar + auto-refresh sin bloquear la UI ─────────────
            st.success(f"🟢 Bot activo: {crypto} | TP: {tp}% | SL: {sl}% | Capital: {capital_op:.2f} USDT")
            st.markdown(
                '<div style="color:#333;font-size:11px;text-align:center;padding:4px;">'
                'Actualizando cada 60s...</div>',
                unsafe_allow_html=True
            )
            # Meta-refresh: el navegador recarga la página solo, sin bloquear Python
            st.markdown(
                '<meta http-equiv="refresh" content="60">',
                unsafe_allow_html=True
            )

        except Exception as e:
            st.error(f"Error al obtener datos: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# HISTORIAL
# ═══════════════════════════════════════════════════════════════════════════════
elif pagina == "HISTORIAL":

    historial = st.session_state.historial

    if historial:
        total    = len(historial)
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
            f'<div>'
            f'  <div class="cs-hist-balance-lbl">CAPITAL ACTUAL</div>'
            f'  <div class="cs-hist-balance">{cap_actual:.2f} USDT</div>'
            f'  <div style="font-size:11px;color:{"#00e676" if ganancia_usdt_total>=0 else "#e82929"};">'
            f'  {signo_usdt}{ganancia_usdt_total:.2f} USDT desde inicio</div>'
            f'</div>'
            f'<div style="text-align:right;">'
            f'  <div class="cs-hist-balance-lbl">WIN RATE</div>'
            f'  <div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:{color_wr};">{win_rate}%</div>'
            f'  <div style="font-size:11px;color:{color_pnl};">P&L: {pnl_str}</div>'
            f'</div>'
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
            es_tp      = t["resultado"] == "TP"
            color_gan  = "#00e676" if t["pnl"] >= 0 else "#e82929"
            pnl_display = ("+" if t["pnl"] >= 0 else "") + str(t["pnl"]) + "%"
            tag_color   = "rgba(0,230,118,0.15)" if es_tp else "rgba(232,41,41,0.15)"
            tag_text    = "#00e676" if es_tp else "#e82929"
            cap_usado   = t.get("capital_usado", "—")
            cap_nuevo   = t.get("capital_nuevo", "—")

            trades_html += (
                f'<div class="cs-hist-trade">'
                f'<div style="flex:1;">'
                f'  <div class="cs-hist-par">{t["par"]} <span class="cs-hist-tipo cs-hist-tipo-compra">buy</span></div>'
                f'  <div class="cs-hist-precios">{t["entrada"]} → {t["salida"]}</div>'
                f'  <div style="font-size:10px;color:#444;margin-top:2px;">Cap: {cap_usado} → {cap_nuevo} USDT &nbsp;•&nbsp; {t["fecha"]}</div>'
                f'</div>'
                f'<div style="text-align:right;">'
                f'  <div class="cs-hist-ganancia" style="color:{color_gan};">{pnl_display}</div>'
                f'  <div class="cs-hist-tag" style="background:{tag_color};color:{tag_text};">{t["resultado"]}</div>'
                f'</div>'
                f'</div>'
            )

        st.markdown(trades_html, unsafe_allow_html=True)

        st.markdown('<div style="padding:16px;">', unsafe_allow_html=True)
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🗑 Limpiar historial", use_container_width=True):
                st.session_state.historial = []
                st.rerun()
        with col_r2:
            if st.button("🔄 Resetear capital a 30 USDT", use_container_width=True):
                st.session_state.capital = 30.0
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:80px 20px;font-size:15px;">'
            '<div style="font-size:40px;margin-bottom:16px;">📋</div>'
            '<div>No hay trades aún.</div>'
            '<div style="font-size:13px;margin-top:8px;">Los trades aparecen aquí cuando el bot detecta TP o SL.</div>'
            '</div>',
            unsafe_allow_html=True
        )
