#!/usr/bin/env python3
import csv
import io
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("DATA_DIR", ROOT / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "research.sqlite3"
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
PORT = int(os.environ.get("PORT", "8000"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "").strip()
MAX_BODY = 2_000_000
APP_VERSION = "0.7"

# On local runs, generate a temporary token instead of silently exposing admin
# endpoints behind a known default. Render sets ADMIN_TOKEN from render.yaml.
if not ADMIN_TOKEN:
    ADMIN_TOKEN = secrets.token_urlsafe(24)
    print("ADMIN_TOKEN was not set. Temporary local admin token:", ADMIN_TOKEN)


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def using_postgres():
    return bool(DATABASE_URL)


def pg_connect():
    import psycopg
    return psycopg.connect(DATABASE_URL)


def init_db():
    if using_postgres():
        with pg_connect() as con:
            with con.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        completed INTEGER NOT NULL DEFAULT 0,
                        payload TEXT NOT NULL
                    )
                """)
            con.commit()
    else:
        con = sqlite3.connect(DB_PATH)
        con.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                payload TEXT NOT NULL
            )
        """)
        con.commit()
        con.close()


def upsert_session(sid, created, updated, completed, payload):
    payload_json = json.dumps(payload, ensure_ascii=False)
    if using_postgres():
        with pg_connect() as con:
            with con.cursor() as cur:
                cur.execute(
                    """INSERT INTO sessions(id,created_at,updated_at,completed,payload)
                       VALUES(%s,%s,%s,%s,%s)
                       ON CONFLICT(id) DO UPDATE SET
                         updated_at=EXCLUDED.updated_at,
                         completed=EXCLUDED.completed,
                         payload=EXCLUDED.payload""",
                    (sid, created, updated, completed, payload_json),
                )
            con.commit()
    else:
        con = sqlite3.connect(DB_PATH)
        con.execute(
            """INSERT INTO sessions(id,created_at,updated_at,completed,payload)
               VALUES(?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 updated_at=excluded.updated_at,
                 completed=excluded.completed,
                 payload=excluded.payload""",
            (sid, created, updated, completed, payload_json),
        )
        con.commit()
        con.close()


def fetch_sessions():
    if using_postgres():
        with pg_connect() as con:
            with con.cursor() as cur:
                cur.execute("SELECT payload FROM sessions ORDER BY updated_at DESC")
                rows = cur.fetchall()
    else:
        con = sqlite3.connect(DB_PATH)
        rows = con.execute("SELECT payload FROM sessions ORDER BY updated_at DESC").fetchall()
        con.close()
    sessions = []
    for (payload,) in rows:
        try:
            sessions.append(json.loads(payload))
        except Exception:
            pass
    return sessions


def fetch_export_rows():
    if using_postgres():
        with pg_connect() as con:
            with con.cursor() as cur:
                cur.execute("SELECT id,updated_at,completed,payload FROM sessions ORDER BY updated_at DESC")
                return cur.fetchall()
    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT id,updated_at,completed,payload FROM sessions ORDER BY updated_at DESC").fetchall()
    con.close()
    return rows


def safe_payload(obj):
    if not isinstance(obj, dict):
        raise ValueError("JSON object required")
    sid = str(obj.get("id", "")).strip()
    if not sid or len(sid) > 120:
        raise ValueError("invalid session id")
    participant = obj.get("participant")
    if participant is not None and not isinstance(participant, dict):
        raise ValueError("invalid participant")
    events = obj.get("events")
    if events is not None and not isinstance(events, list):
        raise ValueError("invalid events")
    return sid, obj


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        if self.path.endswith((".html", "/")):
            self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def json_response(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0 or length > MAX_BODY:
            raise ValueError("invalid body size")
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def is_admin(self):
        supplied = self.headers.get("X-Admin-Token", "")
        return secrets.compare_digest(supplied, ADMIN_TOKEN)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/session":
            return self.json_response(HTTPStatus.NOT_FOUND, {"error": "not found"})
        try:
            obj = self.read_json()
            sid, obj = safe_payload(obj)
            now = utcnow()
            completed = 1 if obj.get("completed") else 0
            created = str(obj.get("created") or now)
            upsert_session(sid, created, now, completed, obj)
            return self.json_response(HTTPStatus.OK, {"ok": True, "id": sid, "completed": bool(completed)})
        except Exception as e:
            print("POST /api/session error:", repr(e))
            return self.json_response(HTTPStatus.BAD_REQUEST, {"error": "session save failed"})

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            try:
                init_db()
                return self.json_response(HTTPStatus.OK, {
                    "ok": True,
                    "version": APP_VERSION,
                    "database": "postgres" if using_postgres() else "sqlite",
                })
            except Exception as e:
                print("health error:", repr(e))
                return self.json_response(HTTPStatus.SERVICE_UNAVAILABLE, {"ok": False, "version": APP_VERSION})

        if path == "/api/sessions":
            if not self.is_admin():
                return self.json_response(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            try:
                sessions = fetch_sessions()
                return self.json_response(HTTPStatus.OK, {"sessions": sessions, "count": len(sessions)})
            except Exception as e:
                print("GET /api/sessions error:", repr(e))
                return self.json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "database read failed"})

        if path == "/api/export.csv":
            if not self.is_admin():
                return self.json_response(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
            try:
                rows = fetch_export_rows()
                buf = io.StringIO()
                w = csv.writer(buf)
                w.writerow([
                    "id","updated_at","completed","age_group","gender","apps","frequency",
                    "gesture_choice","return_choice","duration_ms","memory_text","own_prompt"
                ])
                for sid, updated, completed, payload in rows:
                    try:
                        s = json.loads(payload)
                    except Exception:
                        s = {}
                    part = s.get("participant") or {}
                    w.writerow([
                        sid, updated, completed, part.get("ageGroup", ""), part.get("gender", ""),
                        "|".join(part.get("apps") or []), part.get("frequency", ""),
                        s.get("gestureChoice", ""), s.get("returnChoice", ""), s.get("duration_ms", ""),
                        s.get("memoryText", ""), s.get("ownPrompt", "")
                    ])
                data = buf.getvalue().encode("utf-8-sig")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="minukimi_sessions.csv"')
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            except Exception as e:
                print("GET /api/export.csv error:", repr(e))
                return self.json_response(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": "export failed"})

        return super().do_GET()


if __name__ == "__main__":
    init_db()
    print(f"MINUKIMI research server v{APP_VERSION}: http://localhost:{PORT}")
    print("Storage:", "Render Postgres" if using_postgres() else f"SQLite ({DB_PATH})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
