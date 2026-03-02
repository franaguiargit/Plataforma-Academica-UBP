// Variables globales
let subjects = [];
let myPurchases = [];
let currentSection = 'dashboard';
let platformStats = null;

// Inicializar aplicación
document.addEventListener('DOMContentLoaded', function() {
    // Ocultar loading después de 1 segundo
    setTimeout(() => {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) loadingScreen.style.display = 'none';
    }, 1000);
    
    initAuth();
    setupEventListeners();
});

// Event listeners
function setupEventListeners() {
    // Login form
    document.getElementById('login-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await login(document.getElementById('username').value, document.getElementById('password').value);
    });
    
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', logout);
    
    // Navigation items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            if (this.dataset.section) navigateToSection(this.dataset.section);
        });
    });
}

// Navigation
function navigateToSection(section) {
    currentSection = section;
    
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.section === section);
    });
    
    // Update page title
    const titles = {
        dashboard: 'Dashboard',
        subjects: 'Materias',
        'my-subjects': 'Mis Materias',
        create: 'Crear',
        students: 'Alumnos',
        profile: 'Mi Perfil'
    };
    
    document.getElementById('page-title').textContent = titles[section] || 'Dashboard';
    
    // Load section content
    switch(section) {
        case 'dashboard': loadDashboardSection(); break;
        case 'subjects': loadSubjectsSection(); break;
        case 'my-subjects': loadMySubjectsSection(); break;
        case 'create': loadCreateSection(); break;
        case 'students': loadStudentsSection(); break;
        case 'profile': loadProfileSection(); break;
    }
}

// Cargar dashboard inicial
async function loadDashboard() {
    try {
        // Cargar datos
        subjects = await API.getSubjects();
        const allPurchases = await API.getMyPurchases();
        // Deduplicar por subject_id y filtrar compras de materias que ya no existen
        const subjectIds = new Set(subjects.map(s => s.id));
        const seen = new Set();
        myPurchases = allPurchases.filter(p => {
            if (!subjectIds.has(p.subject_id)) return false; // materia eliminada
            if (seen.has(p.subject_id)) return false; // duplicada
            seen.add(p.subject_id);
            return true;
        });
        
        // Cargar estadísticas reales
        try {
            platformStats = await API.getStats();
        } catch (e) {
            platformStats = null;
        }
        
        // Mostrar sidebar items según rol
        if (isAdmin() || canCreateContent()) {
            document.querySelectorAll('.admin-only').forEach(item => {
                item.style.display = 'flex';
            });
        }
        
        // Cargar sección dashboard por defecto
        loadDashboardSection();
        
    } catch (error) {
        showError('Error cargando el dashboard: ' + error.message);
    }
}

// Dashboard principal con estadísticas
function loadDashboardSection() {
    const contentArea = document.getElementById('content-area');
    const purchasedSubjectIds = myPurchases.map(p => p.subject_id);
    const availableSubjects = subjects.filter(s => !purchasedSubjectIds.includes(s.id));
    
    const isUserAdmin = currentUser && (currentUser.role === 'admin' || currentUser.role === 'teacher');
    
    let adminStatsHtml = '';
    if (isUserAdmin && platformStats) {
        adminStatsHtml = `
            <div class="stats-section-label">
                <i class="fas fa-chart-line"></i> Estadísticas de la Plataforma
            </div>
            <div class="stats-grid">
                <div class="stat-card stat-card-clickable" onclick="navigateToSection('students')" title="Ver listado de alumnos">
                    <div class="stat-header">
                        <span class="stat-title">Alumnos Registrados</span>
                        <div class="stat-icon info">
                            <i class="fas fa-users"></i>
                        </div>
                    </div>
                    <div class="stat-value">${platformStats.total_students}</div>
                    <div class="stat-change">en la plataforma <i class="fas fa-arrow-right" style="font-size:11px;margin-left:4px"></i></div>
                </div>
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Ingresos Totales</span>
                        <div class="stat-icon success">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                    </div>
                    <div class="stat-value">$${Number(platformStats.total_revenue).toLocaleString('es-AR', {minimumFractionDigits: 2})}</div>
                    <div class="stat-change">recaudados</div>
                </div>
                <div class="stat-card stat-card-clickable" onclick="showRecentPurchases()" title="Ver compras recientes">
                    <div class="stat-header">
                        <span class="stat-title">Materias Vendidas</span>
                        <div class="stat-icon warning">
                            <i class="fas fa-receipt"></i>
                        </div>
                    </div>
                    <div class="stat-value">${platformStats.total_purchases}</div>
                    <div class="stat-change">operaciones de compra <i class="fas fa-arrow-right" style="font-size:11px;margin-left:4px"></i></div>
                </div>
            </div>
        `;
    }
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">¡Bienvenido, ${currentUser.full_name || currentUser.username}!</h1>
                <p class="page-subtitle">Aquí tienes un resumen de tu actividad</p>
            </div>
        </div>
        
        ${isUserAdmin ? '<div class="stats-section-label"><i class="fas fa-user"></i> Tu Resumen</div>' : ''}
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Total Materias</span>
                    <div class="stat-icon primary">
                        <i class="fas fa-book"></i>
                    </div>
                </div>
                <div class="stat-value">${subjects.length}</div>
                <div class="stat-change">en el catálogo</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Mis Compras</span>
                    <div class="stat-icon success">
                        <i class="fas fa-check-circle"></i>
                    </div>
                </div>
                <div class="stat-value">${myPurchases.length}</div>
                <div class="stat-change">materias adquiridas</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <span class="stat-title">Disponibles</span>
                    <div class="stat-icon warning">
                        <i class="fas fa-shopping-cart"></i>
                    </div>
                </div>
                <div class="stat-value">${availableSubjects.length}</div>
                <div class="stat-change">para comprar</div>
            </div>
        </div>
        
        ${adminStatsHtml}
        
        <div class="page-header">
            <div>
                <h2 class="page-title">Materias Destacadas</h2>
                <p class="page-subtitle">Descubre nuestros cursos más populares</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="navigateToSection('subjects')">
                    <i class="fas fa-eye"></i>
                    Ver Todas
                </button>
            </div>
        </div>
        
        <div class="subjects-grid">
            ${subjects.slice(0, 3).map(subject => createSubjectCard(subject, purchasedSubjectIds)).join('')}
        </div>
    `;
}

// Sección de perfil de usuario
function loadProfileSection() {
    const contentArea = document.getElementById('content-area');
    const createdDate = currentUser.created_at 
        ? new Date(currentUser.created_at).toLocaleDateString('es-AR', { year: 'numeric', month: 'long', day: 'numeric' })
        : 'N/A';
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Mi Perfil</h1>
                <p class="page-subtitle">Administra tu información personal</p>
            </div>
        </div>
        
        <div class="profile-container">
            <div class="profile-card">
                <div class="profile-avatar">
                    <div class="avatar-circle">
                        <i class="fas fa-user-circle"></i>
                    </div>
                    <h2>${currentUser.full_name || currentUser.username}</h2>
                    <span class="profile-role-badge ${currentUser.role}">${currentUser.role === 'admin' ? 'Administrador' : currentUser.role === 'teacher' ? 'Profesor' : 'Estudiante'}</span>
                    <p class="profile-since">Miembro desde ${createdDate}</p>
                </div>
                
                <div class="profile-stats-row">
                    <div class="profile-stat">
                        <span class="profile-stat-value">${myPurchases.length}</span>
                        <span class="profile-stat-label">Materias</span>
                    </div>
                    <div class="profile-stat">
                        <span class="profile-stat-value">${subjects.length}</span>
                        <span class="profile-stat-label">Disponibles</span>
                    </div>
                </div>
            </div>
            
            <div class="profile-form-card">
                <h3><i class="fas fa-edit"></i> Editar Información</h3>
                <form id="profile-form" onsubmit="saveProfile(event)">
                    <div class="form-group">
                        <label for="profile-fullname">Nombre Completo</label>
                        <input type="text" id="profile-fullname" value="${currentUser.full_name || ''}" placeholder="Tu nombre completo">
                    </div>
                    <div class="form-group">
                        <label for="profile-email">Email</label>
                        <input type="email" id="profile-email" value="${currentUser.email || ''}" placeholder="tu@email.com">
                    </div>
                    <div class="form-group">
                        <label>Usuario</label>
                        <input type="text" value="${currentUser.username}" disabled class="input-disabled">
                        <small style="color: var(--text-secondary);">El nombre de usuario no se puede cambiar</small>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-primary">
                            <i class="fas fa-save"></i>
                            Guardar Cambios
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
}

// Modal de compras recientes
async function showRecentPurchases() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content recent-purchases-modal">
            <div class="modal-header">
                <h2><i class="fas fa-receipt"></i> Compras Recientes</h2>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="modal-body" style="padding:20px;text-align:center;">
                <div class="loading-spinner" style="width:32px;height:32px;border-width:3px;margin:20px auto;"></div>
                <p style="color:var(--text-secondary)">Cargando...</p>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });

    try {
        const purchases = await API.getRecentPurchases(20);

        const listHtml = purchases.length > 0
            ? `<table class="purchases-table">
                <thead>
                    <tr>
                        <th>Alumno</th>
                        <th>Materia</th>
                        <th>Monto</th>
                        <th>Fecha</th>
                    </tr>
                </thead>
                <tbody>
                    ${purchases.map(p => {
                        const date = p.date ? new Date(p.date).toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'N/A';
                        return `<tr>
                            <td><i class="fas fa-user-circle" style="margin-right:6px;color:var(--primary-color)"></i>${p.user}</td>
                            <td>${p.subject}</td>
                            <td class="amount">$${Number(p.amount).toLocaleString('es-AR', {minimumFractionDigits: 2})}</td>
                            <td class="date">${date}</td>
                        </tr>`;
                    }).join('')}
                </tbody>
               </table>`
            : '<p style="text-align:center;color:var(--text-secondary);padding:40px">No hay compras registradas aún.</p>';

        modal.querySelector('.modal-body').innerHTML = listHtml;
    } catch (err) {
        modal.querySelector('.modal-body').innerHTML = `<p style="color:var(--error-color);padding:20px">Error cargando compras: ${err.message}</p>`;
    }
}

// Guardar perfil
async function saveProfile(event) {
    event.preventDefault();
    const fullName = document.getElementById('profile-fullname').value.trim();
    const email = document.getElementById('profile-email').value.trim();
    
    if (!email) {
        showError('El email es obligatorio');
        return;
    }
    
    try {
        const updated = await API.updateMyProfile({ full_name: fullName, email: email });
        currentUser = { ...currentUser, ...updated };
        document.getElementById('user-name').textContent = currentUser.full_name || currentUser.username;
        showSuccess('Perfil actualizado correctamente');
        loadProfileSection();
    } catch (error) {
        showError('Error actualizando perfil: ' + error.message);
    }
}

// Sección de materias
function loadSubjectsSection() {
    const contentArea = document.getElementById('content-area');
    const purchasedSubjectIds = myPurchases.map(p => p.subject_id);
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Todas las Materias</h1>
                <p class="page-subtitle">Explora nuestro catálogo completo de cursos</p>
            </div>
            ${isAdmin() ? `
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="showCreateSubjectForm()">
                    <i class="fas fa-plus"></i>
                    Nueva Materia
                </button>
            </div>
            ` : ''}
        </div>
        
        <div class="search-bar">
            <i class="fas fa-search search-icon"></i>
            <input type="text" id="subject-search" placeholder="Buscar materias por nombre o descripción..." oninput="filterSubjects(this.value)">
            <button class="search-clear hidden" id="search-clear" onclick="clearSearch()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div class="subjects-grid" id="subjects-grid">
            ${subjects.map(subject => createSubjectCard(subject, purchasedSubjectIds)).join('')}
        </div>
    `;
}

// Filtrar materias por búsqueda
function filterSubjects(query) {
    const clearBtn = document.getElementById('search-clear');
    if (clearBtn) clearBtn.classList.toggle('hidden', !query);
    
    const purchasedSubjectIds = myPurchases.map(p => p.subject_id);
    const grid = document.getElementById('subjects-grid');
    if (!grid) return;
    
    const q = query.toLowerCase().trim();
    const filtered = q 
        ? subjects.filter(s => 
            s.title.toLowerCase().includes(q) || 
            (s.description && s.description.toLowerCase().includes(q)))
        : subjects;
    
    grid.innerHTML = filtered.length > 0
        ? filtered.map(subject => createSubjectCard(subject, purchasedSubjectIds)).join('')
        : `<div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
            <i class="fas fa-search" style="font-size: 48px; color: var(--text-secondary); margin-bottom: 20px;"></i>
            <h3>No se encontraron resultados</h3>
            <p style="color: var(--text-secondary);">Intenta con otro término de búsqueda</p>
           </div>`;
}

function clearSearch() {
    const input = document.getElementById('subject-search');
    if (input) { input.value = ''; filterSubjects(''); input.focus(); }
}

// Crear card de materia
function createSubjectCard(subject) {
    const isPurchased = myPurchases.some(p => p.subject_id === subject.id);
    const isAdmin = currentUser && (currentUser.role === 'admin' || currentUser.role === 'teacher');
    
    return `
        <div class="subject-card ${isPurchased ? 'purchased' : ''}">
            <div class="subject-card-header">
                <div class="subject-icon">
                    <i class="fas fa-book"></i>
                </div>
                ${isPurchased ? '<span class="purchased-badge"><i class="fas fa-check"></i> Comprada</span>' : ''}
            </div>
            <div class="subject-card-body">
                <h3 class="subject-title">${subject.title}</h3>
                <p class="subject-description">${subject.description || 'Sin descripción disponible'}</p>
            </div>
            <div class="subject-card-footer">
                <div class="subject-price">
                    <span class="price-label">Precio:</span>
                    <span class="price-value">$${subject.price}</span>
                </div>
                <div class="subject-actions">
                    ${isPurchased 
                        ? `<button class="btn btn-primary" onclick="viewSubjectContent(${subject.id})">
                            <i class="fas fa-play"></i> Ver Contenido
                           </button>`
                        : `<button class="btn btn-success" onclick="purchaseSubject(${subject.id})">
                            <i class="fas fa-shopping-cart"></i> Comprar
                           </button>`
                    }
                    ${isAdmin 
                        ? `<button class="btn btn-secondary" onclick="manageSubjectContent(${subject.id})">
                            <i class="fas fa-cog"></i> Gestionar
                           </button>
                           <button class="btn btn-danger" onclick="deleteSubject(${subject.id}, '${subject.title}')">
                            <i class="fas fa-trash"></i> Eliminar
                           </button>`
                        : ''
                    }
                </div>
            </div>
        </div>
    `;
}

// ==========================================
// MERCADOPAGO CHECKOUT
// ==========================================

// Comprar materia (con MercadoPago)
async function purchaseSubject(subjectId) {
    if (!currentUser) {
        showError('Debes estar logueado para comprar');
        return;
    }

    const subject = subjects.find(s => s.id === parseInt(subjectId));
    if (!subject) {
        showError('Materia no encontrada');
        return;
    }

    try {
        console.log('\ud83d\udcb3 Creando preferencia de pago para materia:', subjectId);
        
        // Crear preferencia en el backend (MercadoPago o simulación)
        const preference = await API.createMPPreference(parseInt(subjectId));
        console.log('\ud83d\udccb Preferencia creada:', preference);
        
        if (preference.simulation) {
            // Modo simulación: mostrar modal de checkout MercadoPago
            showMPCheckoutModal(subject, preference);
        } else if (preference.sandbox_init_point || preference.init_point) {
            // Modo real: redirigir a MercadoPago
            window.location.href = preference.sandbox_init_point || preference.init_point;
        } else {
            // Fallback a simulación
            showMPCheckoutModal(subject, preference);
        }
        
    } catch (error) {
        console.error('Error creando preferencia:', error);
        showError('Error procesando pago: ' + error.message);
    }
}


// Resolver ID de materia desde el input
function resolveSubjectId(source) {
    if (source === null || source === undefined) return null;
    if (typeof source === 'string' || typeof source === 'number') {
        return source;
    }
    const element = source.currentTarget ?? source.target ?? null;
    const card = element?.closest('[data-subject-id]');
    return card?.dataset.subjectId ?? null;
}

// Ver contenido de una materia
function viewSubjectContent(source) {
    const subjectId = resolveSubjectId(source);
    if (!subjectId) {
        console.error('Subject ID no encontrado');
        return;
    }
    
    // ✅ PASAR EL subjectId directamente
    API.getSubjectContent(subjectId)
        .then(content => renderSubjectContent(content, subjectId))
        .catch(err => showError(`Error cargando contenido: ${err.message}`));
}

// Gestionar contenido de materia (Admin)
async function manageSubjectContent(input) {
    const subjectId = resolveSubjectId(input);
    if (!subjectId) {
        console.error('Subject ID no encontrado');
        return;
    }
    
    // ✅ PASAR EL subjectId directamente
    API.getSubjectContent(subjectId)
        .then(content => renderContentManager(content, subjectId))
        .catch(err => showError(`Error cargando contenido: ${err.message}`));
}

// Renderizar contenido de materia
function renderSubjectContent(content, subjectId) {
    currentContent = content; // ✅ AGREGAR ESTA LÍNEA
    const contentArea = document.getElementById('content-area');
    
    const subject = subjects.find(s => s.id == subjectId) || { title: 'Materia' };
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">${subject.title}</h1>
                <p class="page-subtitle">Contenido del curso</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="navigateToSection('subjects')">
                    <i class="fas fa-arrow-left"></i>
                    Volver
                </button>
            </div>
        </div>
        
        <div class="content-grid">
            ${content.length > 0 
                ? content.map(item => `
                    <div class="content-card slide-in-right">
                        <div class="content-type ${item.content_type}">
                            <i class="fas fa-${getContentIcon(item.content_type)}"></i>
                            ${item.content_type}
                        </div>
                        <h3>${item.title}</h3>
                        <p>${item.description || 'Sin descripción'}</p>
                        <button class="btn btn-primary" onclick="openContent(${item.id})">
                            <i class="fas fa-play"></i>
                            Abrir
                        </button>
                    </div>
                `).join('')
                : `<div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px;">
                    <i class="fas fa-inbox" style="font-size: 48px; color: var(--text-secondary); margin-bottom: 20px;"></i>
                    <h3>No hay contenido disponible</h3>
                    <p style="color: var(--text-secondary);">Este curso aún no tiene contenido publicado.</p>
                   </div>`
            }
        </div>
    `;
}

// Renderizar gestión de contenido
function renderContentManager(content, subjectId) {
    const contentArea = document.getElementById('content-area');
    
    // ✅ Usar el subjectId que recibimos
    const subject = subjects.find(s => s.id == subjectId) || { title: 'Materia', price: 0 };
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">Gestionar: ${subject.title}</h1>
                <p class="page-subtitle">Administración de materia y contenido</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="navigateToSection('subjects')">
                    <i class="fas fa-arrow-left"></i>
                    Volver a Materias
                </button>
            </div>
        </div>

        <!-- Información de la materia -->
        <div class="management-section">
            <div class="section-header">
                <h3><i class="fas fa-info-circle"></i> Información de la Materia</h3>
                <div class="section-actions">
                    <button class="btn btn-warning" onclick="editSubject(${subjectId})">
                        <i class="fas fa-edit"></i>
                        Editar Materia
                    </button>
                    <button class="btn btn-danger" onclick="deleteSubjectConfirm(${subjectId}, '${subject.title}')">
                        <i class="fas fa-trash"></i>
                        Eliminar Materia
                    </button>
                </div>
            </div>
            <div class="subject-info-card">
                <div class="info-grid">
                    <div class="info-item">
                        <label>Título:</label>
                        <span>${subject.title}</span>
                    </div>
                    <div class="info-item">
                        <label>Precio:</label>
                        <span class="price-display">$${subject.price}</span>
                    </div>
                    <div class="info-item">
                        <label>Descripción:</label>
                        <span>${subject.description || 'Sin descripción'}</span>
                    </div>
                    <div class="info-item">
                        <label>Contenidos:</label>
                        <span>${content.length} elemento(s)</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Gestión de contenido -->
        <div class="management-section">
            <div class="section-header">
                <h3><i class="fas fa-play-circle"></i> Contenido de la Materia</h3>
                <div class="section-actions">
                    <button class="btn btn-primary" onclick="showCreateContentFormForSubject(${subjectId})">
                        <i class="fas fa-plus"></i>
                        Agregar Contenido
                    </button>
                </div>
            </div>
            <div class="content-management-grid">
                ${content.length > 0 
                    ? content.map(item => createContentManagementCard(item)).join('')
                    : `<div class="no-content">
                        <i class="fas fa-folder-open"></i>
                        <h4>Sin contenido</h4>
                        <p>Esta materia no tiene contenido agregado aún.</p>
                        <button class="btn btn-primary" onclick="showCreateContentFormForSubject(${subjectId})">
                            <i class="fas fa-plus"></i>
                            Agregar Primer Contenido
                        </button>
                       </div>`
                }
            </div>
        </div>

        <!-- Estadísticas de compras -->
        <div class="management-section">
            <div class="section-header">
                <h3><i class="fas fa-chart-bar"></i> Estadísticas de Ventas</h3>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Estudiantes</span>
                        <div class="stat-icon primary">
                            <i class="fas fa-users"></i>
                        </div>
                    </div>
                    <div class="stat-value">${getPurchaseCount(subjectId)}</div>
                    <div class="stat-change">compraron esta materia</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Ingresos</span>
                        <div class="stat-icon success">
                            <i class="fas fa-dollar-sign"></i>
                        </div>
                    </div>
                    <div class="stat-value">$${(getPurchaseCount(subjectId) * subject.price).toFixed(2)}</div>
                    <div class="stat-change">total generado</div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-header">
                        <span class="stat-title">Popularidad</span>
                        <div class="stat-icon warning">
                            <i class="fas fa-star"></i>
                        </div>
                    </div>
                    <div class="stat-value">${getTotalStudents() > 0 ? Math.round((getPurchaseCount(subjectId) / getTotalStudents()) * 100) : 0}%</div>
                    <div class="stat-change">de estudiantes</div>
                </div>
            </div>
        </div>
    `;
}

// Nueva función para agregar contenido desde gestión
function showCreateContentFormForSubject(subjectId) {
    showCreateContentForm();
    // Preseleccionar la materia
    setTimeout(() => {
        const select = document.getElementById('content-subject');
        if (select) {
            select.value = subjectId;
        }
    }, 100);
}


// Funciones auxiliares
function getPurchaseCount(subjectId) {
    if (platformStats && platformStats.per_subject && platformStats.per_subject[subjectId]) {
        return platformStats.per_subject[subjectId].purchases || 0;
    }
    return 0;
}

function getTotalStudents() {
    if (platformStats) return platformStats.total_students || 0;
    return 0;
}

function getContentIcon(type) {
    const icons = {
        video: 'play-circle',
        document: 'file-alt',
        quiz: 'question-circle',
        assignment: 'tasks'
    };
    return icons[type] || 'file';
}

function getContentTypeLabel(type) {
    const labels = {
        video: 'Video',
        document: 'Documento', 
        quiz: 'Quiz',
        assignment: 'Tarea'
    };
    return labels[type] || 'Contenido';
}

// Confirmar eliminación de contenido
async function deleteContentConfirm(contentId, contentTitle) {
    if (confirm(`¿Estás seguro de eliminar el contenido "${contentTitle}"?\n\nEsta acción NO se puede deshacer.`)) {
        try {
            // Mostrar loading en el botón
            const deleteBtn = document.querySelector(`button[onclick="deleteContentConfirm(${contentId}, '${contentTitle}')"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                deleteBtn.disabled = true;
            }

            console.log('Eliminando contenido ID:', contentId);
            
            // Llamar a la API
            await API.deleteContent(contentId);
            
            console.log('Contenido eliminado exitosamente');
            
            // Remover del DOM con animación
            const contentCard = document.querySelector(`[data-content-id="${contentId}"]`);
            if (contentCard) {
                contentCard.style.animation = 'fadeOut 0.3s ease-out forwards';
                setTimeout(() => {
                    contentCard.remove();
                }, 300);
            }
            
            showSuccess(`Contenido "${contentTitle}" eliminado exitosamente`);
            
        } catch (error) {
            console.error('Error eliminando contenido:', error);
            
            // Restaurar botón
            const deleteBtn = document.querySelector(`button[onclick="deleteContentConfirm(${contentId}, '${contentTitle}')"]`);
            if (deleteBtn) {
                deleteBtn.innerHTML = '<i class="fas fa-trash"></i>';
                deleteBtn.disabled = false;
            }
            
            showError('Error eliminando contenido: ' + error.message);
        }
    }
}

// Confirmar eliminación de materia
async function deleteSubjectConfirm(subjectId, subjectTitle) {
    if (confirm(`⚠️ ¿Estás seguro de eliminar la materia "${subjectTitle}"?\n\n⚠️ ADVERTENCIA: Esto también eliminará TODO su contenido y NO se puede deshacer.\n\n¿Continuar?`)) {
        try {
            console.log('🗑️ Eliminando materia ID:', subjectId);
            
            await API.deleteSubject(subjectId);
            
            console.log('✅ Materia eliminada exitosamente');
            
            showSuccess(`Materia "${subjectTitle}" eliminada exitosamente`);
            
            // Recargar materias
            subjects = await API.getSubjects();
            
            // Volver a la lista de materias
            navigateToSection('subjects');
            
        } catch (error) {
            console.error('❌ Error eliminando materia:', error);
            showError('Error eliminando materia: ' + error.message);
        }
    }
}

// También falta deleteSubject para compatibilidad:
async function deleteSubject(subjectId, subjectTitle) {
    deleteSubjectConfirm(subjectId, subjectTitle);
}

// REEMPLAZAR la función editSubject:

function editSubject(subjectId) {
    const subject = subjects.find(s => s.id === subjectId);
    if (!subject) {
        showError('Materia no encontrada');
        return;
    }

    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">
                    <i class="fas fa-edit"></i>
                    Editar Materia
                </h1>
                <p class="page-subtitle">Modificar información de: <strong>${subject.title}</strong></p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="manageSubjectContent(${subjectId})">
                    <i class="fas fa-arrow-left"></i>
                    Cancelar
                </button>
            </div>
        </div>

        <div class="subject-form">
            <form onsubmit="updateSubject(event, ${subjectId})">
                <div class="form-group">
                    <label for="edit-subject-title">
                        <i class="fas fa-book"></i>
                        Título de la Materia *
                    </label>
                    <input 
                        type="text" 
                        id="edit-subject-title" 
                        required 
                        value="${subject.title}"
                        placeholder="Ej: Matemáticas Básicas"
                    >
                </div>
                
                <div class="form-group">
                    <label for="edit-subject-description">
                        <i class="fas fa-align-left"></i>
                        Descripción
                    </label>
                    <textarea 
                        id="edit-subject-description" 
                        rows="4"
                        placeholder="Describe el contenido y objetivos de la materia..."
                    >${subject.description || ''}</textarea>
                </div>
                
                <div class="form-group">
                    <label for="edit-subject-price">
                        <i class="fas fa-dollar-sign"></i>
                        Precio *
                    </label>
                    <input 
                        type="number" 
                        id="edit-subject-price" 
                        step="0.01" 
                        min="0"
                        required 
                        value="${subject.price}"
                        placeholder="0.00"
                    >
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="manageSubjectContent(${subjectId})">
                        <i class="fas fa-times"></i>
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i>
                        Guardar Cambios
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Función para actualizar materia
async function updateSubject(event, subjectId) {
    event.preventDefault();
    
    const title = document.getElementById('edit-subject-title').value;
    const description = document.getElementById('edit-subject-description').value;
    const price = parseFloat(document.getElementById('edit-subject-price').value);
    
    console.log('💾 Guardando materia:', { subjectId, title, description, price });
    
    try {
        const updatedSubject = { title, description, price };
        console.log('📤 Enviando a API:', updatedSubject);
        
        const result = await API.updateSubject(subjectId, updatedSubject);
        console.log('✅ Respuesta API:', result);
        
        showSuccess('Materia actualizada exitosamente! 🎉');
        
        // Recargar materias
        subjects = await API.getSubjects();
        console.log('🔄 Materias recargadas:', subjects);
        
        // Volver a gestión
        setTimeout(() => {
            manageSubjectContent(subjectId);
        }, 1000);
        
    } catch (error) {
        console.error('❌ Error completo:', error);
        showError('Error actualizando materia: ' + error.message);
    }
}

// REEMPLAZAR la función initNotifications COMPLETA:

function initNotifications() {
    console.log('🔔 Inicializando notificaciones...');
    
    const notificationBtn = document.querySelector('.notifications');
    console.log('🔔 Botón encontrado:', notificationBtn);
    
    if (!notificationBtn) {
        console.error('❌ No se encontró el botón de notificaciones');
        return;
    }
    
    // Limpiar eventos previos
    const newBtn = notificationBtn.cloneNode(true);
    notificationBtn.parentNode.replaceChild(newBtn, notificationBtn);
    
    // Agregar evento de click
    newBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔔 Click en notificaciones');
        toggleNotifications();
    });
    
    console.log('✅ Notificaciones inicializadas');
    
    // Actualizar badge
    updateNotificationBadge();
}

// Función para abrir/cerrar panel de notificaciones
function toggleNotifications() {
    console.log('🔔 Toggle notifications');
    
    // Verificar si ya existe el panel
    let panel = document.getElementById('notification-panel');
    
    if (panel) {
        // Si existe, cerrarlo
        panel.remove();
        return;
    }
    
    // Crear panel de notificaciones
    panel = document.createElement('div');
    panel.id = 'notification-panel';
    panel.className = 'notification-panel';
    
    const notifications = getNotifications();
    console.log('📬 Notificaciones:', notifications);
    
    panel.innerHTML = `
        <div class="notification-header">
            <h3>
                <i class="fas fa-bell"></i>
                Notificaciones
            </h3>
            <button class="btn-close-panel" onclick="closeNotificationPanel()">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="notification-list">
            ${notifications.length > 0 
                ? notifications.map(n => `
                    <div class="notification-item ${n.read ? 'read' : 'unread'}">
                        <div class="notification-icon">
                            <i class="fas fa-${n.type === 'purchase' ? 'shopping-cart' : n.type === 'new_subject' ? 'book' : 'info-circle'}"></i>
                        </div>
                        <div class="notification-content">
                            <h4>${n.title}</h4>
                            <p>${n.message}</p>
                            <span class="notification-time">${formatNotificationTime(n.timestamp)}</span>
                        </div>
                        ${!n.read ? `<button class="btn-mark-read" onclick="markAsRead(${n.id})"><i class="fas fa-check"></i></button>` : ''}
                    </div>
                `).join('')
                : '<div class="no-notifications"><i class="fas fa-inbox"></i><p>No tienes notificaciones</p></div>'
            }
        </div>
        ${notifications.length > 0 ? `
            <div class="notification-footer">
                <button class="btn btn-sm btn-secondary" onclick="markAllAsRead()">
                    <i class="fas fa-check-double"></i> Marcar todas como leídas
                </button>
            </div>
        ` : ''}
    `;
    
    document.body.appendChild(panel);
    
    // Cerrar al hacer click fuera
    setTimeout(() => {
        document.addEventListener('click', closeOnClickOutside);
    }, 100);
}

// Cerrar panel de notificaciones
function closeNotificationPanel() {
    const panel = document.getElementById('notification-panel');
    if (panel) {
        panel.remove();
        document.removeEventListener('click', closeOnClickOutside);
    }
}

// Cerrar al hacer click fuera del panel
function closeOnClickOutside(e) {
    const panel = document.getElementById('notification-panel');
    const notificationBtn = document.querySelector('.notifications');
    
    if (panel && !panel.contains(e.target) && !notificationBtn.contains(e.target)) {
        closeNotificationPanel();
    }
}

// Formatear tiempo de notificación
function formatNotificationTime(timestamp) {
    const now = new Date();
    const time = new Date(timestamp);
    const diff = now - time;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (minutes < 1) return 'Ahora';
    if (minutes < 60) return `Hace ${minutes} min`;
    if (hours < 24) return `Hace ${hours} h`;
    return `Hace ${days} días`;
}

// Mostrar formulario para crear contenido
function showCreateContentForm() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <h1 class="page-title">Crear Nuevo Contenido</h1>
            <button class="btn btn-secondary" onclick="navigateToSection('subjects')">
                <i class="fas fa-arrow-left"></i> Volver
            </button>
        </div>
        
        <div class="form-container">
            <form id="create-content-form" class="content-form">
                <div class="form-group">
                    <label for="content-subject">Materia *</label>
                    <select id="content-subject" required>
                        <option value="">Seleccionar materia...</option>
                        ${subjects.map(s => `<option value="${s.id}">${s.title}</option>`).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="content-title">Título *</label>
                    <input type="text" id="content-title" required placeholder="Ej: Introducción al tema">
                </div>
                
                <div class="form-group">
                    <label for="content-type">Tipo de Contenido *</label>
                    <select id="content-type" required>
                        <option value="">Seleccionar tipo...</option>
                        <option value="video">Video</option>
                        <option value="enlace">Enlace</option>
                        <option value="documento">Documento</option>
                        <option value="pdf">PDF</option>
                        <option value="presentacion">Presentación</option>
                        <option value="ejercicio">Ejercicio</option>
                    </select>
                </div>
                
                <div class="form-group" id="url-group" style="display: none;">
                    <label for="content-url">URL del Contenido *</label>
                    <input type="url" id="content-url" placeholder="https://...">
                    <small>URL del video o enlace externo</small>
                </div>
                
                <div class="form-group" id="file-group" style="display: none;">
                    <label for="content-file">Archivo *</label>
                    <input type="file" id="content-file" accept=".pdf,.doc,.docx,.ppt,.pptx">
                    <small>Sube el archivo del contenido</small>
                </div>
                
                <div class="form-group">
                    <label for="content-description">Descripción</label>
                    <textarea id="content-description" rows="4" placeholder="Describe el contenido..."></textarea>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Crear Contenido
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="navigateToSection('subjects')">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    `;
    
    // ✅ Manejar cambio de tipo de contenido
    const typeSelect = document.getElementById('content-type');
    const urlGroup = document.getElementById('url-group');
    const fileGroup = document.getElementById('file-group');
    const urlInput = document.getElementById('content-url');
    const fileInput = document.getElementById('content-file');
    
    typeSelect.addEventListener('change', (e) => {
        const type = e.target.value;
        
        if (type === 'video' || type === 'enlace') {
            // Mostrar campo URL
            urlGroup.style.display = 'block';
            fileGroup.style.display = 'none';
            urlInput.required = true;
            fileInput.required = false;
        } else if (type === 'documento' || type === 'pdf' || type === 'presentacion' || type === 'ejercicio') {
            // Mostrar campo archivo
            urlGroup.style.display = 'none';
            fileGroup.style.display = 'block';
            urlInput.required = false;
            fileInput.required = true;
        } else {
            // Ocultar ambos
            urlGroup.style.display = 'none';
            fileGroup.style.display = 'none';
            urlInput.required = false;
            fileInput.required = false;
        }
    });
    
    // Manejar submit
    document.getElementById('create-content-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const type = document.getElementById('content-type').value;
        let contentUrl = '';
        
        if (type === 'documento' || type === 'pdf' || type === 'presentacion' || type === 'ejercicio') {
            const file = document.getElementById('content-file').files[0];
            if (!file) {
                showError('Debes seleccionar un archivo');
                return;
            }
            
            try {
                contentUrl = await uploadFile(file);
            } catch (error) {
                showError(`Error subiendo archivo: ${error.message}`);
                return;
            }
        } else {
            contentUrl = document.getElementById('content-url').value;
        }
        
        const contentData = {
            subject_id: parseInt(document.getElementById('content-subject').value),
            title: document.getElementById('content-title').value,
            content_type: type,
            content_url: contentUrl,
            description: document.getElementById('content-description').value || null,
            duration: null,  // ✅ Siempre null
            order_index: 1   // ✅ Siempre 1
        };
        
        try {
            await API.createContent(contentData);
            showSuccess('Contenido creado exitosamente');
            navigateToSection('content');
        } catch (error) {
            showError(`Error creando contenido: ${error.message}`);
        }
    });
}

// REEMPLAZAR la función uploadFile completamente:

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('http://127.0.0.1:5000/content/upload', {  // ✅ URL hardcodeada
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText || 'Error subiendo archivo');
        }
        
        const data = await response.json();
        console.log('✅ Archivo subido:', data);
        
        // Retornar URL completa
        return `http://127.0.0.1:5000${data.url}`;
    } catch (error) {
        console.error('❌ Error upload:', error);
        throw error;
    }
}

// Variable global para trackear contenido actual
let currentContent = [];

// Abrir contenido específico
// ==========================================
// PROGRESS TRACKING (localStorage)
// ==========================================
function getProgress() {
    try {
        return JSON.parse(localStorage.getItem('contentProgress') || '{}');
    } catch { return {}; }
}

function markContentViewed(contentId, subjectId) {
    const progress = getProgress();
    const key = `s${subjectId}`;
    if (!progress[key]) progress[key] = [];
    if (!progress[key].includes(contentId)) {
        progress[key].push(contentId);
        localStorage.setItem('contentProgress', JSON.stringify(progress));
    }
}

function getSubjectProgress(subjectId) {
    const progress = getProgress();
    return progress[`s${subjectId}`] || [];
}

function openContent(contentId) {
    console.log('🎬 Opening content:', contentId);
    
    // Buscar el contenido en el array actual
    const content = currentContent.find(c => c.id === contentId);
    if (!content) {
        showError('Contenido no encontrado');
        return;
    }
    
    // Track progress
    if (content.subject_id) {
        markContentViewed(contentId, content.subject_id);
    }
    
    console.log('📄 Content data:', content);
    
    // Abrir según el tipo
    if (content.content_type === 'video') {
        showContentModal(content);
    } else if (content.content_type === 'documento' || content.content_type === 'pdf') {
        showContentModal(content);
    } else if (content.content_type === 'enlace') {
        window.open(content.content_url, '_blank');
    } else {
        // Para otros tipos, intentar abrir en nueva pestaña
        window.open(content.content_url, '_blank');
    }
}

// Mostrar contenido en modal
function showContentModal(content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 90%; max-height: 90vh;">
            <div class="modal-header">
                <h2>${content.title}</h2>
                <button class="btn-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body" style="height: 70vh; overflow: auto;">
                ${content.content_type === 'video' 
                    ? `<video controls style="width: 100%; height: 100%;">
                         <source src="${content.content_url}" type="video/mp4">
                         Tu navegador no soporta video.
                       </video>`
                    : `<iframe src="${content.content_url}" style="width: 100%; height: 100%; border: none;"></iframe>`
                }
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

// Cerrar modal
function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) modal.remove();
}

// Mostrar formulario para crear materia
function showCreateSubjectForm() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">
                    <i class="fas fa-plus-circle"></i>
                    Crear Nueva Materia
                </h1>
                <p class="page-subtitle">Agrega una nueva materia al catálogo</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="navigateToSection('subjects')">
                    <i class="fas fa-arrow-left"></i>
                    Cancelar
                </button>
            </div>
        </div>

        <div class="subject-form">
            <form id="create-subject-form" onsubmit="createSubject(event)">
                <div class="form-group">
                    <label for="subject-title">
                        <i class="fas fa-book"></i>
                        Título de la Materia *
                    </label>
                    <input 
                        type="text" 
                        id="subject-title" 
                        required 
                        placeholder="Ej: Matemáticas Básicas"
                    >
                </div>
                
                <div class="form-group">
                    <label for="subject-description">
                        <i class="fas fa-align-left"></i>
                        Descripción
                    </label>
                    <textarea 
                        id="subject-description" 
                        rows="4"
                        placeholder="Describe el contenido y objetivos de la materia..."
                    ></textarea>
                </div>
                
                <div class="form-group">
                    <label for="subject-price">
                        <i class="fas fa-dollar-sign"></i>
                        Precio *
                    </label>
                    <input 
                        type="number" 
                        id="subject-price" 
                        step="0.01" 
                        min="0"
                        required 
                        placeholder="0.00"
                    >
                </div>
                
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="navigateToSection('subjects')">
                        <i class="fas fa-times"></i>
                        Cancelar
                    </button>
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i>
                        Crear Materia
                    </button>
                </div>
            </form>
        </div>
    `;
}

// Función para crear materia
async function createSubject(event) {
    event.preventDefault();
    
    const title = document.getElementById('subject-title').value;
    const description = document.getElementById('subject-description').value;
    const price = parseFloat(document.getElementById('subject-price').value);
    
    console.log('📝 Creando materia:', { title, description, price });
    
    try {
        const newSubject = { title, description, price };
        
        const result = await API.createSubject(newSubject);
        console.log('✅ Materia creada:', result);
        
        showSuccess('¡Materia creada exitosamente! 🎉');
        
        // Enviar notificación a todos los estudiantes
        addNotificationToAllStudents(
            'new_subject',
            'Nueva materia disponible! 📚',
            `Ya puedes inscribirte en: ${title}`
        );
        
        // Recargar materias
        subjects = await API.getSubjects();
        
        // Volver a la sección de materias
        setTimeout(() => {
            navigateToSection('subjects');
        }, 1000);
        
    } catch (error) {
        console.error('❌ Error creando materia:', error);
        showError('Error creando materia: ' + error.message);
    }
}

// Al final de la función showDashboard, CAMBIAR la llamada:
function showDashboard(user) {
    console.log('🏠 Mostrando dashboard para:', user);
    currentUser = user;
    
    // Ocultar login, mostrar dashboard
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('dashboard-section').classList.remove('hidden');
    
    // Actualizar información del usuario
    document.getElementById('user-name').textContent = user.full_name || user.username;
    document.getElementById('user-role').textContent = getRoleLabel(user.role);
    
    // Controlar visibilidad según rol
    const adminItems = document.querySelectorAll('.admin-only');
    const studentItems = document.querySelectorAll('.student-only');
    
    if (user.role === 'student') {
        adminItems.forEach(item => item.style.display = 'none');
        studentItems.forEach(item => item.style.display = 'flex');
        document.body.classList.add('student');
        document.body.classList.remove('admin');
    } else if (user.role === 'admin' || user.role === 'teacher') {
        adminItems.forEach(item => item.style.display = 'flex');
        studentItems.forEach(item => item.style.display = 'none');
        document.body.classList.add('admin');
        document.body.classList.remove('student');
    }
    
    // Cargar dashboard
    loadDashboard();
    
    // ✅ INICIALIZAR NOTIFICACIONES DESPUÉS DE QUE EL DOM ESTÉ LISTO
    setTimeout(() => {
        initNotifications();
    }, 500);
}

// Obtener notificaciones del usuario
function getNotifications() {
    if (!currentUser) return [];
    
    const notifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    
    // ✅ Filtrar: notificaciones del usuario actual O notificaciones globales (userId === null)
    return notifications.filter(n => n.userId === currentUser.id || n.userId === null);
}

// Actualizar badge de notificaciones
function updateNotificationBadge() {
    const notifications = getNotifications();
    const unreadCount = notifications.filter(n => !n.read).length;
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
    }
}

// Marcar notificación como leída
function markAsRead(notificationId) {
    const notifications = getNotifications();
    const notification = notifications.find(n => n.id === notificationId);
    if (notification) {
        notification.read = true;
        saveNotifications(notifications);
        toggleNotifications(); // Refrescar panel
    }
}

// Marcar todas como leídas
function markAllAsRead() {
    const notifications = getNotifications();
    notifications.forEach(n => n.read = true);
    saveNotifications(notifications);
    toggleNotifications(); // Refrescar panel
}

// Guardar notificaciones en localStorage
function saveNotifications(notifications) {
    const allNotifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    // Actualizar solo las del usuario actual
    const otherNotifications = allNotifications.filter(n => n.userId !== currentUser.id && n.userId);
    const merged = [...otherNotifications, ...notifications];
    localStorage.setItem('notifications', JSON.stringify(merged));
    updateNotificationBadge();
}

// Agregar notificación
function addNotification(type, title, message) {
    const notifications = getNotifications();
    const newNotification = {
        id: Date.now(),
        userId: currentUser.id,
        type,
        title,
        message,
        timestamp: new Date().toISOString(),
        read: false
    };
    notifications.unshift(newNotification);
    saveNotifications(notifications);
}

// Agregar notificación a todos los estudiantes
function addNotificationToAllStudents(type, title, message) {
    console.log('📢 Creando notificación global:', { type, title, message });
    
    // Obtener todas las notificaciones existentes
    const allNotifications = JSON.parse(localStorage.getItem('notifications') || '[]');
    
    // ✅ Crear nueva notificación SIN userId específico (será visible para todos)
    const newNotification = {
        id: Date.now(),
        userId: null,  // ✅ null = visible para todos los usuarios
        type,
        title,
        message,
        timestamp: new Date().toISOString(),
        read: false
    };
    
    // Agregar al inicio del array
    allNotifications.unshift(newNotification);
    
    // Guardar en localStorage
    localStorage.setItem('notifications', JSON.stringify(allNotifications));
    
    console.log('✅ Notificación global guardada');
    
    // Actualizar badge si el usuario actual está logueado
    if (currentUser) {
        updateNotificationBadge();
    }
}

// Cargar sección de Crear
function loadCreateSection() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">
                    <i class="fas fa-plus-circle"></i>
                    Crear Nuevo Contenido
                </h1>
                <p class="page-subtitle">Elige qué deseas crear</p>
            </div>
        </div>

        <div class="create-options">
            <div class="create-option-card" onclick="showCreateSubjectForm()">
                <div class="create-icon">
                    <i class="fas fa-book"></i>
                </div>
                <h3>Nueva Materia</h3>
                <p>Crear una nueva materia en el catálogo</p>
            </div>

            <div class="create-option-card" onclick="showCreateContentForm()">
                <div class="create-icon">
                    <i class="fas fa-file-alt"></i>
                </div>
                <h3>Nuevo Contenido</h3>
                <p>Agregar contenido a una materia existente</p>
            </div>

            <div class="create-option-card" onclick="showCreateUserForm()">
                <div class="create-icon">
                    <i class="fas fa-user-plus"></i>
                </div>
                <h3>Nuevo Usuario</h3>
                <p>Crear un nuevo estudiante o profesor</p>
            </div>
        </div>
    `;
}

// Función para crear usuario (placeholder)
function showCreateUserForm() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <h1 class="page-title">Crear Nuevo Usuario</h1>
            <button class="btn btn-secondary" onclick="loadCreateSection()">
                <i class="fas fa-arrow-left"></i> Volver
            </button>
        </div>
        
        <div class="form-container">
            <form id="create-user-form">
                <div class="form-group">
                    <label for="user-username">Usuario *</label>
                    <input type="text" id="user-username" required placeholder="nombre_usuario">
                </div>
                
                <div class="form-group">
                    <label for="user-email">Email *</label>
                    <input type="email" id="user-email" required placeholder="usuario@example.com">
                </div>
                
                <div class="form-group">
                    <label for="user-fullname">Nombre Completo *</label>
                    <input type="text" id="user-fullname" required placeholder="Juan Pérez">
                </div>
                
                <div class="form-group">
                    <label for="user-password">Contraseña *</label>
                    <input type="password" id="user-password" required placeholder="••••••••">
                </div>
                
                <div class="form-group">
                    <label for="user-role-select">Rol *</label>
                    <select id="user-role-select" name="role" required>
                        <option value="">-- Seleccionar rol --</option>
                        <option value="student">Estudiante</option>
                        <option value="teacher">Profesor</option>
                        <option value="admin">Administrador</option>
                    </select>
                </div>
                
                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">
                        <i class="fas fa-save"></i> Crear Usuario
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="loadCreateSection()">
                        Cancelar
                    </button>
                </div>
            </form>
        </div>
    `;
    
    // ✅ Agregar evento después de renderizar el HTML
    const form = document.getElementById('create-user-form');
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        console.log('📝 Form submitted');
        
        const username = document.getElementById('user-username').value;
        const email = document.getElementById('user-email').value;
        const full_name = document.getElementById('user-fullname').value;
        const password = document.getElementById('user-password').value;
        const role = document.getElementById('user-role-select').value;
        
        console.log('📝 Form values:', { username, email, full_name, password, role });
        
        // Validar campos
        if (!username || !email || !full_name || !password) {
            showError('Todos los campos son obligatorios');
            return;
        }
        
        if (!role) {
            showError('Debes seleccionar un rol');
            return;
        }
        
        const userData = {
            username,
            email,
            full_name,
            password,
            role
        };
        
        console.log('📤 Enviando datos:', userData);
        
        try {
            await API.createUser(userData);
            showSuccess('Usuario creado exitosamente');
            loadStudentsSection();
        } catch (error) {
            console.error('❌ Error:', error);
            showError('Error creando usuario: ' + error.message);
        }
    });
}

// Cargar sección de Alumnos
function loadStudentsSection() {
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">
                    <i class="fas fa-users"></i>
                    Gestión de Alumnos
                </h1>
                <p class="page-subtitle">Administrar estudiantes de la plataforma</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="showCreateUserForm()">
                    <i class="fas fa-user-plus"></i>
                    Nuevo Alumno
                </button>
            </div>
        </div>

        <div id="students-container">
            <div class="loading-spinner"></div>
            <p style="text-align: center; color: var(--text-secondary);">Cargando alumnos...</p>
        </div>
    `;
    
    // Cargar lista de alumnos
    loadStudentsList();
}

// Cargar lista de alumnos
async function loadStudentsList() {
    try {
        const users = await API.getAllUsers();
        const students = users.filter(u => u.role === 'student');
        
        const container = document.getElementById('students-container');
        
        if (students.length === 0) {
            container.innerHTML = `
                <div class="no-content">
                    <i class="fas fa-user-graduate"></i>
                    <h4>No hay alumnos registrados</h4>
                    <p>Crea un nuevo alumno para comenzar</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <div class="students-grid">
                ${students.map(student => `
                    <div class="student-card">
                        <div class="student-avatar">
                            <i class="fas fa-user-graduate"></i>
                        </div>
                        <div class="student-info">
                            <h3>${student.full_name || student.username}</h3>
                            <p class="student-email">
                                <i class="fas fa-envelope"></i>
                                ${student.email}
                            </p>
                            <p class="student-username">
                                <i class="fas fa-user"></i>
                                ${student.username}
                            </p>
                            <span class="student-status ${student.is_active ? 'active' : 'inactive'}">
                                <i class="fas fa-circle"></i>
                                ${student.is_active ? 'Activo' : 'Inactivo'}
                            </span>
                        </div>
                        <div class="student-actions">
                            <button class="btn btn-sm btn-secondary" onclick="viewStudentDetails(${student.id})">
                                <i class="fas fa-eye"></i>
                                Ver detalles
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="deleteStudent(${student.id}, '${student.username}')">
                                <i class="fas fa-trash"></i>
                                Eliminar
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error cargando alumnos:', error);
        document.getElementById('students-container').innerHTML = `
            <div class="no-content">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Error cargando alumnos</h4>
                <p>${error.message}</p>
            </div>
        `;
    }
}

// Ver detalles de alumno
async function viewStudentDetails(studentId) {
    try {
        const purchases = await API.getUserPurchases(studentId);
        
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = `
            <div class="page-header">
                <h1 class="page-title">Detalles del Alumno</h1>
                <button class="btn btn-secondary" onclick="loadStudentsSection()">
                    <i class="fas fa-arrow-left"></i> Volver
                </button>
            </div>
            
            <div class="student-details">
                <h3>Materias Compradas (${purchases.length})</h3>
                <div class="purchases-list">
                    ${purchases.length > 0 
                        ? purchases.map(p => `
                            <div class="purchase-item">
                                <i class="fas fa-book"></i>
                                <span>${p.subject?.title || 'Materia desconocida'}</span>
                                <span class="purchase-date">${new Date(p.purchase_date).toLocaleDateString()}</span>
                            </div>
                        `).join('')
                        : '<p>No ha comprado ninguna materia aún</p>'
                    }
                </div>
            </div>
        `;
    } catch (error) {
        showError('Error cargando detalles: ' + error.message);
    }
}

// Eliminar alumno
async function deleteStudent(studentId, username) {
    if (confirm(`⚠️ ¿Estás seguro de eliminar al alumno "${username}"?\n\nEsto NO se puede deshacer.`)) {
        try {
            await API.deleteUser(studentId);
            showSuccess('Alumno eliminado exitosamente');
            loadStudentsSection();
        } catch (error) {
            showError('Error eliminando alumno: ' + error.message);
        }
    }
}

// Cargar sección "Mis Materias"
function loadMySubjectsSection() {
    const contentArea = document.getElementById('content-area');
    
    // Filtrar solo las materias que el usuario compró
    const mySubjectsIds = myPurchases.map(p => p.subject_id);
    const mySubjects = subjects.filter(s => mySubjectsIds.includes(s.id));
    
    contentArea.innerHTML = `
        <div class="page-header">
            <div>
                <h1 class="page-title">
                    <i class="fas fa-graduation-cap"></i>
                    Mis Materias
                </h1>
                <p class="page-subtitle">Cursos en los que estás inscrito</p>
            </div>
        </div>

        ${mySubjects.length === 0 
            ? `<div class="no-content">
                <i class="fas fa-shopping-cart" style="font-size: 64px; color: var(--text-secondary); margin-bottom: 20px;"></i>
                <h3>No tienes materias compradas</h3>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">
                    Explora nuestro catálogo y comienza a aprender
                </p>
                <button class="btn btn-primary" onclick="navigateToSection('subjects')">
                    <i class="fas fa-book"></i>
                    Ver Materias Disponibles
                </button>
               </div>`
            : `<div class="subjects-grid">
                ${mySubjects.map(subject => createMySubjectCard(subject)).join('')}
               </div>`
        }
    `;
}

// Crear card de materia comprada
function createMySubjectCard(subject) {
    const viewed = getSubjectProgress(subject.id);
    const viewedCount = viewed.length;
    // We'll show a basic progress indicator
    return `
        <div class="subject-card purchased">
            <div class="subject-card-header">
                <div class="subject-icon">
                    <i class="fas fa-book-open"></i>
                </div>
                <span class="purchased-badge">
                    <i class="fas fa-check-circle"></i> 
                    Inscrito
                </span>
            </div>
            <div class="subject-card-body">
                <h3 class="subject-title">${subject.title}</h3>
                <p class="subject-description">
                    ${subject.description || 'Sin descripción disponible'}
                </p>
                ${viewedCount > 0 ? `
                <div class="progress-indicator">
                    <i class="fas fa-eye"></i>
                    <span>${viewedCount} contenido${viewedCount !== 1 ? 's' : ''} visto${viewedCount !== 1 ? 's' : ''}</span>
                </div>` : ''}
            </div>
            <div class="subject-card-footer">
                <div class="subject-price">
                    <span class="price-label">Precio pagado:</span>
                    <span class="price-value">$${subject.price}</span>
                </div>
                <div class="subject-actions">
                    <button class="btn btn-primary" onclick="viewSubjectContent(${subject.id})">
                        <i class="fas fa-play-circle"></i>
                        Ver Contenido
                    </button>
                </div>
            </div>
        </div>
    `;
}

// ==========================================
// MODAL MERCADOPAGO (Checkout Simulación)
// ==========================================

function showMPCheckoutModal(subject, preference) {
    const existing = document.getElementById('mp-checkout-modal');
    if (existing) existing.remove();

    const priceFormatted = Number(subject.price).toLocaleString('es-AR', {minimumFractionDigits: 2});
    const price3 = (subject.price / 3).toLocaleString('es-AR', {minimumFractionDigits: 2});
    const price6 = (subject.price / 6).toLocaleString('es-AR', {minimumFractionDigits: 2});
    const price12 = (subject.price / 12).toLocaleString('es-AR', {minimumFractionDigits: 2});

    const modal = document.createElement('div');
    modal.id = 'mp-checkout-modal';
    modal.innerHTML = `
        <div class="mp-overlay" onclick="closeMPModal()"></div>
        <div class="mp-modal">
            <div class="mp-header">
                <div class="mp-logo">
                    <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect width="36" height="36" rx="8" fill="white" fill-opacity="0.15"/>
                        <path d="M9 17.5C9 13 11.5 9.5 15.5 9.5C17.5 9.5 19 10.8 20 12.3C21 10.8 22.5 9.5 24.5 9.5C28.5 9.5 31 13 31 17.5C31 23.5 25 27.5 20 29.5C15 27.5 9 23.5 9 17.5Z" fill="white"/>
                    </svg>
                    <span>Mercado Pago</span>
                </div>
                <button class="mp-close" onclick="closeMPModal()">
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M1 1L13 13M13 1L1 13" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
                </button>
            </div>
            
            <div class="mp-body" id="mp-body">
                <!-- Resumen del producto -->
                <div class="mp-product-info">
                    <div class="mp-product-icon">
                        <i class="fas fa-graduation-cap"></i>
                    </div>
                    <div class="mp-product-details">
                        <h3>${subject.title}</h3>
                        <p>Plataforma Académica UBP</p>
                    </div>
                    <div class="mp-product-price">
                        <div class="mp-price-tag">
                            <span class="mp-currency">$</span><span class="mp-amount">${priceFormatted}</span>
                        </div>
                    </div>
                </div>

                <div class="mp-separator"></div>

                <!-- Sección de pago -->
                <div class="mp-payment-section">
                    <h4 class="mp-section-title">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#009EE3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="4" width="22" height="16" rx="2" ry="2"/><line x1="1" y1="10" x2="23" y2="10"/></svg>
                        Tarjeta de crédito/débito
                    </h4>
                    
                    <div class="mp-form">
                        <div class="mp-field">
                            <label>Número de tarjeta</label>
                            <div class="mp-input-wrapper">
                                <input type="text" id="mp-card-number" value="5031 7557 3453 0604" maxlength="19" placeholder="1234 5678 9012 3456" readonly>
                                <div class="mp-card-brands">
                                    <!-- Visa SVG -->
                                    <svg width="38" height="24" viewBox="0 0 38 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="38" height="24" rx="4" fill="#1A1F71"/>
                                        <path d="M16.2 16.5H13.7L15.3 7.5H17.8L16.2 16.5Z" fill="white"/>
                                        <path d="M24.1 7.7C23.6 7.5 22.8 7.3 21.8 7.3C19.4 7.3 17.7 8.6 17.7 10.3C17.7 11.6 18.8 12.3 19.7 12.7C20.6 13.1 20.9 13.4 20.9 13.8C20.9 14.4 20.2 14.7 19.5 14.7C18.5 14.7 18 14.5 17.2 14.2L16.8 14L16.4 16.3C17 16.5 18 16.7 19.1 16.7C21.7 16.7 23.3 15.4 23.3 13.6C23.3 12.6 22.7 11.8 21.3 11.2C20.5 10.8 20 10.5 20 10.1C20 9.7 20.4 9.3 21.3 9.3C22.1 9.3 22.7 9.5 23.1 9.6L23.4 9.7L24.1 7.7Z" fill="white"/>
                                        <path d="M27.3 7.5H25.4C24.8 7.5 24.3 7.7 24.1 8.3L20.5 16.5H23.1L23.6 15.1H26.8L27.1 16.5H29.4L27.3 7.5ZM24.3 13.2L25.4 10.2L26 13.2H24.3Z" fill="white"/>
                                        <path d="M12.7 7.5L10.3 13.5L10 12C9.5 10.5 8.1 8.8 6.5 8L8.7 16.5H11.3L15.3 7.5H12.7Z" fill="white"/>
                                        <path d="M9.2 7.5H5.1L5 7.7C8 8.4 10 10.3 10.7 12.5L9.9 8.4C9.8 7.7 9.3 7.5 9.2 7.5Z" fill="#F9A51A"/>
                                    </svg>
                                    <!-- Mastercard SVG -->
                                    <svg width="38" height="24" viewBox="0 0 38 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <rect width="38" height="24" rx="4" fill="#252525"/>
                                        <circle cx="15" cy="12" r="7" fill="#EB001B"/>
                                        <circle cx="23" cy="12" r="7" fill="#F79E1B"/>
                                        <path d="M19 6.8C20.6 8.1 21.6 10 21.6 12C21.6 14 20.6 15.9 19 17.2C17.4 15.9 16.4 14 16.4 12C16.4 10 17.4 8.1 19 6.8Z" fill="#FF5F00"/>
                                    </svg>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mp-field-row">
                            <div class="mp-field">
                                <label>Vencimiento</label>
                                <input type="text" id="mp-expiry" value="11/28" maxlength="5" placeholder="MM/AA" readonly>
                            </div>
                            <div class="mp-field">
                                <label>Código de seguridad</label>
                                <div class="mp-input-wrapper mp-cvv-wrapper">
                                    <input type="text" id="mp-cvv" value="123" maxlength="4" placeholder="CVV" readonly>
                                    <div class="mp-cvv-icon">
                                        <svg width="20" height="16" viewBox="0 0 24 18" fill="none" stroke="#b0b8c4" stroke-width="1.5"><rect x="1" y="1" width="22" height="16" rx="2"/><rect x="1" y="4" width="22" height="4" fill="#b0b8c4" stroke="none"/><rect x="14" y="11" width="6" height="3" rx="1" fill="#d1d9e6" stroke="none"/></svg>
                                </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mp-field">
                            <label>Titular de la tarjeta</label>
                            <input type="text" id="mp-cardholder" value="APRO TESTER" placeholder="Nombre como aparece en la tarjeta" readonly>
                        </div>
                        
                        <div class="mp-field">
                            <label>Documento del titular</label>
                            <div class="mp-doc-field">
                                <select class="mp-doc-type" disabled>
                                    <option>DNI</option>
                                </select>
                                <input type="text" id="mp-doc" value="12345678" maxlength="11" placeholder="12345678" readonly>
                            </div>
                        </div>

                        <div class="mp-installments">
                            <label>Cuotas</label>
                            <select id="mp-installments-select">
                                <option value="1">1 cuota de $${priceFormatted} (sin interés)</option>
                                <option value="3">3 cuotas de $${price3}</option>
                                <option value="6">6 cuotas de $${price6}</option>
                                <option value="12">12 cuotas de $${price12}</option>
                            </select>
                        </div>
                    </div>
                </div>
                
                <div class="mp-test-notice">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#856404" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
                    <span><strong>Modo Sandbox</strong> — Datos de prueba precargados. No se realiza cobro real.</span>
                </div>
                
                <button class="mp-pay-btn" id="mp-pay-btn" onclick="processMPPayment(${subject.id}, '${preference.id}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
                    Pagar $${priceFormatted}
                </button>
                
                <div class="mp-security">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="#28a745" stroke="none"><path d="M12 2L3 7v5c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-9-5zm-1 15l-4-4 1.41-1.41L11 14.17l6.59-6.59L19 9l-8 8z"/></svg>
                    <span>Pago seguro con encriptación SSL de 256-bit</span>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    requestAnimationFrame(() => modal.classList.add('mp-visible'));
}

async function processMPPayment(subjectId, preferenceId) {
    const payBtn = document.getElementById('mp-pay-btn');
    const mpBody = document.getElementById('mp-body');
    
    payBtn.disabled = true;
    payBtn.innerHTML = '<div class="mp-spinner"></div> Procesando pago...';
    payBtn.classList.add('mp-processing');
    
    // Simular proceso de pago (2.5 segundos)
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    const subject = subjects.find(s => s.id === subjectId);
    const priceFormatted = subject ? Number(subject.price).toLocaleString('es-AR', {minimumFractionDigits: 2}) : '0.00';
    
    mpBody.innerHTML = `
        <div class="mp-result">
            <div class="mp-result-icon mp-approved">
                <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="#28a745" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            </div>
            <h2>¡Pago aprobado!</h2>
            <p style="color:#8c94a0; margin:4px 0 0; font-size:14px;">Tu compra fue procesada correctamente</p>
            <p class="mp-result-amount">$${priceFormatted}</p>
            <div class="mp-result-details">
                <div class="mp-result-row">
                    <span>Estado</span>
                    <span class="mp-status-approved">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="#28a745" stroke="none" style="vertical-align:-1px;margin-right:4px"><circle cx="12" cy="12" r="12"/><path d="M10 15.17l-3.59-3.58L5 13l5 5 9-9-1.41-1.42z" fill="white"/></svg>
                        Aprobado
                    </span>
                </div>
                <div class="mp-result-row">
                    <span>Operación</span>
                    <span style="font-family:monospace; font-size:12px;">#${preferenceId.slice(0, 12).toUpperCase()}</span>
                </div>
                <div class="mp-result-row">
                    <span>Medio de pago</span>
                    <span>
                        <svg width="24" height="15" viewBox="0 0 38 24" fill="none" style="vertical-align:-3px;margin-right:4px"><rect width="38" height="24" rx="4" fill="#252525"/><circle cx="15" cy="12" r="6" fill="#EB001B"/><circle cx="23" cy="12" r="6" fill="#F79E1B"/><path d="M19 7.5C20.3 8.6 21.1 10.2 21.1 12C21.1 13.8 20.3 15.4 19 16.5C17.7 15.4 16.9 13.8 16.9 12C16.9 10.2 17.7 8.6 19 7.5Z" fill="#FF5F00"/></svg>
                        Mastercard ****0604
                    </span>
                </div>
                <div class="mp-result-row">
                    <span>Materia</span>
                    <span>${subject ? subject.title : ''}</span>
                </div>
            </div>
            <button class="mp-pay-btn mp-success-btn" onclick="completeMPPurchase(${subjectId}, '${preferenceId}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Continuar al campus
            </button>
        </div>
    `;
}

async function completeMPPurchase(subjectId, preferenceId) {
    try {
        const result = await API.confirmMPPayment(subjectId, preferenceId, 'approved');
        console.log('✅ Compra confirmada:', result);
        
        closeMPModal();
        
        const subject = subjects.find(s => s.id === subjectId);
        showSuccess(`¡Compra exitosa! Ahora tienes acceso a "${subject ? subject.title : 'la materia'}"`);
        
        myPurchases = await API.getMyPurchases();
        
        if (currentSection === 'subjects') loadSubjectsSection();
        else if (currentSection === 'my-subjects') loadMySubjectsSection();
        else loadDashboardSection();
        
    } catch (error) {
        console.error('Error confirmando compra:', error);
        closeMPModal();
        showError('Error registrando la compra: ' + error.message);
    }
}

function closeMPModal() {
    const modal = document.getElementById('mp-checkout-modal');
    if (modal) {
        modal.classList.remove('mp-visible');
        setTimeout(() => modal.remove(), 300);
    }
}