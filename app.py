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
COMISION          = 0.003   # 0.1% limit buy (maker) + 0.2% market sell = 0.3%
PARES_SCAN        = [
    "BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "DOGE/USDT",
    "BILL/USDT", "ONDO/USDT", "POL/USDT"
]
ESTADO_FILE       = "estado_bot.json"   # ← MEJORA #2: archivo de persistencia
MAX_SL_CONSECUTIVOS = 3                 # ← MEJORA #3: límite de SL seguidos
META_CAPITAL      = 200.0              # meta de reinversión

LOGO_B64 = ""

# ── MEJORA #2: PERSISTENCIA JSON ─────────────────────────────────────────────
def guardar_estado():
    """Guarda el estado crítico del bot en disco para sobrevivir reinicios."""
    estado = {
        "capital":           st.session_state.capital,
        "capital_inicial":   st.session_state.capital_inicial,
        "en_posicion":       st.session_state.en_posicion,
        "precio_entrada":    st.session_state.precio_entrada,
        "cantidad_comprada": st.session_state.cantidad_comprada,
        "historial":         st.session_state.historial,
        "sl_consecutivos":   st.session_state.get("sl_consecutivos", 0),
        "ultima_senal":      st.session_state.get("ultima_senal", ""),
        "orden_id":          st.session_state.get("orden_id", 0),
        "par_activo":        st.session_state.get("par_activo", ""),
        "auth_ok":           st.session_state.get("auth", False),
    }
    try:
        with open(ESTADO_FILE, "w") as f:
            json.dump(estado, f)
    except Exception as e:
        st.warning(f"⚠️ No se pudo guardar estado: {e}")

def cargar_estado():
    """Carga el estado guardado al arrancar la app."""
    if os.path.exists(ESTADO_FILE):
        try:
            with open(ESTADO_FILE) as f:
                datos = json.load(f)
            st.session_state.capital           = datos.get("capital", 30.0)
            st.session_state.capital_inicial   = datos.get("capital_inicial", 30.0)
            st.session_state.en_posicion       = datos.get("en_posicion", False)
            st.session_state.precio_entrada    = datos.get("precio_entrada", 0.0)
            st.session_state.cantidad_comprada = datos.get("cantidad_comprada", 0.0)
            st.session_state.historial         = datos.get("historial", [])
            st.session_state.sl_consecutivos   = datos.get("sl_consecutivos", 0)
            st.session_state.ultima_senal      = datos.get("ultima_senal", "")
            st.session_state.orden_id          = datos.get("orden_id", 0)
            st.session_state.orden_ciclos      = datos.get("orden_ciclos", 0)
            st.session_state.par_activo        = datos.get("par_activo", "")
            # ── Auto-login tras reconexión WebSocket ─────────────────────────
            if datos.get("auth_ok", False):
                st.session_state.auth = True
        except Exception as e:
            st.warning(f"⚠️ No se pudo cargar estado guardado: {e}")

# Cargar estado antes de init_state para no sobreescribir datos guardados
if "estado_cargado" not in st.session_state:
    cargar_estado()
    st.session_state.estado_cargado = True

# ── COINEX API ────────────────────────────────────────────────────────────────
def _sign(method, path, body, ts):
    msg = method.upper() + path + body + ts
    return hmac.new(COINEX_API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

def _hdrs(method, path, body=""):
    ts = str(int(time_module.time() * 1000))
    return {"Content-Type":      "application/json",
            "X-COINEX-KEY":      COINEX_API_KEY,
            "X-COINEX-SIGN":     _sign(method, path, body, ts),
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
        bd = json.dumps({"market": market, "market_type": "SPOT",
                         "side": "buy", "type": "market",
                         "amount": str(round(usdt, 2))}, separators=(",", ":"))
        r = requests.post(COINEX_BASE + path, headers=_hdrs("POST", path, bd),
                          data=bd, timeout=10)
        return r.json()
    except Exception as e:
        return {"code": -1, "message": str(e)}

def market_sell(market, amount):
    try:
        path = "/spot/order"
        bd = json.dumps({"market": market, "market_type": "SPOT",
                         "side": "sell", "type": "market",
                         "amount": str(round(amount, 8))}, separators=(",", ":"))
        r = requests.post(COINEX_BASE + path, headers=_hdrs("POST", path, bd),
                          data=bd, timeout=10)
        return r.json()
    except Exception as e:
        return {"code": -1, "message": str(e)}

def limit_buy(market, usdt, price):
    """Orden límite de compra — fee maker 0.1% vs taker 0.2%."""
    try:
        path = "/spot/order"
        amount_base = round(usdt / price, 8)   # USDT → moneda base
        bd = json.dumps({
            "market": market, "market_type": "SPOT",
            "side": "buy", "type": "limit",
            "amount": str(amount_base),
            "price":  str(round(price, 8))
        }, separators=(",", ":"))
        r = requests.post(COINEX_BASE + path, headers=_hdrs("POST", path, bd),
                          data=bd, timeout=10)
        return r.json()
    except Exception as e:
        return {"code": -1, "message": str(e)}

def check_order(order_id, market):
    """Consulta si una orden límite fue ejecutada."""
    try:
        path = "/spot/order"
        r = requests.get(COINEX_BASE + path,
                         headers=_hdrs("GET", path),
                         params={"market": market, "order_id": order_id},
                         timeout=10)
        d = r.json()
        return d.get("data", {}) if d.get("code") == 0 else None
    except:
        return None

def cancel_order(order_id, market):
    """Cancela una orden límite pendiente."""
    try:
        path = "/spot/order"
        bd = json.dumps({
            "market": market, "market_type": "SPOT", "order_id": order_id
        }, separators=(",", ":"))
        r = requests.delete(COINEX_BASE + path, headers=_hdrs("DELETE", path, bd),
                            data=bd, timeout=10)
        return r.json()
    except:
        return {"code": -1}

# ── SESSION STATE ─────────────────────────────────────────────────────────────
def init_state():
    defs = {
        "auth":              False,
        "pagina":            "HOME",
        "bot_activo":        False,
        "auto_trading":      True,
        "en_posicion":       False,
        "precio_entrada":    0.0,
        "cantidad_comprada": 0.0,
        "ultima_senal":      "",
        "log":               [],
        "historial":         [],
        "capital":           30.0,
        "capital_inicial":   30.0,
        "sl_consecutivos":   0,      # ← MEJORA #3
        "orden_id":          0,      # ID orden limit pendiente
        "orden_ciclos":      0,      # ciclos esperando fill (máx 3 = 45s)
        "par_activo":        "",     # par seleccionado por el scanner
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
    g =  d.where(d > 0, 0).rolling(p).mean()
    l = -d.where(d < 0, 0).rolling(p).mean()
    return 100 - (100 / (1 + g / l))

def atr(df, p=14):
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(p).mean()

def klines(market, period, limit=80):
    url = f"https://api.coinex.com/v2/spot/kline?market={market}&period={period}&limit={limit}"
    d = requests.get(url, timeout=10).json()["data"]
    df = pd.DataFrame({
        "open":   [float(c["open"])  for c in d],
        "high":   [float(c["high"])  for c in d],
        "low":    [float(c["low"])   for c in d],
        "close":  [float(c["close"]) for c in d],
        "volume": [float(c["value"]) for c in d],
    })
    return df

def add_log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.log.insert(0, f"[{ts}] {msg}")
    if len(st.session_state.log) > 50:
        st.session_state.log = st.session_state.log[:50]

@st.cache_data(ttl=13)
def scan_pares(timeframe="5min", tf_mayor="15min"):
    """Escanea PARES_SCAN cada 13s y devuelve lista ordenada por score.
    Usa iloc[-2] (vela cerrada) para filtros consistentes.
    timeout=5 por petición para no bloquear la UI."""
    resultados = []
    for par in PARES_SCAN:
        try:
            mkt = par.replace("/", "")
            url_k = f"https://api.coinex.com/v2/spot/kline?market={mkt}&period={timeframe}&limit=80"
            r_k = requests.get(url_k, timeout=5)
            if r_k.status_code != 200:
                raise ValueError("HTTP error")
            d = r_k.json().get("data", [])
            if not d:
                raise ValueError("Sin datos")
            df = pd.DataFrame({
                "open":   [float(c["open"])  for c in d],
                "high":   [float(c["high"])  for c in d],
                "low":    [float(c["low"])   for c in d],
                "close":  [float(c["close"]) for c in d],
                "volume": [float(c["value"]) for c in d],
            })
            df["EMA7"]   = df["close"].ewm(span=7).mean()
            df["EMA18"]  = df["close"].ewm(span=18).mean()
            df["RSI"]    = rsi(df["close"], 9)
            df["VOL_MA"] = df["volume"].rolling(14).mean()
            df["ATR"]    = atr(df, 14)
            s_ema7  = df["EMA7"].iloc[-2]
            s_ema18 = df["EMA18"].iloc[-2]
            s_rsi   = df["RSI"].iloc[-2]
            s_rsip  = df["RSI"].iloc[-3]
            s_vol   = df["volume"].iloc[-2]
            s_volma = df["VOL_MA"].iloc[-2]
            s_atr   = df["ATR"].iloc[-2]
            precio  = df["close"].iloc[-1]
            cambio  = ((precio - df["close"].iloc[-2]) / df["close"].iloc[-2]) * 100
            f_ema   = s_ema7 > s_ema18
            rsi_sub = s_rsi > s_rsip
            f_rsi   = (52 < s_rsi < 68) and rsi_sub
            f_vol   = s_vol > s_volma
            f_tend  = False
            if sum([f_ema, f_rsi, f_vol]) >= 1:
                try:
                    url_m = f"https://api.coinex.com/v2/spot/kline?market={mkt}&period={tf_mayor}&limit=30"
                    r_m   = requests.get(url_m, timeout=5)
                    dm    = r_m.json().get("data", [])
                    dfm   = pd.DataFrame({
                        "close": [float(c["close"]) for c in dm],
                        "high":  [float(c["high"])  for c in dm],
                        "low":   [float(c["low"])   for c in dm],
                        "open":  [float(c["open"])  for c in dm],
                        "volume":[float(c["value"]) for c in dm],
                    })
                    dfm["EMA21"] = dfm["close"].ewm(span=21).mean()
                    dfm["EMA50"] = dfm["close"].ewm(span=50).mean()
                    f_tend = (dfm["EMA21"].iloc[-2] > dfm["EMA50"].iloc[-2] and
                              dfm["close"].iloc[-2]  > dfm["EMA21"].iloc[-2])
                except:
                    pass
            f_total   = sum([f_ema, f_rsi, f_vol, f_tend])
            atr_pct   = round((s_atr / precio) * 100, 3) if precio > 0 else 0
            vol_ratio = round(s_vol / s_volma, 2)        if s_volma > 0 else 0
            score     = f_total * 20
            if 52 < s_rsi < 58: score += 5   # RSI temprano = mejor entrada
            if vol_ratio >= 2.0: score += 5   # volumen excepcional
            score += min(atr_pct * 5, 10)      # más movimiento = más oportunidad
            resultados.append({
                "par": par, "precio": precio, "score": round(score, 1),
                "filtros": f_total, "todos": f_total == 4,
                "f_ema": f_ema, "f_rsi": f_rsi, "f_vol": f_vol, "f_tend": f_tend,
                "rsi": round(s_rsi, 1), "rsi_sub": rsi_sub,
                "atr_pct": atr_pct, "vol_ratio": vol_ratio, "cambio": round(cambio, 2),
            })
        except:
            resultados.append({
                "par": par, "precio": 0, "score": -1, "filtros": 0, "todos": False,
                "rsi": 0, "atr_pct": 0, "vol_ratio": 0, "cambio": 0, "error": True,
            })
    return sorted(resultados, key=lambda x: x["score"], reverse=True)

def _render_scanner(scan_data):
    """Renderiza la tabla del scanner de pares."""
    filas = ""
    for r in scan_data:
        if r.get("error"):
            continue
        color_score = "#00e676" if r["todos"] else ("#ffa726" if r["filtros"] >= 2 else "#555")
        color_cambio = "#00e676" if r["cambio"] >= 0 else "#e82929"
        signo = "+" if r["cambio"] >= 0 else ""
        f_ema_c  = "#00e676" if r["f_ema"]  else "#333"
        f_rsi_c  = "#00e676" if r["f_rsi"]  else "#333"
        f_vol_c  = "#00e676" if r["f_vol"]  else "#333"
        f_tend_c = "#00e676" if r["f_tend"] else "#333"
        rsi_dir  = "↑" if r.get("rsi_sub") else "↓"
        filas += (
            f'<div class="scan-row" style="{"background:#0f1a0f;border-left:2px solid #00e676;" if r["todos"] else ""}">'
            f'<span style="font-weight:700;color:#fff;font-size:12px;">{r["par"]}</span>'
            f'<span style="color:{color_score};font-family:JetBrains Mono,monospace;font-size:13px;font-weight:700;">{r["score"]:.0f}</span>'
            f'<span style="color:#ccc;font-size:10px;">'
            f'<span style="color:{f_ema_c};">E</span>'
            f'<span style="color:{f_rsi_c};">R</span>'
            f'<span style="color:{f_vol_c};">V</span>'
            f'<span style="color:{f_tend_c};">T</span>'
            f' {r["filtros"]}/4</span>'
            f'<span style="color:#888;font-size:10px;">{r["rsi"]}{rsi_dir}</span>'
            f'<span style="color:#888;font-size:10px;">{r["atr_pct"]}%</span>'
            f'<span style="color:{color_cambio};font-size:10px;">{signo}{r["cambio"]}%</span>'
            f'</div>'
        )
    st.markdown(
        '<div style="background:#0a0a0a;border:1px solid #1e1e1e;border-radius:10px;padding:10px;margin-bottom:10px;">'
        '<div style="font-size:9px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">'
        '🔍 SCANNER — 9 PARES (vela cerrada 🕯️) — E=EMA R=RSI V=Vol T=Tend</div>'
        '<div style="display:grid;grid-template-columns:75px 45px 60px 40px 48px 52px;'
        'padding:4px 6px;font-size:9px;color:#333;letter-spacing:1px;text-transform:uppercase;">'
        '<span>PAR</span><span>SCORE</span><span>FILTROS</span>'
        '<span>RSI</span><span>ATR%</span><span>CAMBIO</span></div>'
        + filas +
        '</div>',
        unsafe_allow_html=True
    )

# ── MEJORA #5: BARRA DE PROGRESO $30 → $200 ──────────────────────────────────
def render_barra_progreso(capital, capital_ini, meta=200.0):
    progreso = min(((capital - capital_ini) / (meta - capital_ini)) * 100, 100)
    progreso = max(progreso, 0)
    falta    = max(meta - capital, 0)
    ganancia = capital - capital_ini
    sg       = "+" if ganancia >= 0 else ""
    col_prog = "#00e676" if ganancia >= 0 else "#e82929"
    st.markdown(f"""
    <div style="padding:16px;background:#101010;border:1px solid #1e1e1e;
                border-radius:12px;margin-bottom:12px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
            <span style="color:#666;font-size:11px;letter-spacing:1px;">
                🎯 PROGRESO A META $200
            </span>
            <span style="color:#fff;font-size:11px;font-weight:700;">
                ${capital:.2f} / ${meta:.0f} USDT
            </span>
        </div>
        <div style="background:#1e1e1e;border-radius:4px;height:10px;overflow:hidden;">
            <div style="width:{progreso:.1f}%;
                        background:linear-gradient(90deg,#e82929,#ffa726,#00e676);
                        height:10px;border-radius:4px;transition:width .5s;"></div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:6px;">
            <span style="color:{col_prog};font-size:11px;font-weight:700;">
                {sg}${ganancia:.2f} desde inicio
            </span>
            <span style="color:#555;font-size:10px;">
                Faltan ${falta:.2f} para la meta · {progreso:.1f}%
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#080808!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stSidebar"]{display:none!important}
.cs-nav{display:flex;align-items:center;justify-content:space-between;padding:10px 16px;border-bottom:1px solid #1e1e1e;background:#080808;}
.cs-nav-logo{display:flex;align-items:center;gap:10px}
.cs-nav-name{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;letter-spacing:2px;color:#fff}
.cs-nav-name span{color:#e82929}
.cs-pulse{width:7px;height:7px;background:#e82929;border-radius:50%;animation:cspulse 1.4s infinite}
@keyframes cspulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.7)}}
.cs-hero{padding:40px 20px 36px;text-align:center;position:relative;overflow:hidden}
.cs-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(232,41,41,.1);border:1px solid rgba(232,41,41,.2);border-radius:20px;padding:6px 14px;font-size:11px;color:#e82929;letter-spacing:1px;margin-bottom:20px}
.cs-h1{font-family:'Rajdhani',sans-serif;font-size:44px;font-weight:700;line-height:1;color:#fff;margin-bottom:12px}
.cs-sub{color:#e82929;font-size:17px;font-weight:500;margin-bottom:18px}
.cs-desc{color:#666;font-size:14px;line-height:1.7;max-width:360px;margin:0 auto 32px}
.cs-btn-red{display:inline-flex;align-items:center;justify-content:center;gap:8px;background:#e82929;color:#fff;padding:14px 28px;border-radius:10px;font-weight:700;font-size:14px;text-decoration:none}
.cs-btn-outline{display:inline-flex;align-items:center;justify-content:center;background:transparent;border:1px solid #333;color:#888;padding:14px 28px;border-radius:10px;font-size:14px;text-decoration:none}
.cs-btns{display:flex;flex-direction:column;align-items:center;gap:10px}
.cs-strip{display:flex;border-top:1px solid #1e1e1e;border-bottom:1px solid #1e1e1e;background:#0b0b0b}
.cs-icon-item{flex:1;display:flex;flex-direction:column;align-items:center;padding:16px 4px;gap:8px;border-right:1px solid #1e1e1e}
.cs-icon-item:last-child{border-right:none}
.cs-icon-box{width:38px;height:38px;background:rgba(232,41,41,.15);border:1px solid rgba(232,41,41,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px}
.cs-icon-lbl{font-size:8px;color:#666;text-align:center;letter-spacing:.5px;line-height:1.3;text-transform:uppercase}
.cs-stats{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:#1e1e1e}
.cs-stat{background:#080808;padding:22px 12px;text-align:center}
.cs-stat-num{font-family:'Rajdhani',sans-serif;font-size:34px;font-weight:700;color:#fff}
.acc{font-size:16px;color:#666}
.cs-stat-lbl{font-size:10px;color:#666;letter-spacing:1.5px;margin-top:5px;text-transform:uppercase}
.cs-section{padding:44px 20px}
.cs-features{padding:10px 20px 44px}
.cs-feat-tag{color:#e82929;font-size:11px;letter-spacing:3px;font-weight:700;text-transform:uppercase;margin-bottom:8px}
.cs-feat-h2{font-family:'Rajdhani',sans-serif;font-size:30px;font-weight:700;color:#fff;margin-bottom:8px}
.cs-feat-p{color:#666;font-size:14px;line-height:1.6;margin-bottom:24px}
.cs-fcard{background:#101010;border:1px solid #1e1e1e;border-radius:18px;padding:24px;margin-bottom:12px}
.cs-ficon{width:52px;height:52px;background:linear-gradient(135deg,rgba(232,41,41,.2),rgba(232,41,41,.05));border:1px solid rgba(232,41,41,.2);border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:14px}
.cs-fcard h3{font-family:'Rajdhani',sans-serif;font-size:21px;font-weight:700;margin-bottom:8px;color:#fff}
.cs-fcard p{color:#666;font-size:13px;line-height:1.7}
.cs-signal-buy{background:rgba(0,230,118,.08);border:1px solid rgba(0,230,118,.3);border-radius:12px;padding:14px;margin-bottom:8px;color:#00e676;font-weight:700}
.cs-signal-wait{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.3);border-radius:12px;padding:14px;margin-bottom:8px;color:#ffa726;font-weight:700}
.cs-signal-tp{background:rgba(0,230,118,.15);border:2px solid #00e676;border-radius:12px;padding:14px;margin-bottom:8px;color:#00e676;font-weight:700}
.cs-signal-sl{background:rgba(232,41,41,.15);border:2px solid #e82929;border-radius:12px;padding:14px;margin-bottom:8px;color:#e82929;font-weight:700}
.cs-signal-pos{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.3);border-radius:12px;padding:14px;margin-bottom:8px;color:#ffa726;font-weight:700}
.cs-signal-trend{background:rgba(77,166,255,.08);border:1px solid rgba(77,166,255,.3);border-radius:12px;padding:10px 14px;margin-bottom:8px;color:#4da6ff;font-size:12px;font-weight:600}
.cs-signal-pausa{background:rgba(232,41,41,.2);border:2px solid #e82929;border-radius:12px;padding:14px;margin-bottom:8px;color:#e82929;font-weight:700;text-align:center;font-size:15px}
.fee-banner{background:rgba(255,167,38,.08);border:1px solid rgba(255,167,38,.25);border-radius:8px;padding:8px 14px;margin-bottom:8px;font-size:12px;color:#ffa726}
.auto-on{background:rgba(0,230,118,.15);border:1px solid #00e676;border-radius:10px;padding:8px 14px;font-size:12px;color:#00e676;margin-bottom:8px}
.auto-off{background:rgba(255,167,38,.1);border:1px solid #ffa726;border-radius:10px;padding:8px 14px;font-size:12px;color:#ffa726;margin-bottom:8px}
.log-box{background:#0a0a0a;border:1px solid #1e1e1e;border-radius:8px;padding:10px;max-height:160px;overflow-y:auto;font-family:'JetBrains Mono',monospace;font-size:10px}
.log-buy{color:#00e676}.log-sell{color:#e82929}.log-info{color:#4da6ff}
.mt5-quote-bar{background:#111;border-bottom:1px solid #1e1e1e;padding:8px 14px;display:flex;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:8px}
.mt5-symbol{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#fff}
.mt5-price-main{font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:600}
.mt5-price-up{color:#00e676}.mt5-price-dn{color:#e82929}
.mt5-quote-item{text-align:center}
.mt5-quote-lbl{font-size:9px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px}
.mt5-quote-val{font-family:'JetBrains Mono',monospace;font-size:13px;color:#ccc;font-weight:600}
.mt5-rp-section{border-bottom:1px solid #1e1e1e;padding:12px}
.mt5-rp-title{font-size:9px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;font-weight:700}
.mt5-rp-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.mt5-rp-key{font-size:10px;color:#666}
.mt5-rp-val{font-family:'JetBrains Mono',monospace;font-size:11px;color:#ccc;font-weight:600}
.mt5-ind-bar{height:6px;background:#1e1e1e;border-radius:3px;overflow:hidden;margin-top:4px;margin-bottom:8px}
.mt5-ind-fill{height:100%;border-radius:3px;transition:width .3s}
.mt5-buy-btn{background:linear-gradient(135deg,#00b894,#00e676);color:#000;padding:14px;border-radius:10px;font-family:'Rajdhani',sans-serif;font-size:18px;font-weight:700;text-align:center;margin-bottom:8px}
.mt5-btn-sub{font-size:9px;font-weight:400;display:block;opacity:.8}
.mt5-cap-prog{padding:12px;border-bottom:1px solid #1e1e1e}
.mt5-cap-row{display:flex;justify-content:space-between;margin-bottom:6px}
.mt5-cap-lbl{font-size:9px;color:#555;letter-spacing:1px;text-transform:uppercase}
.mt5-prog-out{height:6px;background:#1e1e1e;border-radius:3px;overflow:hidden}
.mt5-prog-in{height:100%;border-radius:3px;transition:width .5s}
.mt5-terminal{background:#0a0a0a;border-top:2px solid #1e1e1e;font-family:'JetBrains Mono',monospace;font-size:10px}
.mt5-term-tabs{display:flex;background:#111;border-bottom:1px solid #1e1e1e}
.mt5-term-tab{padding:8px 16px;font-size:10px;font-weight:600;color:#555;letter-spacing:1px;text-transform:uppercase}
.mt5-term-tab.active{color:#e82929;border-bottom:2px solid #e82929}
.mt5-term-body{padding:0;max-height:180px;overflow-y:auto}
.mt5-term-row{display:grid;grid-template-columns:85px 75px 55px 65px 65px 60px 65px;padding:7px 12px;border-bottom:1px solid #111}
.mt5-term-row:hover{background:#141414}
.mt5-term-hdr{display:grid;grid-template-columns:85px 75px 55px 65px 65px 60px 65px;padding:5px 12px;background:#0f0f0f;color:#444;font-size:9px;text-transform:uppercase;letter-spacing:1px}
.cs-hist-header{background:#0f0f0f;padding:16px 20px;border-bottom:1px solid #1e1e1e;display:flex;justify-content:space-between;align-items:center}
.cs-hist-balance{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#4da6ff}
.cs-hist-balance-lbl{font-size:10px;color:#666;letter-spacing:1px;text-transform:uppercase}
.cs-hist-resumen{display:grid;grid-template-columns:1fr 1fr 1fr;background:#101010;border-bottom:1px solid #1e1e1e}
.cs-hist-stat{padding:14px 12px;text-align:center;border-right:1px solid #1e1e1e}
.cs-hist-stat:last-child{border-right:none}
.cs-hist-stat-num{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700}
.cs-hist-stat-lbl{font-size:9px;color:#666;letter-spacing:1px;text-transform:uppercase;margin-top:4px}
.cs-hist-seccion{padding:12px 16px 6px;background:#0a0a0a}
.cs-hist-seccion-titulo{font-size:11px;font-weight:700;color:#888;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px}
.cs-hist-trade{background:#0f0f0f;border-bottom:1px solid #141414;padding:14px 16px;display:flex;justify-content:space-between;align-items:center}
.cs-hist-trade:hover{background:#141414}
.cs-hist-par{font-weight:700;font-size:14px;color:#fff;margin-bottom:3px}
.cs-hist-tipo{font-size:12px;font-weight:600;color:#4da6ff}
.cs-hist-precios{font-size:11px;color:#555;margin-top:2px;font-family:'JetBrains Mono',monospace}
.cs-hist-ganancia{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700}
.cs-hist-tag{font-size:10px;padding:2px 8px;border-radius:4px;font-weight:700;margin-top:4px;display:inline-block}
.stButton>button{background:#e82929!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:700!important;letter-spacing:1px!important}
.stButton>button:hover{background:#c0392b!important}
[data-testid="stSelectbox"]>div>div{background:#101010!important;border:1px solid #1e1e1e!important}
[data-testid="stNumberInput"]>div>div{background:#101010!important;border:1px solid #1e1e1e!important}
.scan-row{display:grid;grid-template-columns:75px 45px 60px 40px 48px 52px;padding:5px 6px;border-bottom:1px solid #111;align-items:center;}
.scan-row:hover{background:#141414;}
</style>
""", unsafe_allow_html=True)

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if not st.session_state.auth:
    st.markdown(
        '<div style="min-height:100vh;display:flex;align-items:center;justify-content:center;">'
        '<div style="background:#101010;border:1px solid #1e1e1e;border-radius:20px;padding:40px 32px;width:100%;max-width:360px;text-align:center;">'
        '<div style="font-family:Rajdhani,sans-serif;font-size:24px;font-weight:700;letter-spacing:2px;color:#fff;margin-bottom:8px;">CRYPTO<span style="color:#e82929;">SCALPER</span></div>'
        '<div style="color:#666;font-size:13px;margin-bottom:28px;">BOT PRO — Acceso exclusivo</div>'
        '</div></div>',
        unsafe_allow_html=True
    )
    with st.form("login", clear_on_submit=True):
        clave  = st.text_input("", placeholder="Introduce contraseña",
                               type="password", key="login_pwd")
        entrar = st.form_submit_button("ENTRAR", use_container_width=True)
    if entrar:
        if clave == APP_PASSWORD:
            st.session_state.auth = True
            guardar_estado()   # ← persiste auth_ok:True al disco
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# ── CARGAR SALDO REAL DE COINEX (máx. cada 30s para no frenar la navegación) ──
_ahora = time_module.time()
if (COINEX_API_KEY and COINEX_API_SECRET and not st.session_state.en_posicion and
        _ahora - st.session_state.get("_last_bal_ts", 0) > 30):
    saldo = get_balance()
    st.session_state["_last_bal_ts"] = _ahora
    if saldo > 0 and abs(saldo - st.session_state.capital) > 0.01:
        st.session_state.capital = round(saldo, 4)

# ── NAV ───────────────────────────────────────────────────────────────────────
if st.session_state.bot_activo and st.session_state.auto_trading:
    nav_status = "🟢 AUTO"
    nav_color  = "#00e676"
elif st.session_state.bot_activo:
    nav_status = "🟡 MANUAL"
    nav_color  = "#ffa726"
else:
    nav_status = "⚫ INACTIVO"
    nav_color  = "#555"

st.markdown(
    f'<div class="cs-nav">'
    f'<div class="cs-nav-logo">'
    f'<div class="cs-nav-name">CRYPTO<span>SCALPER</span></div></div>'
    f'<div style="font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;color:{nav_color};">'
    f'{nav_status}</div>'
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

pagina  = st.session_state.pagina
cap     = st.session_state.capital
cap_ini = st.session_state.capital_inicial

# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if pagina == "HOME":
    # Barra de progreso en HOME
    render_barra_progreso(cap, cap_ini)

    st.markdown(
        '<div class="cs-hero">'
        '<div class="cs-badge"><span class="cs-pulse"></span> Sistema operando en vivo</div>'
        '<div class="cs-h1">Trading Automatico<br>de Precision</div>'
        '<div class="cs-sub">Opera solo en CoinEx 24/7</div>'
        '<div class="cs-desc">4 filtros + ATR dinamico + ejecucion automatica de ordenes. Sin intervención manual.</div>'
        '<div class="cs-btns"><a class="cs-btn-red" href="#">Comenzar Ahora</a>'
        '<a class="cs-btn-outline" href="#">Ver Historial</a></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-strip">'
        '<div class="cs-icon-item"><div class="cs-icon-box">🤖</div><div class="cs-icon-lbl">AUTO TRADING</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">📊</div><div class="cs-icon-lbl">4 FILTROS</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">🎯</div><div class="cs-icon-lbl">ATR DINÁMICO</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">💰</div><div class="cs-icon-lbl">COMISIONES</div></div>'
        '<div class="cs-icon-item"><div class="cs-icon-box">📱</div><div class="cs-icon-lbl">TELEGRAM</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    hist   = st.session_state.historial
    total  = len(hist)
    gan    = len([t for t in hist if t["resultado"] == "TP"])
    wr     = round((gan / total) * 100) if total > 0 else 0

    st.markdown(
        '<div class="cs-stats">'
        f'<div class="cs-stat"><div class="cs-stat-num">{total}</div><div class="cs-stat-lbl">Trades</div></div>'
        f'<div class="cs-stat"><div class="cs-stat-num">{cap:.2f} <span class="acc">USDT</span></div><div class="cs-stat-lbl">Capital</div></div>'
        f'<div class="cs-stat"><div class="cs-stat-num">{wr}<span class="acc">%</span></div><div class="cs-stat-lbl">Win Rate</div></div>'
        f'<div class="cs-stat"><div class="cs-stat-num">{round(cap - cap_ini, 2):+.2f}<span class="acc">$</span></div><div class="cs-stat-lbl">P&L Total</div></div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="cs-features"><div style="text-align:center;margin-bottom:26px;">'
        '<div class="cs-feat-tag">TECNOLOGIA AUTOMATICA</div>'
        '<div class="cs-feat-h2">Bot opera solo en CoinEx</div>'
        '<div class="cs-feat-p">Detecta señal → compra solo → monitorea → vende solo al TP o SL</div>'
        '</div>'
        '<div class="cs-fcard"><div class="cs-ficon">🤖</div><h3>Trading 100% Automatico</h3><p>El bot ejecuta compras y ventas sin intervención manual en tiempo real.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📊</div><h3>4 Filtros de Calidad</h3><p>EMA, RSI con dirección, Volumen y Tendencia mayor para entradas de alta probabilidad.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">🎯</div><h3>TP/SL con ATR Dinamico</h3><p>Los niveles de salida se adaptan a la volatilidad real del mercado en cada momento.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">💰</div><h3>Comisiones CoinEx Incluidas</h3><p>0.4% por trade ya descontado en todos los cálculos de ganancia neta.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">💵</div><h3>Reinversion Automatica</h3><p>Cada ganancia se reinvierte automáticamente. Meta: $30 → $200.</p></div>'
        '<div class="cs-fcard"><div class="cs-ficon">📱</div><h3>Alertas Telegram</h3><p>Notificaciones en tiempo real de cada compra, venta y señal detectada.</p></div>'
        '</div>',
        unsafe_allow_html=True
    )

# ══════════════════════════════════════════════════════════════════════════════
# LIVE TRADING
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "LIVE":

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        crypto = st.selectbox("Par (o deja que el scanner elija)", PARES_SCAN, key="sel_par")
    with col2:
        timeframe = st.selectbox("TF entrada",  ["5min","3min","1min"], key="sel_tf")
    with col3:
        tf_mayor  = st.selectbox("TF tendencia", ["15min","5min","1hour"], key="sel_tfm")

    st.markdown(
        '<div class="fee-banner">💡 Comisión CoinEx: 0.3% por trade (0.1% limit buy maker + 0.2% market sell) — ya incluida en cálculos</div>',
        unsafe_allow_html=True
    )

    # ── MEJORA #3: Alerta de pausa por SL consecutivos ───────────────────────
    sl_consec = st.session_state.get("sl_consecutivos", 0)
    if sl_consec >= MAX_SL_CONSECUTIVOS:
        st.markdown(
            f'<div class="cs-signal-pausa">⛔ BOT PAUSADO — {sl_consec} SL consecutivos detectados.<br>'
            '<span style="font-size:12px;font-weight:400;">Revisa el mercado manualmente antes de reanudar.</span></div>',
            unsafe_allow_html=True
        )
        if st.button("🔄 Reanudar bot manualmente", use_container_width=True):
            st.session_state.sl_consecutivos = 0
            guardar_estado()
            st.rerun()
        st.stop()

    # Barra de progreso en LIVE
    render_barra_progreso(cap, cap_ini)

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("▶ INICIAR BOT", use_container_width=True, key="bi"):
            st.session_state.bot_activo = True
            add_log("✅ Bot iniciado en modo AUTO")
            telegram(f"🤖 CRYPTOSCALPER iniciado\nModo: AUTOMATICO\nScanner: {len(PARES_SCAN)} pares | TF: {timeframe}")
    with b2:
        if st.button("⏹ DETENER BOT", use_container_width=True, key="bd"):
            mkt_stop = st.session_state.get("par_activo", crypto)
            mkt_stop = mkt_stop.replace("/", "") if mkt_stop else crypto.replace("/", "")
            if st.session_state.en_posicion and st.session_state.cantidad_comprada > 0:
                market_sell(mkt_stop, st.session_state.cantidad_comprada)
                add_log("⚠️ Bot detenido — posicion cerrada manualmente")
            st.session_state.bot_activo        = False
            st.session_state.en_posicion       = False
            st.session_state.cantidad_comprada = 0.0
            guardar_estado()   # ← MEJORA #2
            telegram("⏹ CRYPTOSCALPER detenido.")
    with b3:
        modo_lbl = "🟢 AUTO: ON  (click = OFF)" if st.session_state.auto_trading else "🟡 MANUAL (click = AUTO)"
        if st.button(modo_lbl, use_container_width=True, key="bm"):
            st.session_state.auto_trading = not st.session_state.auto_trading

    modo_html = '<div class="auto-on">🟢 MODO AUTOMÁTICO — El bot compra y vende solo</div>' \
        if st.session_state.auto_trading else \
        '<div class="auto-off">🟡 MODO MANUAL — Solo envía señales por Telegram</div>'
    st.markdown(modo_html, unsafe_allow_html=True)

    if not st.session_state.bot_activo:
        st.markdown('<div style="text-align:center;color:#444;padding:60px 20px;font-size:15px;">Bot inactivo. Pulsa INICIAR BOT para comenzar.</div>', unsafe_allow_html=True)

        # ── SCANNER — visible aunque el bot esté inactivo ────────────────────
        st.markdown('<div style="font-size:10px;color:#555;letter-spacing:2px;text-transform:uppercase;padding:8px 0 4px;">🔍 SCANNER DE PARES (actualiza al pulsar INICIAR)</div>', unsafe_allow_html=True)
        try:
            scan_data = scan_pares(timeframe, tf_mayor)
            _render_scanner(scan_data)
        except:
            pass
    else:
        st_autorefresh(interval=15000, limit=None, key="ar")

        scan_data = []
        # ── SCANNER: escanear los 9 pares y mostrar tabla ─────────────────────
        _scan_slot = st.empty()
        try:
            scan_data = scan_pares(timeframe, tf_mayor)
            with _scan_slot:
                _render_scanner(scan_data)
            # Auto-selección: si el scanner encuentra señal perfecta (4/4) y no
            # estamos en posición, el bot usa ese par automáticamente
            if not st.session_state.en_posicion:
                mejor = scan_data[0]
                if mejor["todos"] and mejor["par"] != st.session_state.get("par_activo", ""):
                    st.session_state.par_activo = mejor["par"]
                    add_log(f"🔍 SCANNER → mejor par: {mejor['par']} (score {mejor['score']})")
        except Exception as _se:
            _scan_slot.markdown(
                '<div style="color:#555;font-size:11px;padding:6px;">⚠️ Scanner no disponible en este ciclo — reintentará en 15s</div>',
                unsafe_allow_html=True
            )

        # Par efectivo: usar el seleccionado por scanner si hay señal 4/4,
        # si no, usar el que el usuario eligió manualmente en el selectbox
        par_scanner   = st.session_state.get("par_activo", "")
        usar_scanner  = (par_scanner != "" and
                         not st.session_state.en_posicion and
                         any(r["par"] == par_scanner and r["todos"] for r in scan_data))
        crypto_op     = par_scanner if usar_scanner else crypto
        if usar_scanner:
            st.markdown(
                f'<div style="background:rgba(0,230,118,.1);border:1px solid #00e676;border-radius:8px;'
                f'padding:8px 14px;font-size:12px;color:#00e676;margin-bottom:6px;">'
                f'🔍 SCANNER: operando en <b>{crypto_op}</b> (mejor señal automática)</div>',
                unsafe_allow_html=True
            )
        market = crypto_op.replace("/", "")
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
            rsi_prev = df["RSI"].iloc[-2]          # ← MEJORA #6 RSI dirección
            vol_v    = df["volume"].iloc[-1]
            volma_v  = df["VOL_MA"].iloc[-1]
            atr_v    = df["ATR"].iloc[-1]
            cambio_p = ((precio - prev) / prev) * 100
            soporte  = df["low"].tail(20).min()
            resist   = df["high"].tail(20).max()

            # ── VELA CERRADA: variables para evaluación de señales ───────────
            # iloc[-2] = última vela YA CERRADA (no la que está formándose)
            sig_ema7  = df["EMA7"].iloc[-2]
            sig_ema18 = df["EMA18"].iloc[-2]
            sig_rsi   = df["RSI"].iloc[-2]
            sig_rsip  = df["RSI"].iloc[-3]   # RSI anterior → detecta dirección
            sig_vol   = df["volume"].iloc[-2]
            sig_volma = df["VOL_MA"].iloc[-2]
            sig_atr   = df["ATR"].iloc[-2]   # ATR de vela cerrada para TP/SL

            # Tendencia mayor
            try:
                dfm = klines(market, tf_mayor, 30)
                dfm["EMA21"] = dfm["close"].ewm(span=21).mean()
                dfm["EMA50"] = dfm["close"].ewm(span=50).mean()
                tend_ok  = (dfm["EMA21"].iloc[-2] > dfm["EMA50"].iloc[-2] and
                            dfm["close"].iloc[-2] > dfm["EMA21"].iloc[-2])
                tend_str = f"✅ ALCISTA ({tf_mayor})" if tend_ok else f"❌ BAJISTA ({tf_mayor})"
                tend_col = "#00e676" if tend_ok else "#e82929"
            except:
                tend_ok  = False
                tend_str = "⚠️ Error tendencia"
                tend_col = "#ffa726"

            # ── 4 FILTROS (confirmados en vela CERRADA) ──────────────────────
            f_ema  = sig_ema7 > sig_ema18
            # RSI rango ampliado + subiendo — evaluado en vela cerrada
            rsi_subiendo = sig_rsi > sig_rsip
            f_rsi  = (52 < sig_rsi < 68) and rsi_subiendo
            f_vol  = sig_vol > sig_volma
            f_tend = tend_ok
            f_ok   = sum([f_ema, f_rsi, f_vol, f_tend])
            todos  = f_ema and f_rsi and f_vol and f_tend

            # ATR dinámico TP/SL — live para display, cerrada para TP/SL
            atr_pct    = (atr_v / precio) * 100         # display (vela live)
            sig_atrpct = (sig_atr / precio) * 100       # señal (vela cerrada)
            tp_pct   = max(sig_atrpct * 1.5, 1.8)
            sl_pct   = max(sig_atrpct * 0.8, 0.9)
            neto_tp  = tp_pct - (COMISION * 100)
            neto_sl  = -(sl_pct + COMISION * 100)
            precio_tp = precio * (1 + tp_pct / 100)
            precio_sl = precio * (1 - sl_pct / 100)
            capital_op = st.session_state.capital

            # ── Quote bar ────────────────────────────────────────────────────
            pc = "mt5-price-up" if cambio_p >= 0 else "mt5-price-dn"
            sc = "▲" if cambio_p >= 0 else "▼"
            st.markdown(
                f'<div class="mt5-quote-bar">'
                f'<div><div class="mt5-symbol">{crypto_op}</div>'
                f'<div style="font-size:10px;color:#555;">SL CONSECUTIVOS: '
                f'<span style="color:{"#e82929" if sl_consec>0 else "#555"};">{sl_consec}/{MAX_SL_CONSECUTIVOS}</span></div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">PRECIO</div>'
                f'<div class="mt5-price-main {pc}">{sc} {precio:,.4f}</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">ATR%</div>'
                f'<div class="mt5-quote-val">{atr_pct:.3f}%</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">TP DIN.</div>'
                f'<div class="mt5-quote-val" style="color:#00e676;">+{tp_pct:.2f}%</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">SL DIN.</div>'
                f'<div class="mt5-quote-val" style="color:#e82929;">-{sl_pct:.2f}%</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">NETO TP</div>'
                f'<div class="mt5-quote-val" style="color:#00e676;">+{neto_tp:.2f}%</div></div>'
                f'<div class="mt5-quote-item"><div class="mt5-quote-lbl">CAPITAL</div>'
                f'<div class="mt5-quote-val" style="color:#4da6ff;">${capital_op:.2f}</div></div>'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="cs-signal-trend">TENDENCIA {tf_mayor.upper()}: '
                f'<span style="color:{tend_col};">{tend_str}</span></div>',
                unsafe_allow_html=True
            )

            col_chart, col_right = st.columns([4, 1])

            with col_right:
                # Capital progress
                prog      = min((capital_op / META_CAPITAL) * 100, 100)
                cprog_col = "#00e676" if capital_op >= cap_ini else "#e82929"
                gan_u     = capital_op - cap_ini
                sg        = "+" if gan_u >= 0 else ""
                st.markdown(
                    f'<div class="mt5-cap-prog">'
                    f'<div class="mt5-cap-row"><span class="mt5-cap-lbl">CAPITAL COINEX</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:12px;color:#4da6ff;">${capital_op:.2f}</span></div>'
                    f'<div class="mt5-prog-out"><div class="mt5-prog-in" style="width:{prog:.1f}%;'
                    f'background:{cprog_col};"></div></div>'
                    f'<div style="display:flex;justify-content:space-between;margin-top:4px;">'
                    f'<span style="font-size:9px;color:#555;">${cap_ini:.0f}</span>'
                    f'<span style="font-size:9px;color:#555;">${META_CAPITAL:.0f}</span></div>'
                    f'<div style="margin-top:8px;font-size:10px;color:#666;">P&L: '
                    f'<span style="color:{cprog_col};font-weight:700;">{sg}${gan_u:.2f}</span></div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # Indicadores
                rsi_col = "#00e676" if f_rsi else ("#e82929" if sig_rsi > 68 else "#ffa726")
                vol_col = "#00e676" if f_vol else "#e82929"
                vol_pct = min((vol_v / volma_v * 50) if volma_v > 0 else 50, 100)
                rsi_dir = "↑" if rsi_subiendo else "↓"   # ← MEJORA #6 indicador visual
                st.markdown(
                    f'<div class="mt5-rp-section"><div class="mt5-rp-title">INDICADORES</div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 7</span>'
                    f'<span class="mt5-rp-val">{ema7_v:.4f}</span></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">EMA 18</span>'
                    f'<span class="mt5-rp-val">{ema18_v:.4f}</span></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">RSI(9) {rsi_dir}</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    f'color:{rsi_col};font-weight:600;">{rsi_v:.1f}</span></div>'
                    f'<div class="mt5-ind-bar"><div class="mt5-ind-fill" '
                    f'style="width:{min(rsi_v,100):.0f}%;background:{rsi_col};"></div></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">Vol/MA</span>'
                    f'<span style="font-family:JetBrains Mono,monospace;font-size:11px;'
                    f'color:{vol_col};font-weight:600;">{vol_v/volma_v:.2f}x</span></div>'
                    f'<div class="mt5-ind-bar"><div class="mt5-ind-fill" '
                    f'style="width:{vol_pct:.0f}%;background:{vol_col};"></div></div>'
                    f'<div class="mt5-rp-row"><span class="mt5-rp-key">ATR%</span>'
                    f'<span class="mt5-rp-val">{atr_pct:.3f}%</span></div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                # 4 Filtros
                def fr(ok, lbl):
                    c = "#00e676" if ok else "#e82929"
                    i = "✓" if ok else "✗"
                    return (f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:5px;">'
                            f'<span style="color:{c};font-weight:700;">{i}</span>'
                            f'<span style="font-size:10px;color:#888;">{lbl}</span></div>')

                sc2 = "#00e676" if todos else ("#ffa726" if f_ok >= 2 else "#e82929")
                st.markdown(
                    f'<div class="mt5-rp-section"><div class="mt5-rp-title">'
                    f'<span style="color:{sc2};">FILTROS ({f_ok}/4)</span></div>'
                    + fr(f_ema,  "EMA 7 > EMA 18")
                    + fr(f_rsi,  f"RSI 52-68 {rsi_dir} ({sig_rsi:.0f}🕯️)")
                    + fr(f_vol,  "Vol > Media")
                    + fr(f_tend, f"Tend. {tf_mayor}")
                    + '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f'<div style="padding:12px;">'
                    f'<div class="mt5-buy-btn">BUY'
                    f'<span class="mt5-btn-sub">TP {precio_tp:,.4f} (+{tp_pct:.2f}%)</span>'
                    f'<span class="mt5-btn-sub">SL {precio_sl:,.4f} (-{sl_pct:.2f}%)</span>'
                    f'<span class="mt5-btn-sub" style="color:rgba(0,0,0,.6);">Neto: +{neto_tp:.2f}%</span>'
                    '</div></div>',
                    unsafe_allow_html=True
                )

            with col_chart:
                # ── LÓGICA DE TRADING AUTOMÁTICO ─────────────────────────────
                if st.session_state.en_posicion:
                    if st.session_state.precio_entrada == 0.0:
                        st.session_state.precio_entrada = precio

                    entrada  = st.session_state.precio_entrada
                    qty      = st.session_state.cantidad_comprada
                    ganp     = ((precio - entrada) / entrada) * 100
                    p_tp     = entrada * (1 + tp_pct / 100)
                    p_sl     = entrada * (1 - sl_pct / 100)
                    pnl_neto = ganp - (COMISION * 100)
                    color_pnl = "#00e676" if ganp >= 0 else "#e82929"
                    dist_tp  = ((p_tp - precio) / precio) * 100
                    dist_sl  = ((precio - p_sl) / precio) * 100

                    if precio >= p_tp:
                        st.markdown('<div class="cs-signal-tp">✅ TAKE PROFIT — VENDIENDO...</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "TP":
                            st.session_state.ultima_senal = "TP"
                            if st.session_state.auto_trading and qty > 0:
                                res = market_sell(market, qty)
                                if res.get("code") == 0:
                                    add_log(f"✅ VENTA AUTO TP — {crypto_op} — {qty:.6f} unidades")
                                else:
                                    add_log(f"❌ Error venta TP: {res.get('message')}")
                            gan_real  = tp_pct - (COMISION * 100)
                            nuevo_cap = round(capital_op * (1 + gan_real / 100), 4)
                            st.session_state.capital           = nuevo_cap
                            st.session_state.sl_consecutivos   = 0          # ← MEJORA #3: resetear contador
                            st.session_state.historial.insert(0, {
                                "fecha":        datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par":          crypto_op, "tipo": "AUTO",
                                "entrada":      round(entrada, 4),
                                "salida":       round(precio, 4),
                                "pnl":          round(gan_real, 2),
                                "comision":     0.3,
                                "resultado":    "TP",
                                "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_cap,
                            })
                            st.session_state.en_posicion       = False
                            st.session_state.precio_entrada    = 0.0
                            st.session_state.cantidad_comprada = 0.0
                            guardar_estado()   # ← MEJORA #2
                            telegram(f"✅ TAKE PROFIT AUTO\nPar: {crypto_op}\nGanancia bruta: +{tp_pct:.2f}%\nNeto: +{gan_real:.2f}%\nCapital nuevo: ${nuevo_cap:.2f}")

                    elif precio <= p_sl:
                        st.markdown('<div class="cs-signal-sl">🔴 STOP LOSS — VENDIENDO...</div>', unsafe_allow_html=True)
                        if st.session_state.ultima_senal != "SL":
                            st.session_state.ultima_senal = "SL"
                            if st.session_state.auto_trading and qty > 0:
                                res = market_sell(market, qty)
                                if res.get("code") == 0:
                                    add_log(f"🔴 VENTA AUTO SL — {crypto_op} — {qty:.6f} unidades")
                                else:
                                    add_log(f"❌ Error venta SL: {res.get('message')}")
                            perd_real = -(sl_pct + COMISION * 100)
                            nuevo_cap = round(capital_op * (1 + perd_real / 100), 4)
                            st.session_state.capital           = nuevo_cap
                            # ── MEJORA #3: incrementar contador SL ───────────
                            st.session_state.sl_consecutivos  += 1
                            st.session_state.historial.insert(0, {
                                "fecha":        datetime.now().strftime("%d/%m/%y %H:%M"),
                                "par":          crypto_op, "tipo": "AUTO",
                                "entrada":      round(entrada, 4),
                                "salida":       round(precio, 4),
                                "pnl":          round(perd_real, 2),
                                "comision":     0.3,
                                "resultado":    "SL",
                                "capital_usado": round(capital_op, 2),
                                "capital_nuevo": nuevo_cap,
                            })
                            st.session_state.en_posicion       = False
                            st.session_state.precio_entrada    = 0.0
                            st.session_state.cantidad_comprada = 0.0
                            guardar_estado()   # ← MEJORA #2
                            telegram(f"🔴 STOP LOSS AUTO\nPar: {crypto_op}\nPérdida bruta: -{sl_pct:.2f}%\nCapital nuevo: ${nuevo_cap:.2f}\n⚠️ SL consecutivos: {st.session_state.sl_consecutivos}/{MAX_SL_CONSECUTIVOS}")
                            # Pausa automática si se alcanza el límite
                            if st.session_state.sl_consecutivos >= MAX_SL_CONSECUTIVOS:
                                st.session_state.bot_activo = False
                                guardar_estado()
                                telegram(f"⛔ BOT PAUSADO AUTOMÁTICAMENTE\n{MAX_SL_CONSECUTIVOS} SL consecutivos.\nRevisa el mercado y reanuda manualmente.")
                                st.rerun()
                    else:
                        gan_usdt = capital_op * pnl_neto / 100
                        st.markdown(
                            f'<div class="cs-signal-pos">EN POSICIÓN — P&L: '
                            f'<span style="color:{color_pnl};font-weight:700;">{pnl_neto:+.2f}% (${gan_usdt:+.2f})</span><br>'
                            f'TP a {dist_tp:.2f}% &nbsp;|&nbsp; SL a {dist_sl:.2f}%</div>',
                            unsafe_allow_html=True
                        )
                else:
                    # Sin posición — buscar señal
                    if todos:
                        gan_esperada = round(capital_op * neto_tp / 100, 4)
                        st.markdown(
                            f'<div class="cs-signal-buy">⚡ SEÑAL: COMPRA AHORA<br>'
                            f'<span style="font-size:13px;">TP: {precio_tp:,.4f} | SL: {precio_sl:,.4f} | '
                            f'Ganancia esperada: +${gan_esperada:.4f}</span></div>',
                            unsafe_allow_html=True
                        )
                        if st.session_state.ultima_senal != "COMPRA":
                            st.session_state.ultima_senal = "COMPRA"
                            if st.session_state.auto_trading:
                                # ── LIMIT BUY: precio límite = precio actual + 0.03%
                                # para asegurar fill rápido con fee maker (0.1%)
                                precio_limite = round(precio * 1.0003, 8)
                                res = limit_buy(market, capital_op, precio_limite)
                                if res.get("code") == 0:
                                    data_ord = res.get("data", {})
                                    order_id = data_ord.get("order_id", 0)
                                    qty_comp = float(data_ord.get("base_fill_amount",
                                                     data_ord.get("amount", 0)))
                                    if qty_comp == 0:
                                        qty_comp = capital_op / precio_limite
                                    st.session_state.en_posicion       = True
                                    st.session_state.precio_entrada    = precio_limite
                                    st.session_state.cantidad_comprada = qty_comp
                                    st.session_state.orden_id          = order_id
                                    st.session_state.orden_ciclos      = 0
                                    guardar_estado()
                                    add_log(f"🛒 LIMIT BUY — {crypto_op} @ {precio_limite:.4f} — {qty_comp:.6f} u.")
                                    telegram(
                                        f"🛒 LIMIT BUY (maker)\nPar: {crypto_op}\nPrecio límite: {precio_limite:.4f}\n"
                                        f"Capital: {capital_op:.2f} USDT\nCantidad: {qty_comp:.6f}\n"
                                        f"TP: {precio_tp:.4f} (+{tp_pct:.2f}%)\n"
                                        f"SL: {precio_sl:.4f} (-{sl_pct:.2f}%)\n"
                                        f"Fee: 0.1% maker | Neto esperado: +{neto_tp:.2f}%"
                                    )
                                else:
                                    add_log(f"❌ Error limit buy: {res.get('message')}")
                            else:
                                telegram(
                                    f"⚡ SEÑAL MANUAL\nPar: {crypto_op}\nPrecio: {precio:.4f}\n"
                                    f"TP: {precio_tp:.4f} | SL: {precio_sl:.4f}\n"
                                    f"Neto esperado: +{neto_tp:.2f}%"
                                )
                    else:
                        st.markdown(
                            f'<div class="cs-signal-wait">⏳ ESPERANDO SEÑAL — {f_ok}/4 filtros activos</div>',
                            unsafe_allow_html=True
                        )

                # ── Gráfico ───────────────────────────────────────────────────
                fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                                    row_heights=[0.60, 0.20, 0.20], vertical_spacing=0.01)
                fig.add_trace(go.Candlestick(
                    x=df.index, open=df["open"], high=df["high"],
                    low=df["low"], close=df["close"],
                    increasing=dict(line=dict(color="#00e676"), fillcolor="#00e676"),
                    decreasing=dict(line=dict(color="#e82929"), fillcolor="#e82929"),
                    name="Precio"), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA7"], mode="lines",
                    name="EMA7", line=dict(color="#e82929", width=1.5)), row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["EMA18"], mode="lines",
                    name="EMA18", line=dict(color="#ffa726", width=1.5)), row=1, col=1)
                if st.session_state.en_posicion and st.session_state.precio_entrada > 0:
                    ep = st.session_state.precio_entrada
                    fig.add_hline(y=ep*(1+tp_pct/100), line_color="#00e676", line_dash="dash", annotation_text="TP", row=1, col=1)
                    fig.add_hline(y=ep*(1-sl_pct/100), line_color="#e82929", line_dash="dash", annotation_text="SL", row=1, col=1)
                    fig.add_hline(y=ep, line_color="#4da6ff", line_dash="dot", line_width=1, annotation_text="ENTRADA", row=1, col=1)
                fig.add_hline(y=soporte, line_dash="dot", line_color="#00e676", annotation_text="Soporte", row=1, col=1)
                fig.add_hline(y=resist,  line_dash="dot", line_color="#e82929", annotation_text="Resist",  row=1, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], fill="tozeroy",
                    fillcolor="rgba(232,41,41,0.05)", line=dict(color="#e82929", width=1), name="RSI"), row=2, col=1)
                fig.add_hline(y=52, line_color="#00e676", line_width=0.7, line_dash="dot", row=2, col=1)
                fig.add_hline(y=68, line_color="#e82929", line_width=0.7, line_dash="dot", row=2, col=1)
                cv = ["#00e676" if c >= o else "#e82929" for c, o in zip(df["close"], df["open"])]
                fig.add_trace(go.Bar(x=df.index, y=df["volume"], marker_color=cv, name="Vol"), row=3, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["VOL_MA"], mode="lines",
                    line=dict(color="#ffa726", width=1), name="Vol MA"), row=3, col=1)
                fig.update_layout(
                    height=500, paper_bgcolor="#080808", plot_bgcolor="#0c0c0c",
                    xaxis=dict(showgrid=False, color="#333"),
                    xaxis2=dict(showgrid=False, color="#333"),
                    xaxis3=dict(showgrid=False, color="#333"),
                    yaxis=dict(showgrid=True, gridcolor="#141414", color="#555"),
                    yaxis2=dict(showgrid=True, gridcolor="#141414", color="#555", title="RSI"),
                    yaxis3=dict(showgrid=True, gridcolor="#141414", color="#555", title="Vol"),
                    xaxis_rangeslider_visible=False,
                    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#666"), orientation="h"),
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)

                # ── Terminal + Log ────────────────────────────────────────────
                hist_r = st.session_state.historial[:8]
                rows_t = ""
                if hist_r:
                    rows_t += '<div class="mt5-term-hdr"><span>FECHA</span><span>PAR</span><span>TIPO</span><span>ENTRADA</span><span>SALIDA</span><span>P&L</span><span>CAPITAL</span></div>'
                    for t in hist_r:
                        pc2 = "#00e676" if t["pnl"] >= 0 else "#e82929"
                        sg2 = "+" if t["pnl"] >= 0 else ""
                        rows_t += (
                            f'<div class="mt5-term-row">'
                            f'<span>{t["fecha"]}</span>'
                            f'<span style="color:#fff;font-weight:700;">{t["par"]}</span>'
                            f'<span style="color:#4da6ff;">{t["tipo"]}</span>'
                            f'<span>{t["entrada"]}</span><span>{t["salida"]}</span>'
                            f'<span style="color:{pc2};font-weight:700;">{sg2}{t["pnl"]}%</span>'
                            f'<span style="color:#4da6ff;">{t.get("capital_nuevo","—")}</span>'
                            '</div>'
                        )
                else:
                    rows_t = '<div style="padding:20px;color:#444;text-align:center;font-size:12px;">Sin trades aún</div>'

                st.markdown(
                    '<div class="mt5-terminal">'
                    '<div class="mt5-term-tabs"><div class="mt5-term-tab active">📋 Historial (P&L)</div></div>'
                    '<div class="mt5-term-body">' + rows_t + '</div></div>',
                    unsafe_allow_html=True
                )

                if st.session_state.log:
                    log_html = "".join(
                        f'<div class="log-{"buy" if "COMPRA" in l else "sell" if "VENTA" in l or "SL" in l else "info"}">{l}</div>'
                        for l in st.session_state.log[:10]
                    )
                    st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)

                modo_txt = "AUTO 🟢" if st.session_state.auto_trading else "MANUAL 🟡"
                st.success(f"🟢 Bot activo | {crypto_op} | TP: {tp_pct:.2f}% | SL: {sl_pct:.2f}% | Neto: +{neto_tp:.2f}% | Modo: {modo_txt}")

        except Exception as e:
            st.error(f"Error: {e}")
            add_log(f"❌ Error: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# HISTORIAL
# ══════════════════════════════════════════════════════════════════════════════
elif pagina == "HISTORIAL":
    # Barra de progreso en HISTORIAL
    render_barra_progreso(cap, cap_ini)

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
            '<div class="cs-hist-header">'
            f'<div><div class="cs-hist-balance-lbl">CAPITAL ACTUAL (COINEX)</div>'
            f'<div class="cs-hist-balance">{cap_a:.2f} USDT</div>'
            f'<div style="font-size:11px;color:{cgan};">{sg3}{gan_u:.2f} USDT desde inicio</div>'
            f'<div style="font-size:10px;color:#555;margin-top:3px;">Comisiones pagadas: -${com_t:.2f}</div></div>'
            f'<div style="text-align:right;"><div class="cs-hist-balance-lbl">WIN RATE</div>'
            f'<div style="font-family:Rajdhani,sans-serif;font-size:22px;font-weight:700;color:{cwr};">{wr}%</div>'
            f'<div style="font-size:11px;color:{cpnl};">P&L neto: {("+" if pnl_t>=0 else "")}{pnl_t}%</div>'
            '</div></div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="cs-hist-resumen">'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num">{total}</div><div class="cs-hist-stat-lbl">Trades</div></div>'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#00e676;">{gans}</div><div class="cs-hist-stat-lbl">TP</div></div>'
            f'<div class="cs-hist-stat"><div class="cs-hist-stat-num" style="color:#e82929;">{total-gans}</div><div class="cs-hist-stat-lbl">SL</div></div>'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown('<div class="cs-hist-seccion"><div class="cs-hist-seccion-titulo">Operaciones</div></div>', unsafe_allow_html=True)
        html_t = ""
        for t in historial:
            es_tp = t["resultado"] == "TP"
            cg    = "#00e676" if t["pnl"] >= 0 else "#e82929"
            pd_   = ("+" if t["pnl"] >= 0 else "") + str(t["pnl"]) + "%"
            tc    = "rgba(0,230,118,0.15)" if es_tp else "rgba(232,41,41,0.15)"
            tt    = "#00e676" if es_tp else "#e82929"
            html_t += (
                f'<div class="cs-hist-trade"><div style="flex:1;">'
                f'<div class="cs-hist-par">{t["par"]} <span class="cs-hist-tipo">{t["tipo"]}</span></div>'
                f'<div class="cs-hist-precios">{t["entrada"]} → {t["salida"]}</div>'
                f'<div style="font-size:10px;color:#444;margin-top:2px;">Cap usado: ${t.get("capital_usado","—")} → ${t.get("capital_nuevo","—")}</div>'
                f'</div><div style="text-align:right;">'
                f'<div class="cs-hist-ganancia" style="color:{cg};">{pd_}</div>'
                f'<div style="font-size:9px;color:#555;">neto</div>'
                f'<div class="cs-hist-tag" style="background:{tc};color:{tt};">{t["resultado"]}</div>'
                '</div></div>'
            )
        st.markdown(html_t, unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        with r1:
            if st.button("🗑️ Limpiar historial", use_container_width=True):
                st.session_state.historial = []
                guardar_estado()   # ← MEJORA #2
                st.rerun()
        with r2:
            if st.button("🔄 Resetear capital a $30", use_container_width=True):
                st.session_state.capital         = 30.0
                st.session_state.capital_inicial = 30.0
                st.session_state.sl_consecutivos = 0
                guardar_estado()   # ← MEJORA #2
                st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#444;padding:80px 20px;font-size:15px;">'
            '<div style="font-size:40px;margin-bottom:16px;">📋</div>'
            '<div>No hay trades aun.</div>'
            '<div style="font-size:13px;margin-top:8px;">El bot registra cada operacion automaticamente.</div>'
            '</div>',
            unsafe_allow_html=True
        )
