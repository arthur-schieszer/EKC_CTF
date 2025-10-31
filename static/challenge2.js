// challenge2.js - cookie-based role (base64). Change cookie to btoa("admin") to get flag.
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
        const res = await fetch("/api/flag/challenge2");
        if (res.ok) {
            const j = await res.json();
            flagContainer.textContent = j.flag;
        } else {
            flagContainer.textContent = "Flag not available.";
        }
    }

    // set default role cookie to "user" (base64) so players start as non-admin
    // cookie path is / so /api/login can see it
    (function ensureDefaultRoleCookie(){
        const name = "role=";
        if (!document.cookie.split('; ').find(row => row.startsWith("role="))) {
            document.cookie = "role=" + btoa("user") + "; path=/";
        }
    })();

    loginForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const username = document.getElementById("username").value;
        const password = document.getElementById("password").value;

        // We do NOT send role in JSON; server reads cookie "role" (base64) and sets session accordingly.
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
    await fetch("/api/logout", { method: "POST" });
    window.location.reload();
}
