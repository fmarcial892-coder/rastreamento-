import os
import sqlite3
import secrets
from datetime import datetime, timezone, timedelta
from functools import wraps
from flask import Flask, jsonify, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))
DB_PATH = os.environ.get("DB_PATH", "/tmp/rastreamento.sqlite3")
ADMIN_USER = os.environ.get("ADMIN_USER", "")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "")
REFERENCE_ADDRESS = "Rua Aristides Crivellaro, 228 - Macuco, Valinhos - SP, 13279-813"


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_code TEXT NOT NULL UNIQUE,
            street TEXT NOT NULL, number TEXT NOT NULL, complement TEXT,
            neighborhood TEXT, city TEXT, state TEXT, cep TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'received', created_at TEXT NOT NULL,
            released_at TEXT, updated_at TEXT NOT NULL
        )""")
        conn.commit()


def now():
    return datetime.now(timezone.utc).isoformat()


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapped


def order_dict(row):
    item = dict(row)
    item["eta_minutes"] = 60
    if item.get("released_at"):
        elapsed = datetime.now(timezone.utc) - datetime.fromisoformat(item["released_at"])
        item["progress"] = max(0, min(100, int(elapsed.total_seconds() / 3600 * 100)))
        item["eta_minutes"] = max(0, 60 - int(elapsed.total_seconds() / 60))
    else:
        item["progress"] = 0
    return item


@app.before_request
def startup():
    init_db()


@app.get("/")
def index():
    return render_template("index.html", reference_address=REFERENCE_ADDRESS)


@app.post("/api/orders")
def create_order():
    data = request.get_json(silent=True) or {}
    required = ["street", "number", "cep", "city", "state"]
    if any(not str(data.get(field, "")).strip() for field in required):
        return jsonify(error="Informe o endereço completo."), 400
    tracking = str(data.get("tracking_code", "")).strip().upper() or f"RF-{secrets.token_hex(4).upper()}"
    timestamp = now()
    try:
        with db() as conn:
            conn.execute("""INSERT INTO orders
                (tracking_code,street,number,complement,neighborhood,city,state,cep,status,created_at,updated_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (tracking, data["street"].strip(), data["number"].strip(), str(data.get("complement", "")).strip(), data.get("neighborhood", "").strip(), data["city"].strip(), data["state"].strip(), data["cep"].strip(), "received", timestamp, timestamp))
            conn.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="Esse código já foi utilizado. Informe outro."), 409
    return jsonify(tracking_code=tracking, status="received"), 201


@app.get("/api/orders/<tracking>")
def public_order(tracking):
    with db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE tracking_code=?", (tracking.upper(),)).fetchone()
    if not row:
        return jsonify(error="Pedido não encontrado."), 404
    return jsonify(order_dict(row))


@app.get("/admin/login")
def admin_login():
    return render_template("admin_login.html")


@app.post("/admin/login")
def admin_login_post():
    if not ADMIN_USER or not ADMIN_PASSWORD:
        return render_template("admin_login.html", error="Painel ainda não configurado na hospedagem."), 503
    if secrets.compare_digest(request.form.get("username", ""), ADMIN_USER) and secrets.compare_digest(request.form.get("password", ""), ADMIN_PASSWORD):
        session.clear(); session["admin"] = True
        return redirect(url_for("admin"))
    return render_template("admin_login.html", error="Usuário ou senha inválidos."), 401


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin():
    with db() as conn:
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    return render_template("admin.html", orders=[order_dict(row) for row in rows], reference_address=REFERENCE_ADDRESS)


@app.post("/api/admin/orders/<int:order_id>/status")
@admin_required
def update_status(order_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    allowed = {"received", "released", "in_transit", "delivered"}
    if status not in allowed:
        return jsonify(error="Status inválido."), 400
    timestamp = now()
    with db() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
        if not row:
            return jsonify(error="Pedido não encontrado."), 404
        released_at = row["released_at"]
        if status == "released" and not released_at:
            released_at = timestamp
        conn.execute("UPDATE orders SET status=?, released_at=?, updated_at=? WHERE id=?", (status, released_at, timestamp, order_id))
        conn.commit()
    return jsonify(ok=True)


@app.get("/privacidade")
def privacy():
    return render_template("privacy.html")


@app.get("/termos")
def terms():
    return render_template("terms.html")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
