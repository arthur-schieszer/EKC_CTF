import base64
import hmac
import hashlib
import json
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# --- lightly obfuscated secrets ---
# base64 of a random secret key (do not use in production)
_OBFUSCATED_SECRET = b'c2VjcmV0X2ZsYXNrX3NlY3JldA=='     # "secret_flask_secret"
# base64 of the admin password
_OBFUSCATED_ADMIN_PASS = b'YWRtMW5wYXNz'  # "adm1npass"

def _decode(b):
    return base64.b64decode(b).decode()

def _b64url_decode(inp: str) -> bytes:
    # Accept both b64 and base64url (JWT style)
    inp = inp.replace('-', '+').replace('_', '/')
    padding = len(inp) % 4
    if padding:
        inp += '=' * (4 - padding)
    return base64.b64decode(inp)

app = Flask(__name__)
app.secret_key = _decode(_OBFUSCATED_SECRET)

# --- flags (hard-coded for development) ---
FLAGS = {
    "challenge2": "ekc{c00k13s_4r3_n0t_s3cur3}",
    "challenge3": "ekc{jwt_n0n3_alg0r1thm_pwn3d}"
}

# --- simple user check ---
def check_credentials(username, password):
    # regular users: any username/password -> role 'user'
    # admin credentials: username == 'admin' and password matches obfuscated admin pass
    admin_pass = _decode(_OBFUSCATED_ADMIN_PASS)
    if username == "admin" and password == admin_pass:
        return "admin"
    return "user"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/challenge1")
def c1():
    # challenge 1 is the "needle in haystack" single-page static (left as client-side)
    return render_template("challenge1.html")

@app.route("/challenge2")
def c2():
    return render_template("challenge2.html")

@app.route("/challenge3")
def c3():
    return render_template("challenge3.html")

# --- API endpoints for login/logout and flag retrieval ---
@app.route("/api/login", methods=["POST"])
def api_login():
    # 1) If a token is provided in JSON body, prefer that (JWT challenge)
    data = request.json or {}
    token = data.get("token")
    if token:
        try:
            parts = token.split('.')
            if len(parts) >= 2:
                header_b, payload_b = parts[0], parts[1]
                header_json = json.loads(_b64url_decode(header_b).decode())
                payload_json = json.loads(_b64url_decode(payload_b).decode())
                alg = header_json.get("alg", "").lower()
                if alg == "none":
                    # take role directly from payload (only 'admin' or 'user' allowed)
                    role_raw = payload_json.get("role", "")
                    role = "admin" if role_raw == "admin" else "user"
                    session["role"] = role
                    # username can be optional; preserve existing username if provided in JSON
                    session["username"] = (request.json.get("username", "") if request.json else "")
                    return jsonify({"ok": True, "role": role})
                # else: not 'none' -> let fall through to credential-based path
        except Exception:
            # malformed token -> ignore and fall back
            pass

    # 2) If there's a role cookie, prefer it (cookie should be base64 encoded)
    role_cookie = request.cookies.get("role")
    if role_cookie:
        try:
            decoded = base64.b64decode(role_cookie).decode()
            role = "admin" if decoded == "admin" else "user"
            session["role"] = role
            session["username"] = data.get("username", "") if data else ""
            return jsonify({"ok": True, "role": role})
        except Exception:
            pass

    # 3) fallback: old credential-based behavior
    username = data.get("username", "")
    password = data.get("password", "")
    role = check_credentials(username, password)
    session["role"] = role
    session["username"] = username
    return jsonify({"ok": True, "role": role})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/flag/<challenge>", methods=["GET"])
def api_flag(challenge):
    # only return the flag for admin sessions
    role = session.get("role")
    if role != "admin":
        return jsonify({"ok": False, "error": "forbidden"}), 403
    flag = FLAGS.get(challenge)
    if not flag:
        return jsonify({"ok": False, "error": "not found"}), 404
    return jsonify({"ok": True, "flag": flag})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
