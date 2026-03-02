const API = {
    BASE_URL: 'http://127.0.0.1:5000',
    
getHeaders() {
    const headers = {
        'Content-Type': 'application/json'  // ✅ AGREGAR ESTO
    };
    const token = localStorage.getItem('token');
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    return headers;
},

    async handleResponse(fetchPromise) {
        try {
            const response = await fetchPromise;
            console.log('📡 API Response', response.status + ':', response.url);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('❌ API Error:', errorText);
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            // ✅ FIX: Verificar si hay contenido antes de parsear
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                const data = await response.json();
                console.log('✅ API Data:', data);
                return data;
            } else {
                // Si no es JSON, devolver texto
                const text = await response.text();
                console.log('✅ API Text:', text);
                return text;
            }
        } catch (error) {
            console.error('❌ API Request Failed:', error);
            throw error;
        }
    },

    async login(username, password) {
        console.log('🔑 API Login:', username);
        
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${this.BASE_URL}/auth/login`, {
            method: 'POST',
            body: formData
        });
        return this.handleResponse(response);
    },

    async getCurrentUser() {
        console.log('👤 API Get Current User');
        const response = await fetch(`${this.BASE_URL}/auth/me`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    },

    async getSubjects() {
        console.log('📚 API Get Subjects');
        const response = await fetch(`${this.BASE_URL}/subjects/`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    },

    async getMyPurchases() {
        console.log('🛒 API Get My Purchases');
        const response = await fetch(`${this.BASE_URL}/purchases/my-purchases`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    },

    async createSubject(subject) {
        console.log('➕ API Create Subject:', subject);
        const response = await fetch(`${this.BASE_URL}/subjects/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify(subject)
        });
        return this.handleResponse(response);
    },

    async getSubjectContent(subjectId) {
        console.log('📖 API Get Subject Content:', subjectId);
        // ✅ CAMBIAR LA RUTA:
        return this.handleResponse(
            fetch(`${this.BASE_URL}/content/subjects/${subjectId}/content`, {
                headers: this.getHeaders()
            })
        );
    },

    async createContent(content) {
        console.log('➕ API Create Content:', content);
        const response = await fetch(`${this.BASE_URL}/content/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify(content)
        });
        return this.handleResponse(response);
    },

    async purchaseSubjectWithData(purchaseData) {
        console.log('💳 API Purchase:', purchaseData);
        const response = await fetch(`${this.BASE_URL}/purchases/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify(purchaseData)
        });
        return this.handleResponse(response);
    },

    async createMPPreference(subjectId) {
        console.log('💳 API Create MP Preference:', subjectId);
        const response = await fetch(`${this.BASE_URL}/purchases/create-preference`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify({ subject_id: subjectId })
        });
        return this.handleResponse(response);
    },

    async confirmMPPayment(subjectId, paymentId, paymentStatus) {
        console.log('✅ API Confirm MP Payment:', subjectId, paymentId, paymentStatus);
        const response = await fetch(`${this.BASE_URL}/purchases/confirm-payment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify({
                subject_id: subjectId,
                payment_id: paymentId || 'simulation',
                payment_status: paymentStatus || 'approved'
            })
        });
        return this.handleResponse(response);
    },

    async deleteSubject(subjectId) {
        console.log('🗑️ API Delete Subject:', subjectId);
        return this.handleResponse(
            fetch(`${this.BASE_URL}/subjects/${subjectId}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            })
        );
    },

    async deleteContent(contentId) {
        console.log('🗑️ API Delete Content:', contentId);
        const response = await fetch(`${this.BASE_URL}/content/${contentId}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    },

    async updateSubject(subjectId, subject) {
        console.log('📝 API Update Subject:', subjectId, subject);
        const response = await fetch(`${this.BASE_URL}/subjects/${subjectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...this.getHeaders()
            },
            body: JSON.stringify(subject)
        });
        return this.handleResponse(response);
    },

    // Nuevos métodos para gestión de usuarios
    async getAllUsers() {
        console.log('👥 API Get All Users');
        return this.handleResponse(
            fetch(`${this.BASE_URL}/users/`, {
                headers: this.getHeaders()
            })
        );
    },

    async getUserPurchases(userId) {
        console.log('🛒 API Get User Purchases:', userId);
        return this.handleResponse(
            fetch(`${this.BASE_URL}/purchases/user/${userId}`, {
                headers: this.getHeaders()
            })
        );
    },

    async deleteUser(userId) {
        console.log('🗑️ API Delete User:', userId);
        return this.handleResponse(
            fetch(`${this.BASE_URL}/users/${userId}`, {
                method: 'DELETE',
                headers: this.getHeaders()
            })
        );
    },

    async createUser(userData) {
        console.log('➕ API Create User:', userData);
        return this.handleResponse(
            fetch(`${this.BASE_URL}/users/`, {
                method: 'POST',
                headers: this.getHeaders(),
                body: JSON.stringify(userData)
            })
        );
    },

    async refreshToken(refreshToken) {
        console.log('🔄 API Refresh Token');
        const response = await fetch(`${this.BASE_URL}/auth/refresh-token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken })
        });
        return this.handleResponse(response);
    },

    async getStats() {
        console.log('📊 API Get Stats');
        return this.handleResponse(
            fetch(`${this.BASE_URL}/stats`, {
                headers: this.getHeaders()
            })
        );
    },

    async updateMyProfile(data) {
        console.log('👤 API Update Profile:', data);
        const response = await fetch(`${this.BASE_URL}/users/me`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        return this.handleResponse(response);
    },

    async getRecentPurchases(limit = 20) {
        const response = await fetch(`${this.BASE_URL}/purchases/recent?limit=${limit}`, {
            headers: this.getHeaders()
        });
        return this.handleResponse(response);
    }
};


/*
// Estado de autenticación
let currentUser = null;

// Inicializar autenticación
function initAuth() {
    // ... TODO ESTO COMENTAR ...
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
*/