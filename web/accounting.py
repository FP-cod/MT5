"""Accounting helper module using SQLite.
Provides simple CRUD for accounting entries, settings and users.
"""
import sqlite3
from pathlib import Path
import datetime
import csv
import hashlib
import os


def get_conn(db_path: Path):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path):
    if db_path.exists():
        return
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    c.execute("""
    CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    c.execute("""
    CREATE TABLE entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        mode TEXT,
        category TEXT,
        subcategory TEXT,
        type TEXT,
        amount REAL,
        currency TEXT,
        description TEXT,
        created_at TEXT
    )
    """)
    # default settings
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", ("nom_propre_charges_pct", "0.45"))
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", ("nom_propre_ir_pct", "0.20"))
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", ("sasu_is_pct", "0.25"))
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", ("mode", "nom_propre"))
    conn.commit()
    conn.close()


# Simple PBKDF2 password hashing

def _hash_password(password: str, salt: bytes = None):
    if salt is None:
        salt = os.urandom(16)
    pwd = password.encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", pwd, salt, 100_000)
    return dk.hex(), salt.hex()


def create_user(db_path: Path, username: str, password: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    pwd_hash, salt = _hash_password(password)
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO users(username,password_hash,salt,created_at) VALUES (?,?,?,?)", (username, pwd_hash, salt, now))
    conn.commit()
    conn.close()


def user_count(db_path: Path) -> int:
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute("SELECT COUNT(1) as c FROM users")
    r = c.fetchone()
    conn.close()
    return int(r[0]) if r else 0


def verify_user(db_path: Path, username: str, password: str) -> bool:
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute("SELECT password_hash, salt FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    stored_hash = row[0]
    salt = bytes.fromhex(row[1])
    dk, _ = _hash_password(password, salt)
    return dk == stored_hash


# Settings helpers

def set_setting(db_path: Path, key: str, value: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", (key, str(value)))
    conn.commit()
    conn.close()


def get_setting(db_path: Path, key: str):
    conn = get_conn(db_path)
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key=?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


# Entries

def add_entry(db_path: Path, mode: str, date: str = None, category: str = "uncategorized", subcategory: str = "", type: str = "credit", amount: float = 0.0, currency: str = "EUR", description: str = ""):
    if date is None:
        date = datetime.datetime.utcnow().isoformat()
    conn = get_conn(db_path)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("INSERT INTO entries(date,mode,category,subcategory,type,amount,currency,description,created_at) VALUES (?,?,?,?,?,?,?,?,?)", (date, mode, category, subcategory, type, amount, currency, description, now))
    conn.commit()
    conn.close()


def list_entries(db_path: Path, mode: str = None, limit: int = 500):
    conn = get_conn(db_path)
    c = conn.cursor()
    if mode:
        c.execute("SELECT * FROM entries WHERE mode=? ORDER BY date DESC LIMIT ?", (mode, limit))
    else:
        c.execute("SELECT * FROM entries ORDER BY date DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def export_entries_csv(db_path: Path, mode: str = None):
    rows = list_entries(db_path, mode=mode, limit=10000)
    out = Path(db_path).parent / f"accounting_{mode}.csv"
    with open(out, "w", newline='') as f:
        if not rows:
            f.write("")
            return str(out)
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return str(out)
