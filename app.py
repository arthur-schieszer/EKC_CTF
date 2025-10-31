import os
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Simple XOR-based obfuscation helper (server-side)
def _xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

def decode_obfuscated_flag(b64_obf: str, secret_key: bytes) -> str:
    raw = base64.b64decode(b64_obf)
    decoded = _xor_bytes(raw, secret_key)
    return decoded.decode('utf-8', errors='ignore')

# Default secret (used to obfuscate the in-code flags).
# IMPORTANT: change APP_SECRET in your environment for real use.
DEFAULT_SECRET = b"my_default_secret_2025"
APP_SECRET = os.environ.get("APP_SECRET", None)
SECRET_KEY_BYTES = APP_SECRET.encode() if APP_SECRET else DEFAULT_SECRET

app = Flask(__name__, static_folder="static", template_folder="templates")
# Flask session secret key (keeps session cookie secure). Use APP_SECRET if set.
app.secret_key = os.environ.get("FLASK_SESSION_KEY", os.environ.get("APP_SECRET", "fallback_session_key_2025"))

# --- Obfuscated flags stored here (NOT in client files) ---
# These were produced by XORing the flag bytes with DEFAULT_SECRET and base64-encoding the result.
OBF_FLAG_2 = "CBI8HwZWUR5dRywsURFBOhpvRm9BBg4MLVcY"
OBF_FLAG_3 = "CBI8Hw8RFSoCRDFAOgIeAkQtA0RaWDIJKApWAhw="

# Admin credentials (server-side). You may set ADMIN_PASS via env for realism.
ADMIN_USER = "admin"
ADMIN_PASS = os.environ.get("ADMIN_PASS", "adminpass123")  # change for real event

# Simple user credentials for demonstration
USER_USER = "user"
USER_PASS = "password"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/challenge1")
def challenge1():
    return render_template("challenge1.html")

# ---- Challenge 2: username/password login ----
@app.route("/challenge2")
def challenge2():
    return render_template("challenge2.html")

@app.route("/api/challenge2/login", methods=["POST"])
def challenge2_login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if username == ADMIN_USER and password == ADMIN_PASS:
        session["role"] = "admin"
        # decode flag on-demand server-side
        flag = decode_obfuscated_flag(OBF_FLAG_2, SECRET_KEY_BYTES)
        return jsonify({"success": True, "role": "admin", "flag": flag})
    elif username == USER_USER and password == USER_PASS:
        session["role"] = "user"
        return jsonify({"success": True, "role": "user"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/challenge2/logout", methods=["POST"])
def challenge2_logout():
    session.pop("role", None)
    return jsonify({"success": True})

# ---- Challenge 3: token-check style (still via POST form to keep UI similar) ----
@app.route("/challenge3")
def challenge3():
    return render_template("challenge3.html")

# For this simple CTF, challenge3 also accepts username/password but demonstrates
# the server-side gating of the flag (same pattern).
@app.route("/api/challenge3/login", methods=["POST"])
def challenge3_login():
    data = request.get_json() or {}
    username = data.get("username", "")
    password = data.get("password", "")

    # You can create a more complex token mechanism for the challenge.
    # Here: admin credentials grant role 'admin'.
    if username == ADMIN_USER and password == ADMIN_PASS:
        session["role"] = "admin"
        flag = decode_obfuscated_flag(OBF_FLAG_3, SECRET_KEY_BYTES)
        return jsonify({"success": True, "role": "admin", "flag": flag})
    elif username == USER_USER and password == USER_PASS:
        session["role"] = "user"
        return jsonify({"success": True, "role": "user"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route("/api/challenge3/logout", methods=["POST"])
def challenge3_logout():
    session.pop("role", None)
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
