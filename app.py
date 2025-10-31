import base64
import json
import hmac
import hashlib
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response

# --- lightly obfuscated secrets ---
_OBFUSCATED_SECRET = b'c2VjcmV0X2ZsYXNrX3NlY3JldA=='     # "secret_flask_secret"
_OBFUSCATED_ADMIN_PASS = b'YWRtMW5wYXNz'  # "adm1npass"

def _decode(b):
    return base64.b64decode(b).decode()

app = Flask(__name__)
app.secret_key = _decode(_OBFUSCATED_SECRET)

# --- flags (hard-coded for development) ---
FLAGS = {
    "challenge2": "ekc{c00k13s_4r3_n0t_s3cur3}",
    "challenge3": "ekc{jwt_n0n3_alg0r1thm_pwn3d}"
}

def check_credentials(username, password):
    admin_pass = _decode(_OBFUSCATED_ADMIN_PASS)
    if username == "admin" and password == admin_pass:
        return "admin"
    return "user"

# --- base64url helpers ---
def _b64url_decode(inp: str) -> bytes:
    inp = inp.replace('-', '+').replace('_', '/')
    padding = len(inp) % 4
    if padding:
        inp += '=' * (4 - padding)
    return base64.b64decode(inp)

def _b64url_encode(inp: bytes) -> str:
    return base64.b64encode(inp).decode().replace('+', '-').replace('/', '_').rstrip('=')

# --- verify JWT ---
def verify_jwt(token: str):
    """
    Returns payload dict if token is acceptable; otherwise None.
    Acceptable cases (for this CTF):
      - header.alg == "none" -> trust payload (exploit path)
      - header.alg == "HS256" -> verify HMAC-SHA256 using app.secret_key
    """
    try:
        parts = token.split('.')
        if len(parts) < 2:
            return None
        header_b, payload_b = parts[0], parts[1]
        header_json = json.loads(_b64url_decode(header_b).decode())
        payload_json = json.loads(_b64url_decode(payload_b).decode())
        alg = header_json.get("alg", "").lower()

        if alg == "none":
            return payload_json

        if alg == "hs256":
            # signature present?
            if len(parts) < 3:
                return None
            sig_b = parts[2]
            msg = (header_b + "." + payload_b).encode()
            secret = app.secret_key if isinstance(app.secret_key, str) else app.secret_key.decode()
            hm = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
            expected_sig = _b64url_encode(hm)
            # compare safely
            if hmac.compare_digest(expected_sig, sig_b):
                return payload_json
            return None

        # other algs: not supported in this CTF
        return None
    except Exception:
        return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/challenge1")
def c1():
    return render_template("challenge1.html")

@app.route("/challenge2")
def c2():
    return render_template("challenge2.html")

@app.route("/challenge3")
def c3():
    return render_template("challenge3.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    """
    Login behavior:
    - If a cookie named 'token' exists and verifies (alg none OR valid HS256), use its payload.role.
    - Else if a cookie named 'role' exists (base64), decode that and use it (Challenge 2 flow).
    - Else fallback to username/password check.
    """
    # 1) check token cookie (JWT)
    token = request.cookies.get("token")
    if token:
        payload = verify_jwt(token)
        if payload:
            role_raw = payload.get("role", "")
            role = "admin" if role_raw == "admin" else "user"
            session["role"] = role
            session["username"] = (request.json.get("username", "") if request.json else "")
            return jsonify({"ok": True, "role": role})

    # 2) check role cookie (Challenge 2 base64)
    role_cookie = request.cookies.get("role")
    if role_cookie:
        try:
            decoded = base64.b64decode(role_cookie).decode()
            role = "admin" if decoded == "admin" else "user"
            session["role"] = role
            session["username"] = (request.json.get("username", "") if request.json else "")
            return jsonify({"ok": True, "role": role})
        except Exception:
            pass

    # 3) fallback: credential check
    data = request.json or {}
    username = data.get("username", "")
    password = data.get("password", "")
    role = check_credentials(username, password)
    session["role"] = role
    session["username"] = username
    return jsonify({"ok": True, "role": role})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    # Clear session and instruct browser to delete both cookies used in challenges
    session.clear()
    resp = jsonify({"ok": True})
    # set cookies expired; path=/ so they get cleared site-wide
    resp.set_cookie("role", "", expires=0, path="/")
    resp.set_cookie("token", "", expires=0, path="/")
    return resp

@app.route("/api/flag/<challenge>", methods=["GET"])
def api_flag(challenge):
    role = session.get("role")
    if role != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403
    flag = FLAGS.get(challenge)
    if not flag:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, "flag": flag})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
