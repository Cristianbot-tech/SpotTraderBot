import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64, os, json, hmac, hashlib, time as time_module
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="CRYPTOSCALPER BOT PRO", page_icon="🔴",
                   layout="wide", initial_sidebar_state="collapsed")

# ── ENTORNO ──────────────────────────────────────────────────────────────────
TELEGRAM_TOKEN    = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID  = os.environ.get("TELEGRAM_CHAT_ID", "")
APP_PASSWORD      = os.environ.get("APP_PASSWORD", "CRYPTOSCALPER123")
COINEX_API_KEY    = os.environ.get("COINEX_API_KEY", "")
COINEX_API_SECRET = os.environ.get("COINEX_API_SECRET", "")
COINEX_BASE       = "https://api.coinex.com/v2"
COMISION          = 0.004   # 0.2% compra + 0.2% venta
LOGO_B64          = "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"

# ── COINEX API ────────────────────────────────────────────────────────────────
def _sign(method, path, body, ts):
    msg = method.upper() + path + body + ts
    return hmac.new(COINEX_API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

def _hdrs(method, path, body=""):
    ts = str(int(time_module.time() * 1000))
    return {"Content-Type": "application/json",
            "X-COINEX-KEY": COINEX_API_KEY,
            "X-COINEX-SIGN": _sign(method, path, body, ts),
            "X-COINEX-TIMESTAMP": ts}

def get_balance():
    try:
        path = "/assets/spot/balance"
        r = requests.get(COINEX_BASE + path, headers=_hdrs("GET", path), timeout=10)
        d = r.json()
        if d.get("code") != 0:
            return -1.0
        for a in d["data"]:
            if a["ccy"] == "USDT":
                return float(a["available"])
        return 0.0
    except:
        return -1.0

def market_buy(market, usdt):
    try:
        path = "/spot/order"
        bd   = json.dumps({"market": market, "market_type": "SPOT",
                           "side": "buy", "type": "market",
                           "amount": str(round(usdt, 2))}, separators=(",",":"))
        r = requests.post(COINEX_BASE + path, headers=_hdrs("POST", path, bd),
                          data=bd, timeout=10)
        return r.json()
    except Exception as e:
        return {"code": -1, "message": str(e)}

def market_sell(market, amount):
    try:
        path = "/spot/order"
        bd   = json.dumps({"market": market, "market_type": "SPOT",
                           "side": "sell", "type": "market",
                           "amount": str(round(amount, 8))}, separators=(",",":"))
        r = requests.post(COINEX_BASE + path, headers=_hdrs("POST", path, bd),
                          data=bd, timeout=10)
        return r.json()
    except Exception as e:
        return {"code": -1, "message": str(e)}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defs = {
        "auth": False, "pagina": "HOME", "bot_activo": False,
        "auto_trading": True, "en_posicion": False,
        "precio_entrada": 0.0, "cantidad_comprada": 0.0,
        "ultima_senal": "", "log": [],
        "historial": [], "capital": 30.0, "capital_inicial": 30.0,
    }
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                      data={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"},
                      timeout=5)
    except:
        pass

def rsi(series, p=9):
    d = series.diff()
    g = d.where(d > 0, 0).rolling(p).mean()
    l = -d.where(d < 0, 0).rolling(p).mean()
    return 100 - (100 / (1 + g / l))

def atr(df, p=14):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h-l, (h-c.shift()).abs(), (l-c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(p).mean()

def klines(market, period, limit=80):
    url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={period}&limit={limit}"
    d   = requests.get(url, timeout=10).json()["data"]
    df  = pd.DataFrame({"open":   [float(c["open"])  for c in d],
                        "high":   [float(c["high"])  for c in d],
                        "low":    [float(c["low"])   for c in d],
                        "close":  [float(c["close"]) for c in d],
                        "volume": [float(c["value"]) for c in d]})
    return df

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.insert(0, f"[{ts}] {msg}")
    if len(st.session_state.log) > 50:
        st.session_state.log = st.session_state.log[:50]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#080808!important;color:#fff!important;font-family:'Inter',sans-serif!important}
[data-testid="stHeader"]{background:transparent!important}[data-testid="stSidebar"]{display:none}.block-container{padding:0!important;max-width:100%!important}footer,#MainMenu{display:none!important}
.cs-nav{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:1px solid #1e1e1e;background:rgba(8,8,8,.97);position:sticky;top:0;z-index:999}
.cs-nav-logo{display:flex;align-items:center;gap:10px}.cs-nav-logo img{width:44px;height:44px;object-fit:contain;border-radius:8px}
.cs-nav-name{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;letter-spacing:2px;color:#fff}.cs-nav-name span{color:#e82929}
.cs-pulse{width:7px;height:7px;background:#e82929;border-radius:50%;animation:cspulse 1.4s infinite;display:inline-block}
@keyframes cspulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.7)}}
.cs-hero{padding:40px 20px 36px;text-align:center;position:relative;overflow:hidden}
.cs-hero::before{content:'';position:absolute;top:-80px;left:50%;transform:translateX(-50%);width:420px;height:420px;background:radial-gradient(circle,rgba(232,41,41,.1) 0%,transparent 70%);pointer-events:none}
.cs-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(232,41,41,.1);border:1px solid rgba(232,41,41,.3);color:#e82929;padding:7px 16px;border-radius:100px;font-size:12px;font-weight:600;letter-spacing:1px;margin-bottom:24px}
.cs-h1{font-family:'Rajdhani',sans-serif;font-size:44px;font-weight:700;line-height:1;color:#fff;margin-bottom:14px}
.cs-sub{color:#e82929;font-size:17px;font-weight:500;margin-bottom:18px}
.cs-desc{color:#666;font-size:14px;line-height:1.7;max-width:360px;margin:0 auto 32px}
.cs-btn-red{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:#e82929;color:#fff;padding:15px 32px;border-radius:12px;font-weight:700;font-size:15px;border:none;cursor:pointer;width:100%;max-width:320px;box-shadow:0 0 28px rgba(232,41,41,.35);margin-bottom:10px;text-decoration:none}
.cs-btn-outline{display:inline-flex;align-items:center;justify-content:center;background:transparent;color:#fff;padding:15px 32px;border-radius:12px;font-weight:500;font-size:15px;border:1px solid #1e1e1e;cursor:pointer;width:100%;max-width:320px;text-decoration:none}
.cs-btns{display:flex;flex-direction:column;align-items:center;gap:10px}
.cs-strip{display:flex;border-top:1px solid #1e1e1e;border-bottom:1px solid #1e1e1e;background:#0c0c0c}
.cs-icon-item{flex:1;display:flex;flex-direction:column;align-items:center;padding:16px 4px;gap:6px;border-right:1px solid #1e1e1e}
.cs-icon-item:last-child{border-right:none}
.cs-icon-box{width:38px;height:38px;background:rgba(232,41,41,.15);border:1px solid rgba(232,41,41,.3);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px}
.cs-icon-lbl{font-size:8px;color:#666;text-align:center;letter-spacing:.5px;line-height:1.3;text-transform:uppercase}
.cs-stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#1e1e1e}
.cs-stat{background:#080808;padding:22px 12px;text-align:center}
.cs-stat-num{font-family:'Rajdhani',sans-serif;font-size:34px;font-weight:700;color:#fff}.acc{color:#e82929}
.cs-stat-lbl{font-size:10px;color:#666;letter-spacing:1.5px;margin-top:5px;text-transform:uppercase}
.cs-section{padding:44px 20px}
.cs-sec-badge{display:flex;align-items:center;justify-content:center;gap:8px;color:#e82929;font-size:11px;letter-spacing:3px;font-weight:700;text-transform:uppercase;margin-bottom:14px}
.cs-sec-h2{font-family:'Rajdhani',sans-serif;font-size:32px;font-weight:700;text-align:center;margin-bottom:8px;color:#fff}
.cs-sec-desc{color:#666;font-size:14px;text-align:center;margin-bottom:26px}
.cs-terminal{background:#0b0b0b;border:1px solid #1e1e1e;border-radius:14px;overflow:hidden}
.cs-term-head{display:flex;align-items:center;gap:7px;padding:11px 14px;border-bottom:1px solid #1e1e1e}
.cs-dot{width:11px;height:11px;border-radius:50%;display:inline-block}.cs-dr{background:#ff5f57}.cs-dy{background:#febc2e}.cs-dg{background:#28c840}
.cs-stream-lbl{margin-left:8px;font-size:10px;color:#e82929;letter-spacing:2px;font-weight:700}
.cs-trade{display:flex;align-items:center;gap:8px;padding:12px 14px;border-bottom:1px solid rgba(255,255,255,.03);font-size:12px}
.cs-trade:last-child{border-bottom:none}
.cs-arr{color:#444;font-size:10px}.cs-time{color:#444;font-family:monospace;width:56px;flex-shrink:0}
.cs-pair{font-weight:700;flex:1;font-size:11px;color:#fff}
.cs-tag{padding:3px 9px;border-radius:5px;font-size:10px;font-weight:700}
.cs-tl{background:rgba(0,230,118,.1);color:#00e676;border:1px solid rgba(0,230,118,.2)}
.cs-pnl{font-weight:700;margin-left:auto;font-size:12px}.cs-pos{color:#00e676}.cs-neg{color:#e82929}
.cs-features{padding:10px 20px 44px}
.cs-feat-tag{color:#e82929;font-size:11px;letter-spacing:3px;font-weight:700;text-transform:uppercase;margin-bottom:12px;display:block}
.cs-feat-h2{font-family:'Rajdhani',sans-serif;font-size:30px;font-weight:700;color:#fff;margin-bottom:10px}
.cs-feat-p{color:#666;font-size:14px;line-height:1.6;margin-bottom:24px}
.cs-fcard{background:#101010;border:1px solid #1e1e1e;border-radius:18px;padding:24px;margin-bottom:14px}
.cs-ficon{width:52px;height:52px;background:linear-gradient(135deg,rgba(232,41,41,.2),rgba(232,41,41,.04));border:1px solid rgba(232,41,41,.3);border-radius:13px;display:flex;align-items:center;justify-content:center;font-size:21px;margin-bottom:16px}
.cs-fcard h3{font-family:'Rajdhani',sans-serif;font-size:21px;font-weight:700;margin-bottom:8px;color:#fff}
.cs-fcard p{color:#666;font-size:13px;line-height:1.7}
.cs-signal-buy{background:rgba(0,230,118,.08);border:1px solid rgba(0,230,118,.3);border-radius:12px;padding:16px;text-align:center;font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#00e676;margin:10px 0}
.cs-signal-wait{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.3);border-radius:12px;padding:16px;text-align:center;font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#ffa726;margin:10px 0}
.cs-signal-tp{background:rgba(0,230,118,.15);border:2px solid #00e676;border-radius:12px;padding:16px;text-align:center;font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#00e676;margin:10px 0}
.cs-signal-sl{background:rgba(232,41,41,.15);border:2px solid #e82929;border-radius:12px;padding:16px;text-align:center;font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#e82929;margin:10px 0}
.cs-signal-pos{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.3);border-radius:12px;padding:12px;text-align:center;font-size:14px;font-weight:600;color:#ffa726;margin:10px 0}
.cs-signal-trend{background:rgba(77,166,255,.08);border:1px solid rgba(77,166,255,.3);border-radius:10px;padding:10px 14px;text-align:center;font-size:13px;font-weight:600;color:#4da6ff;margin:6px 0}
.fee-banner{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.25);border-radius:10px;padding:10px 14px;margin:6px 0;font-size:11px;color:#ffa726}
.auto-on{background:rgba(0,230,118,.15);border:1px solid #00e676;border-radius:10px;padding:8px 14px;font-size:12px;font-weight:700;color:#00e676;text-align:center;margin:6px 0}
.auto-off{background:rgba(255,167,38,.1);border:1px solid #ffa726;border-radius:10px;padding:8px 14px;font-size:12px;font-weight:700;color:#ffa726;text-align:center;margin:6px 0}
.log-box{background:#0a0a0a;border:1px solid #1e1e1e;border-radius:8px;padding:10px;max-height:160px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:10px;color:#666}
.log-buy{color:#00e676}.log-sell{color:#e82929}.log-info{color:#4da6ff}
.mt5-quote-bar{background:#111;border-bottom:1px solid #1e1e1e;padding:8px 14px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.mt5-symbol{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#fff}
.mt5-price-main{font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:600}
.mt5-price-up{color:#00e676}.mt5-price-dn{color:#e82929}
.mt5-quote-item{text-align:center}
.mt5-quote-lbl{font-size:9px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:2px}
.mt5-quote-val{font-family:'JetBrains Mono',monospace;font-size:13px;color:#ccc;font-weight:600}
.mt5-rp-section{border-bottom:1px solid #1e1e1e;padding:12px}
.mt5-rp-title{font-size:9px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;font-weight:700}
.mt5-rp-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.mt5-rp-key{font-size:10px;color:#666}
.mt5-rp-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:#ccc;font-weight:600}
.mt5-ind-bar{height:6px;background:#1e1e1e;border-radius:3px;overflow:hidden;margin-top:4px;margin-bottom:8px}
.mt5-ind-fill{height:100%;border-radius:3px;transition:width .3s}
.mt5-buy-btn{background:linear-gradient(135deg,#00b894,#00e676);color:#000;padding:14px;border-radius:6px;width:100%;text-align:center;font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700}
.mt5-btn-sub{font-size:9px;font-weight:400;display:block;opacity:.8}
.mt5-cap-prog{padding:12px;border-bottom:1px solid #1e1e1e}
.mt5-cap-row{display:flex;justify-content:space-between;margin-bottom:6px}
.mt5-cap-lbl{font-size:9px;color:#555;letter-spacing:1px;text-transform:uppercase}
.mt5-prog-out{height:6px;background:#1e1e1e;border-radius:3px;overflow:hidden}
.mt5-prog-in{height:100%;border-radius:3px;transition:width .5s}
.mt5-terminal{background:#0a0a0a;border-top:2px solid #1e1e1e;font-family:'JetBrains Mono',monospace}
.mt5-term-tabs{display:flex;background:#111;border-bottom:1px solid #1e1e1e}
.mt5-term-tab{padding:8px 16px;font-size:10px;font-weight:600;color:#555;letter-spacing:1px;text-transform:uppercase;cursor:pointer;border-right:1px solid #1e1e1e;border-bottom:2px solid transparent}
.mt5-term-tab.active{color:#e82929;border-bottom:2px solid #e82929}
.mt5-term-body{padding:0;max-height:180px;overflow-y:auto}
.mt5-term-row{display:grid;grid-template-columns:85px 75px 55px 65px 65px 60px 65px;padding:7px 12px;border-bottom:1px solid #141414;font-size:10px;color:#888;align-items:center}
.mt5-term-row:hover{background:#141414}
.mt5-term-hdr{display:grid;grid-template-columns:85px 75px 55px 65px 65px 60px 65px;padding:5px 12px;background:#0f0f0f;font-size:9px;color:#444;letter-spacing:1px;text-transform:uppercase;border-bottom:1px solid #1e1e1e;position:sticky;top:0}
.cs-hist-header{background:#0f0f0f;padding:16px 20px;border-bottom:1px solid #1e1e1e;display:flex;align-items:center;justify-content:space-between}
.cs-hist-balance{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#4da6ff}
.cs-hist-balance-lbl{font-size:10px;color:#666;letter-spacing:1px;text-transform:uppercase}
.cs-hist-resumen{display:grid;grid-template-columns:1fr 1fr 1fr;background:#101010;border-bottom:1px solid #1e1e1e}
.cs-hist-stat{padding:14px 12px;text-align:center;border-right:1px solid #1e1e1e}
.cs-hist-stat:last-child{border-right:none}
.cs-hist-stat-num{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700}
.cs-hist-stat-lbl{font-size:9px;color:#666;letter-spacing:1px;text-transform:uppercase;margin-top:3px}
.cs-hist-seccion{padding:12px 16px 6px;background:#0a0a0a}
.cs-hist-seccion-titulo{font-size:11px;font-weight:700;color:#888;letter-spacing:1px;text-transform:uppercase}
.cs-hist-trade{background:#0f0f0f;border-bottom:1px solid #141414;padding:14px 16px;display:flex;align-items:center;justify-content:space-between}
.cs-hist-trade:hover{background:#141414}
.cs-hist-par{font-weight:700;font-size:14px;color:#fff;margin-bottom:3px}
.cs-hist-tipo{font-size:12px;font-weight:600;color:#4da6ff}
.cs-hist-precios{font-size:11px;color:#555;margin-top:2px;font-family:'JetBrains Mono',monospace}
.cs-hist-ganancia{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700}
.cs-hist-tag{font-size:10px;padding:2px 8px;border-radius:4px;font-weight:700;margin-top:4px;display:inline-block}
.stButton>button{background:#e82929!important;color:#fff!important;border:none!important;border-radius:10px!important;font-weight:700!important;box-shadow:0 0 20px rgba(232,41,41,.3)!important}
.stButton>button:hover{background:#c0392b!important}
[data-testid="stSelectbox"]>div>div{background:#101010!important;border:1px solid #1e1e1e!important;color:#fff!important;border-radius:10px!important}
[data-testid="stNumberInput"]>div>div{background:#101010!important;border:1px solid #1e1e1e!important;border-radius:10px!important}
</style>
""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if not st.session_state.auth:
    st.markdown(
        '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">' +
        '<div style="background:#101010;border:1px solid #1e1e1e;border-radius:20px;padding:40px 32px;width:100%;max-width:360px;text-align:center;">' +
        f'<img src="data:image/jpeg;base64,{LOGO_B64}" style="width:110px;margin-bottom:16px;border-radius:12px;">' +
        '<div style="font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;letter-spacing:2px;color:#fff;margin-bottom:4px;">CRYPTO<span style=\'color:#e82929;\'>SCALPER</span></div>' +
        '<div style="color:#666;font-size:13px;margin-bottom:28px;">BOT PRO — Acceso exclusivo</div>' +
        '</div></div>',
        unsafe_allow_html=True
    )
    with st.form("login", clear_on_submit=True):
        clave  = st.text_input("", placeholder="Introduce contraseña", type="password")
        entrar = st.form_submit_button("ENTRAR")
    if entrar:
        if clave == APP_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# ── CARGAR SALDO REAL DE COINEX ───────────────────────────────────────────────
if COINEX_API_KEY and COINEX_API_SECRET and not st.session_state.en_posicion:
    saldo = get_balance()
    if saldo > 0 and abs(saldo - st.session_state.capital) > 0.01:
        st.session_state.capital = round(saldo, 4)

# ── NAV ───────────────────────────────────────────────────────────────────────
if st.session_state.bot_activo and st.session_state.auto_trading:
    nav_status = "🤖 AUTO"
    nav_color  = "#00e676"
elif st.session_state.bot_activo:
    nav_status = "🟡 MANUAL"
    nav_color  = "#ffa726"
else:
    nav_status = "⚪ INACTIVO"
    nav_color  = "#555"

st.markdown(
    f'<div class="cs-nav">' +
    f'<div class="cs-nav-logo"><img src="data:image/jpeg;base64,{LOGO_B64}">' +
    f'<div class="cs-nav-name">CRYPTO<span>SCALPER</span></div></div>' +
    f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{nav_color};">{nav_status}</div>' +
    '</div>',
    unsafe_allow_html=True
)

c1, c2, c3 = st.columns(3)
with c1:
    if st.button("🏠 HOME",      use_container_width=True, key="m1"): st.session_state.pagina = "HOME"
with c2:
    if st.button("⚡ LIVE",      use_container_width=True, key="m2"): st.session_state.pagina = "LIVE"
with c3:
    if st.button("📋 HISTORIAL", use_container_width=True, key="m3"): st.session_state.pagina = "HISTORIAL"

pagina         = st.session_state.pagina
cap            = st.session_state.capital
cap_ini        = st.session_state.capital_inicial

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "HOME":
    st.markdown(
        '<div class="cs-hero">' +
        '<div class="cs-badge"><span class="cs-pulse"></span> Sistema operando en vivo</div>' +
        '<div class="cs-h1">Trading Automatico<br>de Precision</div>' +
        '<div class="cs-sub">Opera solo en CoinEx 24/7</div>' +
        '<div class="cs-desc">4 filtros + ATR dinamico + ejecucion automatica de ordenes. Sin emociones, sin tocar el telefono.</div>' +
        '<div class="cs-btns"><a class="cs-btn-red" href="#">Comenzar Ahora</a><a class="cs-btn-outline" href="#">Ver Features</a></div></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="cs-strip">' +
        '<div class="cs-icon-item"><div class="cs-icon-box">🤖</div><div class="cs-icon-lbl">Trading<br>Auto</div></div>' +
        '<div class="cs-icon-item"><div class="cs-icon-box">📊</div><div class="cs-icon-lbl">4 Filtros<br>Activos</div></div>' +
        '<div class="cs-icon-item"><div class="cs-icon-box">📐</div><div class="cs-icon-lbl">ATR<br>Dinamico</div></div>' +
        '<div class="cs-icon-item"><div class="cs-icon-box">💸</div><div class="cs-icon-lbl">Anti<br>Comision</div></div>' +
        '<div class="cs-icon-item"><div class="cs-icon-box">🔗</div><div class="cs-icon-lbl">CoinEx<br>API</div></div>' +
        '</div>',
        unsafe_allow_html=True
    )
    hist  = st.session_state.historial
    total = len(hist)
    gan   = len([t for t in hist if t["resultado"] == "TP"])
    wr    = round((gan / total) * 100) if total > 0 else 0
    st.markdown(
        '<div class="cs-stats">' +
        f'<div class="cs-stat"><div class="cs-stat-num">{total}</div><div class="cs-stat-lbl">Trades Auto</div></div>' +
        f'<div class="cs-stat"><div class="cs-stat-num">{cap:.2f} <span class="acc">USDT</span></div><div class="cs-stat-lbl">Capital Actual</div></div>' +
        f'<div class="cs-stat"><div class="cs-stat-num">{wr}<span class="acc">%</span></div><div class="cs-stat-lbl">Win Rate Real</div></div>' +
        f'<div class="cs-stat"><div class="cs-stat-num">{round(cap - cap_ini, 2):+.2f}<span class="acc"> $</span></div><div class="cs-stat-lbl">P&L Total</div></div>' +
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="cs-features"><div style="text-align:center;margin-bottom:26px;">' +
        '<div class="cs-feat-tag">TECNOLOGIA AUTOMATICA</div>' +
        '<div class="cs-feat-h2">Bot opera solo en CoinEx</div>' +
        '<div class="cs-feat-p">Detecta señal → compra solo → monitorea → vende solo al TP o SL.</div>' +
        '</div>' +
        '<div class="cs-fcard"><div class="cs-ficon">🤖</div><h3>Trading 100% Automatico</h3><p>El bot ejecuta ordenes reales en CoinEx sin que toques nada. Compra cuando detecta señal, vende al llegar al TP o SL.</p></div>' +
        '<div class="cs-fcard"><div class="cs-ficon">📊</div><h3>4 Filtros de Calidad</h3><p>EMA7/18 + RSI(9) zona 55-65 + Volumen + Tendencia 5min. Solo entra cuando todo confirma.</p></div>' +
        '<div class="cs-fcard"><div class="cs-ficon">📐</div><h3>TP/SL con ATR Dinamico</h3><p>Take Profit y Stop Loss se ajustan a la volatilidad real. TP minimo 1.8% para garantizar ganancia neta despues de comisiones.</p></div>' +
        '<div class="cs-fcard"><div class="cs-ficon">💸</div><h3>Comisiones CoinEx Incluidas</h3><p>0.4% por trade ya calculado. Nunca entras en un trade donde la comision se come la ganancia.</p></div>' +
        '<div class="cs-fcard"><div class="cs-ficon">💰</div><h3>Reinversion Automatica</h3><p>Capital crece trade a trade desde 30 USDT. El saldo real de CoinEx se carga automaticamente.</p></div>' +
        '<div class="cs-fcard"><div class="cs-ficon">📡</div><h3>Alertas Telegram</h3><p>Notificacion de cada compra y venta con precio, ganancia neta y capital actualizado.</p></div>' +
        '</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# LIVE TRADING
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "LIVE":

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        crypto = st.selectbox("Par", ["BTC/USDT","ETH/USDT","SOL/USDT","XRP/USDT","DOGE/USDT","BNB/USDT","OXO/USDT"], key="sel_c")
    with col2:
        timeframe = st.selectbox("TF entrada", ["1min","3min","5min"], key="sel_tf")
    with col3:
        tf_mayor  = st.selectbox("TF tendencia", ["5min","15min","1hour"], key="sel_tfm")

    st.markdown(
        f'<div class="fee-banner">⚠️ Comisión CoinEx: 0.4% por trade (0.2% compra + 0.2% venta) — ya incluida en TP/SL</div>',
        unsafe_allow_html=True
    )

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("▶ INICIAR BOT", use_container_width=True, key="bi"):
            st.session_state.bot_activo = True
            add_log("✅ Bot iniciado en modo AUTO")
            telegram(f"🤖 CRYPTOSCALPER iniciado\nModo: AUTOMATICO\nPar: {crypto} | TF: {timeframe}")
    with b2:
        if st.button("⏹ DETENER BOT", use_container_width=True, key="bd"):
            if st.session_state.en_posicion and st.session_state.cantidad_comprada > 0:
                market_sell(crypto.replace("/",""), st.session_state.cantidad_comprada)
                add_log("⚠️ Bot detenido — posicion cerrada manualmente")
            st.session_state.bot_activo       = False
            st.session_state.en_posicion      = False
            st.session_state.cantidad_comprada = 0.0
            telegram("⏹ CRYPTOSCALPER detenido.")
    with b3:
        modo_lbl = "🤖 AUTO: ON  (click = OFF)" if st.session_state.auto_trading else "✋ MANUAL: ON  (click = AUTO)"
        if st.button(modo_lbl, use_container_width=True, key="bm"):
            st.session_state.auto_trading = not st.session_state.auto_trading

    modo_html = '<div class="auto-on">🤖 MODO AUTOMÁTICO — El bot compra y vende solo</div>' if st.session_state.auto_trading else '<div class="auto-off">✋ MODO MANUAL — El bot solo avisa, tú ejecutas</div>'
    st.markdown(modo_html, unsafe_allow_html=True)

    if not st.session_state.bot_activo:
        st.markdown('<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;"><div style="font-size:40px;margin-bottom:12px;">⏸</div>Bot detenido — pulsa INICIAR para comenzar.</div>', unsafe_allow_html=True)
    else:
        st_autorefresh(interval=60000, limit=None, key="ar")
        market = crypto.replace("/","")
        try:
            df = klines(market, timeframe, 80)
            df["EMA7"]   = df["close"].ewm(span=7).mean()
            df["EMA18"]  = df["close"].ewm(span=18).mean()
            df["RSI"]    = rsi(df["close"], 9)
            df["VOL_MA"] = df["volume"].rolling(14).mean()
            df["ATR"]    = atr(df, 14)

            precio   = df["close"].iloc[-1]
            prev     = df["close"].iloc[-2]
            ema7_v   = df["EMA7"].iloc[-1]
            ema18_v  = df["EMA18"].iloc[-1]
            rsi_v    = df["RSI"].iloc[-1]
            vol_v    = df["volume"].iloc[-1]
            volma_v  = df["VOL_MA"].iloc[-1]
            atr_v    = df["ATR"].iloc[-1]
            cambio_p = ((precio - prev) / prev) * 100
            soporte  = df["low"].tail(20).min()
            resist   = df["high"].tail(20).max()

            # Tendencia mayor
            try:
                dfm = klines(market, tf_mayor, 30)
                dfm["EMA21"] = dfm["close"].ewm(span=21).mean()
                dfm["EMA50"] = dfm["close"].ewm(span=50).mean()
                tend_ok  = (dfm["EMA21"].iloc[-1] > dfm["EMA50"].iloc[-1] and
                            dfm["close"].iloc[-1] > dfm["EMA21"].iloc[-1])
                tend_str = f"📈 ALCISTA ({tf_mayor})" if tend_ok else f"📉 BAJISTA ({tf_mayor})"
                tend_col = "#00e676" if tend_ok else "#e82929"
            except:
                tend_ok  = False
                tend_str = "⚠️ Error tendencia"
                tend_col = "#ffa726"

            # 4 filtros
            f_ema  = ema7_v > ema18_v
            f_rsi  = 55 < rsi_v < 65
            f_vol  = vol_v > volma_v
            f_tend = tend_ok
            f_ok   = sum([f_ema, f_rsi, f_vol, f_tend])
            todos  = f_ema and f_rsi and f_vol and f_tend

            # ATR dinámico TP/SL
            atr_pct  = (atr_v / precio) * 100
            tp_pct   = max(atr_pct * 1.5, 1.8)
            sl_pct   = max(atr_pct * 0.8, 0.9)
            neto_tp  = tp_pct - (COMISION * 100)
            neto_sl  = -(sl_pct + COMISION * 100)
            precio_tp = precio * (1 + tp_pct / 100)
            precio_sl = precio * (1 - sl_pct / 100)
            capital_op = st.session_state.capital

            # ── Quote bar ────────────────────────────────────────────────
            pc = "mt5-price-up" if cambio_p >= 0 else "mt5-price-dn"
            sc = "▲" if cambio_p >= 0 else "▼"
            st.markdown(
                f'<div class="mt5-quote-bar">' +
                f'<div><div class="mt5-symbol">{crypto}</div><div style="font-size:10px;color:#555;">CoinEx Spot • {timeframe}</div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">PRECIO</div><div class="mt5-price-main {pc}">{precio:,.4f} <span style="font-size:14px;">{sc} {abs(cambio_p):.2f}%</span></div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">ATR%</div><div class="mt5-quote-val">{atr_pct:.2f}%</div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">TP DIN.</div><div class="mt5-quote-val" style="color:#00e676;">{tp_pct:.2f}%</div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">SL DIN.</div><div class="mt5-quote-val" style="color:#e82929;">{sl_pct:.2f}%</div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">NETO TP</div><div class="mt5-quote-val" style="color:#00e676;">+{neto_tp:.2f}%</div></div>' +
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">CAPITAL</div><div class="mt5-quote-val" style="color:#4da6ff;">{capital_op:.2f} USDT</div></div>' +
                '</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="cs-signal-trend">TENDENCIA {tf_mayor.upper()}: <span style="color:{tend_col};font-weight:700;">{tend_str}</span></div>',
                unsafe_allow_html=True
            )

            col_chart, col_right = st.columns([4, 1])

            with col_right:
                # Capital progress
                prog      = min((capital_op / 200.0) * 100, 100)
                cprog_col = "#00e676" if capital_op >= cap_ini else "#e82929"
                gan_u     = capital_op - cap_ini
                sg        = "+" if gan_u >= 0 else ""
                st.markdown(
                    f'<div class="mt5-cap-prog">' +
                    f'<div class="mt5-cap-row"><span class="mt5-cap-lbl">CAPITAL COINEX</span><span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{cprog_col};">{capital_op:.2f} USDT</span></div>' +
                    f'<div class="mt5-prog-out"><div class="mt5-prog-in" style="width:{prog:.1f}%;background:{cprog_col};"></div></div>' +
                    f'<div style="display:flex;justify-content:space-between;margin-top:4px;"><span style="font-size:9px;color:#555;">30</span><span style="font-size:9px;color:#555;">200 USDT</span></div>' +
                    f'<div style="margin-top:8px;font-size:10px;color:#666;">P&L: <span style="color:{cprog_col};font-weight:700;">{sg}{gan_u:.2f} USDT</span></div>' +
                    '</div>',
                    unsafe_allow_html=True
                )
                # Indicadores
                rsi_col = "#00e676" if f_rsi else ("#e82929" if rsi_v > 65 else "#ffa726")
                vol_col = "#00e676" if f_vol else "#e82929"
                vol_pct = min((vol_v / volma_v * 50) if volma_v > 0 else 50, 100)
                st.markdown(
                    f'<div class="mt5-rp-section"><div class="mt5-rp-title">INDICADORES</div>' +
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 7</span><span class="mt5-rp-val">{ema7_v:,.4f}</span></div>' +
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 18</span><span class="mt5-rp-val">{ema18_v:,.4f}</span></div>' +
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">RSI(9)</span><span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{rsi_col};">{rsi_v:.1f}</span></div>' +
                    f'<div class="mt5-ind-bar"><div class="mt5-ind-fill" style="width:{min(rsi_v,100):.0f}%;background:{rsi_col};"></div></div>' +
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">Vol/MA</span><span style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{vol_col};">{(vol_v/volma_v):.2f}x</span></div>' +
                    f'<div class="mt5-ind-bar"><div class="mt5-ind-fill" style="width:{vol_pct:.0f}%;background:{vol_col};"></div></div>' +
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">ATR%</span><span style="font-family:JetBrains Mono,monospace;font-size:11px;color:#ffa726;">{atr_pct:.2f}%</span></div>' +
                    '</div>',
                    unsafe_allow_html=True
                )
                # 4 Filtros
                def fr(ok, lbl):
                    c = "#00e676" if ok else "#e82929"
                    i = "✓" if ok else "✗"
                    return f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;"><span style="color:{c};font-size:11px;font-weight:700;">{i}</span><span style="font-size:9px;color:#888;">{lbl}</span></div>'
                sc2 = "#00e676" if todos else ("#ffa726" if f_ok >= 2 else "#e82929")
                st.markdown(
                    f'<div class="mt5-rp-section"><div class="mt5-rp-title">FILTROS ({f_ok}/4) <span style="color:{sc2};">{"✓ COMPRA" if todos else "⏳ ESPERA"}</span></div>' +
                    fr(f_ema,  "EMA 7 > EMA 18") +
                    fr(f_rsi,  f"RSI 55-65 ({rsi_v:.0f})") +
                    fr(f_vol,  "Vol > Media") +
                    fr(f_tend, f"Tend. {tf_mayor}") +
                    '</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div style="padding:12px;">' +
                    f'<div class="mt5-buy-btn">BUY' +
                    f'<span class="mt5-btn-sub">TP {precio_tp:,.4f} (+{tp_pct:.2f}%)</span>' +
                    f'<span class="mt5-btn-sub">SL {precio_sl:,.4f} (-{sl_pct:.2f}%)</span>' +
                    f'<span class="mt5-btn-sub" style="color:rgba(0,0,0,.6);">Neto: +{neto_tp:.2f}%</span>' +
                    '</div></div>',
                    unsafe_allow_html=True
                )

            with col_chart:
                # ── LÓGICA DE TRADING AUTOMÁTICO ─────────────────────────
                if st.session_state.en_posicion:
                    if st.session_state.precio_entrada == 0.0:
                        st.session_state.precio_entrada = precio

                    entrada    = st.session_state.precio_entrada
                    qty        = st.session_state.cantidad_comprada
                    ganp       = ((precio - entrada) / entrada) * 100
                    p_tp       = entrada * (1 + tp_pct / 100)
                    p_sl       = entrada * (1 - sl_pct / 100)
                    pnl_neto   = ganp - (COMISION * 100)
                    color_pnl  = "#00e676" if ganp >= 0 else "#e82929"
                    dist_tp    = ((p_tp - precio) / precio) * 100
                    dist_sl    = ((precio - p_sl) / precio) * 100

                    if precio >= p_tp:
                        st.markdown('<div class="cs-signal-tp">✅ TAKE PROFIT — VENDIENDO...</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "TP":
                            st.session_state.ultima_senal = "TP"
                            # AUTO-SELL
                            if st.session_state.auto_trading and qty > 0:
                                res = market_sell(market, qty)
                                if res.get("code") == 0:
                                    add_log(f"✅ VENTA AUTO TP — {crypto} — {qty:.6f} unidades")
                                else:
                                    add_log(f"❌ Error venta TP: {res.get('message')}")
                            gan_real   = tp_pct - (COMISION * 100)
                            nuevo_cap  = round(capital_op * (1 + gan_real / 100), 4)
                            st.session_state.capital = nuevo_cap
                            st.session_state.historial.insert(0, {
                                "fecha": datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par": crypto, "tipo": "AUTO",
                                "entrada": round(entrada, 4), "salida": round(precio, 4),
                                "pnl": round(gan_real, 2), "comision": 0.4,
                                "resultado": "TP", "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_cap,
                            })
                            st.session_state.en_posicion       = False
                            st.session_state.precio_entrada    = 0.0
                            st.session_state.cantidad_comprada = 0.0
                            telegram(f"✅ TAKE PROFIT AUTO\nPar: {crypto}\nGanancia bruta: +{tp_pct:.2f}%\nComisión: -0.40%\nGanancia NETA: +{gan_real:.2f}%\nCapital nuevo: {nuevo_cap:.2f} USDT")

                    elif precio <= p_sl:
                        st.markdown('<div class="cs-signal-sl">🛑 STOP LOSS — VENDIENDO...</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "SL":
                            st.session_state.ultima_senal = "SL"
                            if st.session_state.auto_trading and qty > 0:
                                res = market_sell(market, qty)
                                if res.get("code") == 0:
                                    add_log(f"🛑 VENTA AUTO SL — {crypto} — {qty:.6f} unidades")
                                else:
                                    add_log(f"❌ Error venta SL: {res.get('message')}")
                            perd_real  = -(sl_pct + COMISION * 100)
                            nuevo_cap  = round(capital_op * (1 + perd_real / 100), 4)
                            st.session_state.capital = nuevo_cap
                            st.session_state.historial.insert(0, {
                                "fecha": datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par": crypto, "tipo": "AUTO",
                                "entrada": round(entrada, 4), "salida": round(precio, 4),
                                "pnl": round(perd_real, 2), "comision": 0.4,
                                "resultado": "SL", "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_cap,
                            })
                            st.session_state.en_posicion       = False
                            st.session_state.precio_entrada    = 0.0
                            st.session_state.cantidad_comprada = 0.0
                            telegram(f"🛑 STOP LOSS AUTO\nPar: {crypto}\nPérdida bruta: -{sl_pct:.2f}%\nComisión: -0.40%\nPérdida NETA: {perd_real:.2f}%\nCapital nuevo: {nuevo_cap:.2f} USDT")
                    else:
                        gan_usdt = capital_op * pnl_neto / 100
                        st.markdown(
                            f'<div class="cs-signal-pos">EN POSICIÓN — P&L: <span style="color:{color_pnl};">{ganp:+.2f}% neto {pnl_neto:+.2f}% ({gan_usdt:+.4f} USDT)</span><br>' +
                            f'TP a {dist_tp:.2f}% &nbsp;|&nbsp; SL a {dist_sl:.2f}%</div>',
                            unsafe_allow_html=True
                        )

                else:
                    # Sin posición — buscar señal
                    if todos:
                        gan_esperada = round(capital_op * neto_tp / 100, 4)
                        st.markdown(
                            f'<div class="cs-signal-buy">⚡ SEÑAL: COMPRA AHORA<br>' +
                            f'<span style="font-size:13px;">TP: {precio_tp:,.4f} | SL: {precio_sl:,.4f} | Neto esperado: +{neto_tp:.2f}% (+{gan_esperada} USDT)</span></div>',
                            unsafe_allow_html=True
                        )
                        if st.session_state.ultima_senal != "COMPRA":
                            st.session_state.ultima_senal = "COMPRA"
                            if st.session_state.auto_trading:
                                # AUTO-BUY
                                res = market_buy(market, capital_op)
                                if res.get("code") == 0:
                                    data_ord = res.get("data", {})
                                    qty_comp = float(data_ord.get("base_fill_amount",
                                                    data_ord.get("amount", 0)))
                                    if qty_comp == 0:
                                        qty_comp = capital_op / precio
                                    st.session_state.en_posicion       = True
                                    st.session_state.precio_entrada    = precio
                                    st.session_state.cantidad_comprada = qty_comp
                                    add_log(f"🛒 COMPRA AUTO — {crypto} — {qty_comp:.6f} unidades @ {precio:,.4f}")
                                    telegram(
                                        f"🛒 COMPRA AUTO\nPar: {crypto}\nPrecio: {precio:.4f}\n"
                                        f"Capital: {capital_op:.2f} USDT\nCantidad: {qty_comp:.6f}\n"
                                        f"TP: {precio_tp:.4f} (+{tp_pct:.2f}%)\n"
                                        f"SL: {precio_sl:.4f} (-{sl_pct:.2f}%)\n"
                                        f"Ganancia neta esperada: +{neto_tp:.2f}%"
                                    )
                                else:
                                    add_log(f"❌ Error compra: {res.get('message')}")
                            else:
                                telegram(
                                    f"⚡ SEÑAL MANUAL\nPar: {crypto}\nPrecio: {precio:.4f}\n"
                                    f"TP: {precio_tp:.4f} | SL: {precio_sl:.4f}\n"
                                    f"Neto esperado: +{neto_tp:.2f}%"
                                )
                    else:
                        st.markdown(
                            f'<div class="cs-signal-wait">⏳ ESPERANDO SEÑAL — {f_ok}/4 filtros OK</div>',
                            unsafe_allow_html=True
                        )

                # ── Gráfico ───────────────────────────────────────────────
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                    row_heights=[0.60, 0.20, 0.20], vertical_spacing=0.01)
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["open"], high=df["high"],
                    low=df["low"], close=df["close"],
                    increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
                    decreasing=dict(line=dict(color="#e82929"), fillcolor="#e82929"),
                    name="Precio"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"],  mode="lines",
                    name="EMA7",  line=dict(color="#e82929", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA18"], mode="lines",
                    name="EMA18", line=dict(color="#ffa726", width=1.5)), row=1, col=1)
                if st.session_state.en_posicion and st.session_state.precio_entrada > 0:
                    ep = st.session_state.precio_entrada
                    fig.add_hline(y=ep*(1+tp_pct/100), line_color="#00e676", line_dash="dash", line_width=1.5, annotation_text=f"TP {tp_pct:.1f}%", row=1, col=1)
                    fig.add_hline(y=ep*(1-sl_pct/100), line_color="#e82929", line_dash="dash", line_width=1.5, annotation_text=f"SL {sl_pct:.1f}%", row=1, col=1)
                    fig.add_hline(y=ep, line_color="#4da6ff", line_dash="dot", line_width=1, annotation_text="Entrada", row=1, col=1)
                fig.add_hline(y=soporte, line_dash="dot", line_color="#00e676", annotation_text="Soporte", row=1, col=1)
                fig.add_hline(y=resist,  line_dash="dot", line_color="#e82929", annotation_text="Resist.",  row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], fill="tozeroy",
                    fillcolor="rgba(232,41,41,0.05)", line=dict(color="#e82929", width=1), name="RSI"), row=2, col=1)
                fig.add_hline(y=55, line_color="#00e676", line_width=0.7, line_dash="dot", row=2, col=1)
                fig.add_hline(y=65, line_color="#e82929", line_width=0.7, line_dash="dot", row=2, col=1)
                cv = ["#00e676" if c >= o else "#e82929" for c,o in zip(df["close"], df["open"])]
                fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=cv, name="Vol", opacity=0.7), row=3, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["VOL_MA"], mode="lines",
                    line=dict(color="#ffa726", width=1), name="Vol MA"), row=3, col=1)
                fig.update_layout(height=500, paper_bgcolor="#080808", plot_bgcolor="#0c0c0c",
                    xaxis=dict(showgrid=False, color="#333"), xaxis2=dict(showgrid=False, color="#333"),
                    xaxis3=dict(showgrid=False, color="#333"),
                    yaxis=dict(showgrid=True, gridcolor="#141414", color="#555"),
                    yaxis2=dict(showgrid=True, gridcolor="#141414", color="#555", title="RSI"),
                    yaxis3=dict(showgrid=True, gridcolor="#141414", color="#555", title="Vol"),
                    xaxis_rangeslider_visible=False,
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#666"), orientation="h", y=1.02),
                    margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)

            # ── Terminal + Log ────────────────────────────────────────────
            hist_r = st.session_state.historial[:8]
            rows_t = ""
            if hist_r:
                rows_t += '<div class="mt5-term-hdr"><span>FECHA</span><span>PAR</span><span>MODO</span><span>ENTRADA</span><span>SALIDA</span><span>NETO%</span><span>CAPITAL</span></div>'
                for t in hist_r:
                    pc2 = "#00e676" if t["pnl"] >= 0 else "#e82929"
                    sg2 = "+" if t["pnl"] >= 0 else ""
                    rows_t += (
                        f'<div class="mt5-term-row">' +
                        f'<span>{t["fecha"]}</span>' +
                        f'<span style="color:#fff;font-weight:700;">{t["par"]}</span>' +
                        f'<span style="color:#4da6ff;">{t["tipo"]}</span>' +
                        f'<span>{t["entrada"]}</span><span>{t["salida"]}</span>' +
                        f'<span style="color:{pc2};font-weight:700;">{sg2}{t["pnl"]}%</span>' +
                        f'<span style="color:#4da6ff;">{t.get("capital_nuevo","—")}</span>' +
                        '</div>'
                    )
            else:
                rows_t = '<div style="padding:20px;color:#444;text-align:center;font-size:12px;">Sin operaciones aun.</div>'

            st.markdown(
                '<div class="mt5-terminal">' +
                '<div class="mt5-term-tabs"><div class="mt5-term-tab active">📋 Historial (P&L neto)</div><div class="mt5-term-tab">💰 Capital</div></div>' +
                '<div class="mt5-term-body">' + rows_t + '</div></div>',
                unsafe_allow_html=True
            )

            # Log de operaciones
            if st.session_state.log:
                log_html = "".join(
                    f'<div class="log-{"buy" if "COMPRA" in l else "sell" if "VENTA" in l or "SL" in l or "TP" in l else "info"}">{l}</div>'
                    for l in st.session_state.log[:10]
                )
                st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

            modo_txt = "AUTO 🤖" if st.session_state.auto_trading else "MANUAL ✋"
            st.success(f"🟢 Bot activo | {crypto} | TP: {tp_pct:.2f}% | SL: {sl_pct:.2f}% | Neto: +{neto_tp:.2f}% | Modo: {modo_txt} | Capital: {capital_op:.2f} USDT")

        except Exception as e:
            st.error(f"Error: {e}")
            add_log(f"❌ Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "HISTORIAL":
    historial = st.session_state.historial
    if historial:
        total  = len(historial)
        gans   = len([t for t in historial if t["resultado"] == "TP"])
        wr     = round((gans / total) * 100)
        pnl_t  = round(sum(t["pnl"] for t in historial), 2)
        com_t  = round(total * COMISION * 100, 2)
        cap_a  = st.session_state.capital
        gan_u  = round(cap_a - cap_ini, 2)
        cwr    = "#00e676" if wr >= 50 else "#e82929"
        cpnl   = "#00e676" if pnl_t >= 0 else "#e82929"
        cgan   = "#00e676" if gan_u >= 0 else "#e82929"
        sg3    = "+" if gan_u >= 0 else ""

        st.markdown(
            '<div class="cs-hist-header">' +
            f'<div><div class="cs-hist-balance-lbl">CAPITAL ACTUAL (COINEX)</div>' +
            f'<div class="cs-hist-balance">{cap_a:.2f} USDT</div>' +
            f'<div style="font-size:11px;color:{cgan};">{sg3}{gan_u:.2f} USDT desde inicio</div>' +
            f'<div style="font-size:10px;color:#555;margin-top:3px;">Comisiones pagadas: -{com_t:.2f}% total</div></div>' +
            f'<div style="text-align:right;"><div class="cs-hist-balance-lbl">WIN RATE</div>' +
            f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:{cwr};">{wr}%</div>' +
            f'<div style="font-size:11px;color:{cpnl};">P&L neto: {("+" if pnl_t>=0 else "")}{pnl_t}%</div>' +
            '</div></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="cs-hist-resumen">' +
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num">{total}</div><div class="cs-hist-stat-lbl">Trades</div></div>' +
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#00e676;">{gans}</div><div class="cs-hist-stat-lbl">Ganados</div></div>' +
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#e82929;">{total-gans}</div><div class="cs-hist-stat-lbl">Perdidos</div></div>' +
            '</div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="cs-hist-seccion"><div class="cs-hist-seccion-titulo">Operaciones cerradas (P&L neto)</div></div>', unsafe_allow_html=True)
        html_t = ""
        for t in historial:
            es_tp = t["resultado"] == "TP"
            cg    = "#00e676" if t["pnl"] >= 0 else "#e82929"
            pd    = ("+" if t["pnl"] >= 0 else "") + str(t["pnl"]) + "%"
            tc    = "rgba(0,230,118,0.15)" if es_tp else "rgba(232,41,41,0.15)"
            tt    = "#00e676" if es_tp else "#e82929"
            html_t += (
                f'<div class="cs-hist-trade"><div style="flex:1;">' +
                f'<div class="cs-hist-par">{t["par"]} <span class="cs-hist-tipo">{t["tipo"]}</span></div>' +
                f'<div class="cs-hist-precios">{t["entrada"]} → {t["salida"]}</div>' +
                f'<div style="font-size:10px;color:#444;margin-top:2px;">Cap: {t.get("capital_usado","—")} → {t.get("capital_nuevo","—")} USDT • Com: -{t.get("comision",0.4)}% • {t["fecha"]}</div>' +
                f'</div><div style="text-align:right;">' +
                f'<div class="cs-hist-ganancia" style="color:{cg};">{pd}</div>' +
                f'<div style="font-size:9px;color:#555;">neto</div>' +
                f'<div class="cs-hist-tag" style="background:{tc};color:{tt};">{t["resultado"]}</div>' +
                '</div></div>'
            )
        st.markdown(html_t, unsafe_allow_html=True)
        r1, r2 = st.columns(2)
        with r1:
            if st.button("🗑 Limpiar historial", use_container_width=True):
                st.session_state.historial = []
                st.rerun()
        with r2:
            if st.button("🔄 Resetear capital a 30 USDT", use_container_width=True):
                st.session_state.capital = 30.0
                st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:80px 20px;font-size:15px;">' +
            '<div style="font-size:40px;margin-bottom:16px;">📋</div>' +
            '<div>No hay trades aun.</div>' +
            '<div style="font-size:13px;margin-top:8px;">El bot registra cada operacion automatica aqui.</div>' +
            '</div>',
            unsafe_allow_html=True
        )
