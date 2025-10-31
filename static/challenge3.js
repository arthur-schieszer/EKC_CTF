// challenge3.js - Cookie-based JWT manipulation challenge
// Players can edit the cookie named "token" to set header.alg="none" and payload.role="admin".
// logout() will attempt to clear the token cookie client-side as well as call /api/logout.

document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("loginForm");
    const message = document.getElementById("message");
    const loginPage = document.getElementById("loginPage");
    const userDashboard = document.getElementById("userDashboard");
    const adminDashboard = document.getElementById("adminDashboard");
    const flagContainer = document.getElementById("flagContainer");

    function showMessage(text, cls) {
        message.textContent = text;
        message.className = "message " + (cls || "success");
        message.style.display = "block";
    }

    function showView(role) {
        loginPage.style.display = role ? "none" : "block";
        userDashboard.style.display = role === "user" ? "block" : "none";
        adminDashboard.style.display = role === "admin" ? "block" : "none";
    }

    async function fetchFlag() {
        const res = await fetch("/api/flag/challenge3");
        if (res.ok) {
            const j = await res.json();
            flagContainer.textContent = j.flag;
        } else {
            flagContainer.textContent = "Flag not available.";
        }
    }

    // helper: base64url encode (like JWT)
    function b64urlEncode(str) {
        return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    }

    // generate a default HS256 token (non-admin) if none exists
    (function ensureDefaultToken() {
        if (!document.cookie.split('; ').find(row => row.startsWith("token="))) {
            const header = { alg: "HS256", typ: "JWT" };
            const payload = { role: "user", sub: "player" };
            const token = b64urlEncode(JSON.stringify(header)) + "." + b64urlEncode(JSON.stringify(payload)) + ".signature";
            document.cookie = "token=" + token + "; path=/";
        }
    })();

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        const res = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
        const j = await res.json();
        if (j.ok) {
            showMessage("Login successful — role: " + j.role, "success");
            showView(j.role);
            if (j.role === "admin") {
                await fetchFlag();
            }
        } else {
            showMessage("Login failed", "error");
        }
    });
});

async function logout() {
    // client-side attempt to clear token cookie (defensive)
    document.cookie = "token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    // call server to clear session and cookies
    await fetch("/api/logout", { method: "POST" });
    window.location.reload();
}
