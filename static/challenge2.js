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

function checkAuth() {
    const role = getCookie('role');
    
    if (!role) {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'none';
        return;
    }
    
    let decodedRole;
    try {
        decodedRole = atob(role);
    } catch (e) {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'none';
        return;
    }
    
    if (decodedRole === 'admin') {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'block';
    } else if (decodedRole === 'user') {
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('userDashboard').style.display = 'block';
        document.getElementById('adminDashboard').style.display = 'none';
    } else {
        document.getElementById('loginPage').style.display = 'block';
        document.getElementById('userDashboard').style.display = 'none';
        document.getElementById('adminDashboard').style.display = 'none';
    }
}

function logout() {
    deleteCookie('role');
    checkAuth();
    showMessage('Logged out successfully', 'success');
}

document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    if (username && password) {
        setCookie('role', btoa('user'));
        showMessage('Login successful!', 'success');
        
        setTimeout(() => {
            checkAuth();
        }, 1000);
    }
});

checkAuth();