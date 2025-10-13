// Estado de autenticación
let currentUser = null;

// Inicializar autenticación
function initAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        // Verificar si el token es válido
        API.getMe()
            .then(user => {
                currentUser = user;
                showDashboard();
            })
            .catch(() => {
                // Token inválido, limpiar
                logout();
            });
    } else {
        showLogin();
    }
}

// Login
async function login(username, password) {
    try {
        const response = await API.login(username, password);
        
        // Guardar token
        localStorage.setItem('token', response.access_token);
        
        // Obtener datos del usuario
        currentUser = await API.getMe();
        
        showDashboard();
        return true;
    } catch (error) {
        showError(error.message);
        return false;
    }
}

// Logout
function logout() {
    localStorage.removeItem('token');
    currentUser = null;
    showLogin();
}

// Mostrar/ocultar secciones
function showLogin() {
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('dashboard-section').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    
    // Actualizar info del usuario
    document.getElementById('user-name').textContent = currentUser.username;
    document.getElementById('user-role').textContent = `(${currentUser.role})`;
    
    // Cargar contenido del dashboard
    loadDashboard();
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

// Verificar si es admin
function isAdmin() {
    return currentUser && currentUser.role === 'admin';
}

// Verificar si es teacher o admin
function canCreateContent() {
    return currentUser && (currentUser.role === 'admin' || currentUser.role === 'teacher');
}