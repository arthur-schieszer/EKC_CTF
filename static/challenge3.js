function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function setCookie(name, value, days = 7) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${value};expires=${expires.toUTCString()};path=/`;
}

function deleteCookie(name) {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function showMessage(text, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

function base64UrlEncode(str) {
    return btoa(str)
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

function base64UrlDecode(str) {
    str = str.replace(/-/g, '+').replace(/_/g, '/');
    while (str.length % 4) {
        str += '=';
    }
    return atob(str);
}

function checkAuth() {
    const token = getCookie('token');
    
    if (!token) {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'none';
        return;
    }
    
    try {
        const parts = token.split('.');
        if (parts.length !== 3) throw new Error('Invalid token');
        
        const header = JSON.parse(base64UrlDecode(parts[0]));
        const payload = JSON.parse(base64UrlDecode(parts[1]));
        
        // Check if algorithm is "none" - vulnerable implementation
        if (header.alg === "none" || header.alg === "None" || header.alg === "NONE") {
            // Accept token without signature verification
            if (payload.role === 'admin') {
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('userDashboard').style.display = 'none';
                document.getElementById('adminDashboard').style.display = 'block';
                return;
            }
        }
        
        // Normal flow - just check role
        if (payload.role === 'user') {
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('userDashboard').style.display = 'block';
            document.getElementById('adminDashboard').style.display = 'none';
        } else {
            document.getElementById('loginPage').style.display = 'block';
            document.getElementById('userDashboard').style.display = 'none';
            document.getElementById('adminDashboard').style.display = 'none';
        }
    } catch (e) {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'none';
    }
}

function logout() {
    deleteCookie('token');
    checkAuth();
    showMessage('Logged out successfully', 'success');
}

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (username && password) {
        const header = { alg: "HS256", typ: "JWT" };
        const payload = { sub: username, role: "user", iat: Math.floor(Date.now() / 1000) };
        
        const headerEncoded = base64UrlEncode(JSON.stringify(header));
        const payloadEncoded = base64UrlEncode(JSON.stringify(payload));
        const signature = base64UrlEncode("fake_signature_12345");
        
        const token = `${headerEncoded}.${payloadEncoded}.${signature}`;
        setCookie('token', token);
        
        showMessage('Login successful!', 'success');
        
        setTimeout(() => {
            checkAuth();
        }, 1000);
    }
});

checkAuth();