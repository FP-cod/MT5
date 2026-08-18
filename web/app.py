from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import subprocess
import os
import signal
import time
import pandas as pd
from pathlib import Path
from tools.metrics import compute_metrics
from web import accounting
import secrets
import json

APP_ROOT = Path(__file__).resolve().parent
TEMPLATES = Environment(
    loader=FileSystemLoader(APP_ROOT / "templates"),
    autoescape=select_autoescape(["html", "xml"]),
)

BOT_CMD = ["python", "main.py"]  # executed from repo root; ensure venv if needed
PID_FILE = APP_ROOT.parent / "bot.pid"
SIM_CSV = APP_ROOT.parent / "trades_simulated.csv"
BACKTEST_TRADES = APP_ROOT.parent / "backtest_trades.csv"
BACKTEST_EQUITY = APP_ROOT.parent / "backtest_equity.csv"

DB_PATH = APP_ROOT.parent / "data" / "accounting.db"
if not DB_PATH.parent.exists():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

# In-memory sessions: token -> username
SESSIONS: dict = {}


def read_sim_trades():
    if not SIM_CSV.exists():
        return []
    try:
        df = pd.read_csv(SIM_CSV, header=None)
        # trades_simulated.csv format: symbol,side,lots,price,sl,tp
        df = df.tail(200)
        records = []
        for row in df.itertuples(index=False):
            records.append({
                "symbol": row[0],
                "side": row[1],
                "lots": row[2],
                "price": row[3],
                "sl": row[4],
                "tp": row[5],
            })
        return records
    except Exception:
        return []


def read_backtest():
    trades = pd.read_csv(BACKTEST_TRADES) if BACKTEST_TRADES.exists() else None
    equity = pd.read_csv(BACKTEST_EQUITY) if BACKTEST_EQUITY.exists() else None
    metrics = None
    if trades is not None and equity is not None:
        trades_list = trades.to_dict(orient="records")
        equity_list = list(equity.iloc[:, 0].values)
        metrics = compute_metrics(trades_list, equity_list, start_balance=float(os.getenv("CAPITAL", 1000)))
    return trades, equity, metrics


def bot_is_running():
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            os.kill(pid, 0)
            return True
        except Exception:
            return False
    return False


def start_bot():
    if bot_is_running():
        return False, "Bot already running"
    proc = subprocess.Popen(BOT_CMD, cwd=str(APP_ROOT.parent), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    PID_FILE.write_text(str(proc.pid))
    return True, f"Started (pid={proc.pid})"


def stop_bot():
    if not PID_FILE.exists():
        return False, "No pid file"
    try:
        pid = int(PID_FILE.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.3)
            except OSError:
                break
        if PID_FILE.exists():
            PID_FILE.unlink()
        return True, "Stopped"
    except Exception as e:
        return False, f"Error stopping bot: {e}"


def require_auth(request: Request):
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user = SESSIONS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    trades = read_sim_trades()
    trades_df, equity_df, metrics = read_backtest()
    template = TEMPLATES.get_template("index.html")
    return HTMLResponse(template.render(trades=trades, metrics=metrics, running=bot_is_running()))


@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    template = TEMPLATES.get_template("login.html")
    return HTMLResponse(template.render(error=None))


@app.post("/login")
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # verify user via accounting module
    if not DB_PATH.exists():
        return HTMLResponse("<p>DB not initialized. Call /init first.</p>")
    ok = accounting.verify_user(DB_PATH, username, password)
    if not ok:
        template = TEMPLATES.get_template("login.html")
        return HTMLResponse(template.render(error="Invalid credentials"))
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = username
    resp = RedirectResponse(url='/', status_code=302)
    resp.set_cookie("session", token, httponly=True)
    return resp


@app.get("/logout")
def logout(request: Request):
    token = request.cookies.get("session")
    if token in SESSIONS:
        del SESSIONS[token]
    resp = RedirectResponse(url='/login', status_code=302)
    resp.delete_cookie("session")
    return resp


@app.post("/init")
async def api_init(payload: dict):
    """Initialize the SQLite DB. Payload: {"username":..., "password":...}
    This endpoint creates the DB and creates the admin user. Only allowed if no users exist.
    """
    username = payload.get("username")
    password = payload.get("password")
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password required")
    accounting.init_db(DB_PATH)
    count = accounting.user_count(DB_PATH)
    if count > 0:
        raise HTTPException(status_code=400, detail="DB already initialized")
    accounting.create_user(DB_PATH, username, password)
    return {"status": "ok", "msg": "db initialized and admin created"}


@app.get("/accounting", response_class=HTMLResponse)
def accounting_ui(request: Request):
    try:
        require_auth(request)
    except HTTPException:
        return RedirectResponse(url='/login')
    template = TEMPLATES.get_template("accounting.html")
    return HTMLResponse(template.render())


@app.get("/api/accounting/entries")
def api_list_entries(request: Request):
    require_auth(request)
    mode = accounting.get_setting(DB_PATH, "mode") or "nom_propre"
    entries = accounting.list_entries(DB_PATH, mode=mode)
    return {"entries": entries}


@app.post("/api/accounting/entries")
async def api_add_entry(request: Request):
    user = require_auth(request)
    payload = await request.json()
    mode = accounting.get_setting(DB_PATH, "mode") or "nom_propre"
    accounting.add_entry(DB_PATH, mode=mode, **payload)
    return {"status": "ok"}


@app.get("/api/accounting/mode")
def api_get_mode(request: Request):
    require_auth(request)
    mode = accounting.get_setting(DB_PATH, "mode") or "nom_propre"
    return {"mode": mode}


@app.post("/api/accounting/mode")
async def api_set_mode(request: Request):
    require_auth(request)
    payload = await request.json()
    mode = payload.get("mode")
    if mode not in ("nom_propre", "sasu"):
        raise HTTPException(status_code=400, detail="invalid mode")
    accounting.set_setting(DB_PATH, "mode", mode)
    return {"status": "ok", "mode": mode}


@app.get("/api/accounting/export")
def api_export_entries(request: Request):
    require_auth(request)
    mode = accounting.get_setting(DB_PATH, "mode") or "nom_propre"
    fp = accounting.export_entries_csv(DB_PATH, mode=mode)
    return FileResponse(fp, media_type="text/csv", filename=os.path.basename(fp))


@app.get("/metrics")
def api_metrics():
    trades, equity, metrics = read_backtest()
    if metrics is None:
        return {"message": "No backtest available yet"}
    return metrics
