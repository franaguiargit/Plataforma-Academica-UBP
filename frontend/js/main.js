// Variables globales
let subjects = [];
let myPurchases = [];

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', function() {
    initAuth();
    setupEventListeners();
});

// Event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('login-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        await login(username, password);
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
}

// Cargar dashboard
async function loadDashboard() {
    try {
        // Cargar materias y compras
        subjects = await API.getSubjects();
        myPurchases = await API.getMyPurchases();
        
        // Mostrar contenido según el rol
        if (isAdmin()) {
            showAdminDashboard();
        } else {
            showStudentDashboard();
        }
    } catch (error) {
        showError('Error cargando el dashboard: ' + error.message);
    }
}

// Dashboard para estudiantes
function showStudentDashboard() {
    const contentArea = document.getElementById('content-area');
    
    const purchasedSubjectIds = myPurchases.map(p => p.subject_id);
    
    contentArea.innerHTML = `
        <h2>Materias Disponibles</h2>
        <div class="subjects-grid">
            ${subjects.map(subject => `
                <div class="subject-card">
                    <h3>${subject.title}</h3>
                    <p>${subject.description || 'Sin descripción'}</p>
                    <div class="price">$${subject.price}</div>
                    ${purchasedSubjectIds.includes(subject.id) 
                        ? `<button class="btn btn-success" onclick="viewContent(${subject.id})">Ver Contenido</button>`
                        : `<button class="btn btn-primary" onclick="purchaseSubject(${subject.id})">Comprar</button>`
                    }
                </div>
            `).join('')}
        </div>
    `;
}

// Dashboard para admin
function showAdminDashboard() {
    const contentArea = document.getElementById('content-area');
    
    contentArea.innerHTML = `
        <div style="display: flex; gap: 20px; margin-bottom: 20px;">
            <button class="btn btn-primary" onclick="showCreateSubjectForm()">Crear Materia</button>
            <button class="btn btn-primary" onclick="showCreateContentForm()">Crear Contenido</button>
        </div>
        
        <h2>Todas las Materias</h2>
        <div class="subjects-grid">
            ${subjects.map(subject => `
                <div class="subject-card">
                    <h3>${subject.title}</h3>
                    <p>${subject.description || 'Sin descripción'}</p>
                    <div class="price">$${subject.price}</div>
                    <button class="btn btn-primary" onclick="viewContent(${subject.id})">Ver Contenido</button>
                </div>
            `).join('')}
        </div>
    `;
}

// Comprar materia
async function purchaseSubject(subjectId) {
    try {
        await API.purchaseSubject(subjectId);
        alert('¡Materia comprada exitosamente!');
        loadDashboard(); // Recargar para mostrar cambios
    } catch (error) {
        showError('Error comprando materia: ' + error.message);
    }
}

// Ver contenido de una materia
async function viewContent(subjectId) {
    try {
        const content = await API.getSubjectContent(subjectId);
        const subject = subjects.find(s => s.id === subjectId);
        
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="loadDashboard()">← Volver</button>
            </div>
            <h2>Contenido: ${subject.title}</h2>
            <div class="subjects-grid">
                ${content.length > 0 
                    ? content.map(item => `
                        <div class="subject-card">
                            <h3>${item.title}</h3>
                            <p>${item.description || 'Sin descripción'}</p>
                            <p><strong>Tipo:</strong> ${item.content_type}</p>
                        </div>
                    `).join('')
                    : '<p>No hay contenido disponible para esta materia.</p>'
                }
            </div>
        `;
    } catch (error) {
        showError('Error cargando contenido: ' + error.message);
    }
}

// Mostrar formulario crear materia
function showCreateSubjectForm() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="margin-bottom: 20px;">
            <button class="btn btn-primary" onclick="loadDashboard()">← Volver</button>
        </div>
        <h2>Crear Nueva Materia</h2>
        <div class="login-form" style="margin: 20px 0;">
            <form id="create-subject-form">
                <input type="text" id="subject-title" placeholder="Título de la materia" required>
                <textarea id="subject-description" placeholder="Descripción" rows="4" style="width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                <input type="number" id="subject-price" placeholder="Precio" step="0.01" required>
                <button type="submit">Crear Materia</button>
            </form>
        </div>
    `;
    
    document.getElementById('create-subject-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const subject = {
            title: document.getElementById('subject-title').value,
            description: document.getElementById('subject-description').value,
            price: parseFloat(document.getElementById('subject-price').value)
        };
        
        try {
            await API.createSubject(subject);
            alert('¡Materia creada exitosamente!');
            loadDashboard();
        } catch (error) {
            showError('Error creando materia: ' + error.message);
        }
    });
}

// Mostrar formulario crear contenido
function showCreateContentForm() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div style="margin-bottom: 20px;">
            <button class="btn btn-primary" onclick="loadDashboard()">← Volver</button>
        </div>
        <h2>Crear Contenido</h2>
        <div class="login-form" style="margin: 20px 0;">
            <form id="create-content-form">
                <select id="content-subject" required style="width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="">Seleccionar materia</option>
                    ${subjects.map(subject => `
                        <option value="${subject.id}">${subject.title}</option>
                    `).join('')}
                </select>
                <input type="text" id="content-title" placeholder="Título del contenido" required>
                <textarea id="content-description" placeholder="Descripción" rows="4" style="width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;"></textarea>
                <select id="content-type" required style="width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px;">
                    <option value="">Tipo de contenido</option>
                    <option value="video">Video</option>
                    <option value="document">Documento</option>
                    <option value="quiz">Quiz</option>
                    <option value="assignment">Tarea</option>
                </select>
                <button type="submit">Crear Contenido</button>
            </form>
        </div>
    `;
    
    document.getElementById('create-content-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const content = {
            subject_id: parseInt(document.getElementById('content-subject').value),
            title: document.getElementById('content-title').value,
            description: document.getElementById('content-description').value,
            content_type: document.getElementById('content-type').value
        };
        
        try {
            await API.createContent(content);
            alert('¡Contenido creado exitosamente!');
            loadDashboard();
        } catch (error) {
            showError('Error creando contenido: ' + error.message);
        }
    });
}