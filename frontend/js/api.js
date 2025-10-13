// Configuración de la API
const API_BASE_URL = 'http://127.0.0.1:8000';

// Utilidad para hacer requests
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = localStorage.getItem('token');
    
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    };
    
    // Agregar token si existe
    if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Error en la API');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Funciones específicas de la API
const API = {
    // Autenticación
    login: async (username, password) => {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        return apiRequest('/auth/login', {
            method: 'POST',
            headers: {
                // No poner Content-Type para FormData
            },
            body: formData
        });
    },
    
    getMe: async () => {
        return apiRequest('/auth/me');
    },
    
    // Materias
    getSubjects: async () => {
        return apiRequest('/subjects/');
    },
    
    createSubject: async (subject) => {
        return apiRequest('/subjects/', {
            method: 'POST',
            body: JSON.stringify(subject)
        });
    },
    
    // Contenido
    getSubjectContent: async (subjectId) => {
        return apiRequest(`/content/subject/${subjectId}`);
    },
    
    createContent: async (content) => {
        return apiRequest('/content/', {
            method: 'POST',
            body: JSON.stringify(content)
        });
    },
    
    // Compras
    purchaseSubject: async (subjectId) => {
        return apiRequest('/purchases/', {
            method: 'POST',
            body: JSON.stringify({
                subject_id: subjectId,
                user_id: 1, // Se ignora en backend, usa current_user
                amount: 0   // Se calcula en backend
            })
        });
    },
    
    getMyPurchases: async () => {
        return apiRequest('/purchases/my-purchases');
    }
};

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