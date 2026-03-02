// Estado de autenticación
let currentUser = null;
let tokenRefreshTimer = null;

// Inicializar autenticación
async function initAuth() {
    console.log('🔄 Verificando autenticación...');
    const token = localStorage.getItem('token');
    
    if (token) {
        try {
            console.log('🔑 Token encontrado, validando...');
            const user = await API.getCurrentUser();
            currentUser = user;
            console.log('✅ Usuario autenticado:', user);
            startTokenRefreshTimer();
            showDashboard(user);
        } catch (error) {
            console.log('❌ Token inválido, intentando refresh...');
            const refreshed = await tryRefreshToken();
            if (refreshed) {
                try {
                    const user = await API.getCurrentUser();
                    currentUser = user;
                    startTokenRefreshTimer();
                    showDashboard(user);
                    return;
                } catch (e) { /* fall through */ }
            }
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('currentUser');
            showLogin();
        }
    } else {
        console.log('📝 No hay token, mostrando login');
        showLogin();
    }
}

// Intentar refrescar el token
async function tryRefreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) return false;
    try {
        const data = await API.refreshToken(refreshToken);
        localStorage.setItem('token', data.access_token);
        console.log('🔄 Token renovado automáticamente');
        return true;
    } catch (e) {
        console.log('❌ No se pudo renovar el token');
        return false;
    }
}

// Timer para auto-refrescar el token antes de que expire
function startTokenRefreshTimer() {
    if (tokenRefreshTimer) clearInterval(tokenRefreshTimer);
    // Refrescar cada 20 minutos (el token dura 24h, así que está de sobra)
    tokenRefreshTimer = setInterval(async () => {
        console.log('🔄 Auto-refresh de token...');
        await tryRefreshToken();
    }, 20 * 60 * 1000);
}

function stopTokenRefreshTimer() {
    if (tokenRefreshTimer) { clearInterval(tokenRefreshTimer); tokenRefreshTimer = null; }
}

// Login
function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    console.log('🔑 Intentando login:', username);
    
    if (!username || !password) {
        showError('Por favor ingresa usuario y contraseña');
        return;
    }

    API.login(username, password)
        .then(data => {
            console.log('✅ Login exitoso:', data);
            localStorage.setItem('token', data.access_token);
            if (data.refresh_token) localStorage.setItem('refreshToken', data.refresh_token);
            
            return API.getCurrentUser();
        })
        .then(userData => {
            console.log('✅ User data:', userData);
            currentUser = userData;
            startTokenRefreshTimer();
            showDashboard(userData);
        })
        .catch(error => {
            console.error('❌ Login error:', error);
            showError('Error de login: ' + error.message);
        });
}

// Logout
function logout() {
    console.log('👋 Logout');
    stopTokenRefreshTimer();
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('currentUser');
    currentUser = null;
    showLogin();
}

// Mostrar/ocultar secciones
function showLogin() {
    console.log('📝 Mostrando login');
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('dashboard-section').classList.add('hidden');
}

function showDashboard(user) {
    console.log('🏠 Mostrando dashboard para:', user);
    currentUser = user;
    
    // Ocultar login, mostrar dashboard
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    
    // Actualizar información del usuario
    document.getElementById('user-name').textContent = user.full_name || user.username;
    document.getElementById('user-role').textContent = getRoleLabel(user.role);
    
    // ✅ AGREGAR ESTAS LÍNEAS PARA CONTROLAR VISIBILIDAD:
    const adminItems = document.querySelectorAll('.admin-only');
    const studentItems = document.querySelectorAll('.student-only');
    
    if (user.role === 'student') {
        // Mostrar elementos de estudiante, ocultar de admin
        adminItems.forEach(item => item.style.display = 'none');
        studentItems.forEach(item => item.style.display = 'flex');
        document.body.classList.add('student');
        document.body.classList.remove('admin');
    } else if (user.role === 'admin' || user.role === 'teacher') {
        // Mostrar elementos de admin, ocultar de estudiante
        adminItems.forEach(item => item.style.display = 'flex');
        studentItems.forEach(item => item.style.display = 'none');
        document.body.classList.add('admin');
        document.body.classList.remove('student');
    }
    
    // Cargar dashboard inicial
    loadDashboard();
}

function showError(message) {
    console.error('❌ Error:', message);
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

// ✅ AGREGAR ESTA FUNCIÓN:
function showSuccess(message) {
    console.log('✅ Success:', message);
    const successDiv = document.createElement('div');
    successDiv.className = 'success-message';
    successDiv.textContent = message;
    successDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Verificar si es admin
function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// Verificar si es teacher o admin
function canCreateContent() {
    return currentUser && (currentUser.role === 'admin' || currentUser.role === 'teacher');
}

// Obtener etiqueta del rol
function getRoleLabel(role) {
    const roles = {
        'admin': 'Administrador',
        'teacher': 'Profesor',
        'student': 'Estudiante'
    };
    return roles[role] || 'Usuario';
}