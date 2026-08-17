from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
import subprocess
import os
import signal
import time
import pandas as pd
from pathlib import Path
from tools.metrics import compute_metrics

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

app = FastAPI()
app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")


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


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    trades = read_sim_trades()
    trades_df, equity_df, metrics = read_backtest()
    template = TEMPLATES.get_template("index.html")
    return HTMLResponse(template.render(trades=trades, metrics=metrics, running=bot_is_running()))


@app.post("/start")
def api_start():
    ok, msg = start_bot()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "started", "msg": msg}


@app.post("/stop")
def api_stop():
    ok, msg = stop_bot()
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "stopped", "msg": msg}


@app.get("/download/trades")
def download_trades():
    if SIM_CSV.exists():
        return FileResponse(str(SIM_CSV), media_type="text/csv", filename="trades_simulated.csv")
    raise HTTPException(status_code=404, detail="No simulated trades file")


@app.get("/metrics")
def api_metrics():
    trades, equity, metrics = read_backtest()
    if metrics is None:
        return {"message": "No backtest available yet"}
    return metrics
