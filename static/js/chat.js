// Global variables
let socket;
let currentContentType = null;
let generatedFiles = null;
let contentTypes = [];
let formats = {};
let styles = [];
let colorPalettes = [];
let chatActive = false;
let currentUserId = null;
let premiumTemplates = []; // NUEVO: Plantillas premium cargadas

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    loadInitialData();
    showWelcome();
    
    // NUEVO: Cargar plantillas premium y configurar detección de cambios
    loadPremiumTemplates();
    setTimeout(setupFormChangeDetection, 1000);
});

// Socket.IO initialization
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Conectado al servidor');
        showSmartNotification('Conectado al servidor premium', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado del servidor');
        showSmartNotification('Desconectado del servidor', 'error');
    });
    
    socket.on('generation_status', function(data) {
        updateGenerationStatus(data.message, data.status);
        
        // Update estimated time if provided
        if (data.estimated_time) {
            const estimatedTimeElement = document.getElementById('estimated-time');
            if (estimatedTimeElement) {
                estimatedTimeElement.textContent = data.estimated_time;
            }
        }
    });
    
    socket.on('generation_complete', function(data) {
        // Complete all steps
        for (let i = 1; i <= 4; i++) {
            const step = document.getElementById(`step-${i}`);
            if (step) {
                step.className = 'step-indicator step-completed w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold';
                step.innerHTML = '<i class="fas fa-check"></i>';
            }
        }
        
        // Update progress to 100%
        const progressBar = document.getElementById('progress-bar');
        const progressPercentage = document.getElementById('progress-percentage');
        if (progressBar) progressBar.style.width = '100%';
        if (progressPercentage) progressPercentage.textContent = '100%';
        
        // Wait a moment to show completion, then hide status
        setTimeout(() => {
            hideGenerationStatus();
        }, 1500);
        
        if (data.success) {
            generatedFiles = {
                html: data.html_file,
                image: data.image_file
            };
            showResults(data);
            
            // MEJORADO: Notificación según tipo de generación
            const notificationType = data.type === 'premium' ? 'premium' : 'success';
            const message = data.type === 'premium' ? 
                '🎉 ¡Contenido premium generado exitosamente!' : 
                '✅ ¡Contenido generado exitosamente!';
            showSmartNotification(message, notificationType);
        } else {
            showSmartNotification(`Error: ${data.error}`, 'error');
        }
    });
    
    // ================================
    // EVENTOS PARA CHAT INTELIGENTE
    // ================================
    
    socket.on('chat_response', function(data) {
        console.log('Chat response received:', data);
        
        hideTypingIndicator();
        
        if (data.success) {
            if (data.is_bot) {
                addBotMessage(data.message, data.options, data.examples);
                
                if (data.completed) {
                    // Chat completado
                    showChatCompleted();
                }
            }
        } else {
            addBotMessage(data.message || 'Hubo un error en la conversación.', ['Reiniciar chat']);
            showSmartNotification(`Error en chat: ${data.error}`, 'error');
        }
    });
    
    socket.on('chat_reset', function(data) {
        if (data.success) {
            resetChatInterface();
            showSmartNotification('Chat reiniciado', 'info');
        }
    });
    
    socket.on('chat_generation_started', function(data) {
        addBotMessage(data.message);
        showGenerationStatus('🚀 Generando contenido personalizado...');
    });
}

// Load initial data from API
async function loadInitialData() {
    try {
        // Load content types
        const contentTypesResponse = await fetch('/api/content-types');
        contentTypes = await contentTypesResponse.json();
        
        // Load formats
        const formatsResponse = await fetch('/api/formats');
        formats = await formatsResponse.json();
        
        // Load styles - MEJORADO: Ahora carga estilos profesionales
        const stylesResponse = await fetch('/api/styles');
        styles = await stylesResponse.json();
        
        // Load color palettes - MEJORADO: Ahora carga paletas profesionales
        const palettesResponse = await fetch('/api/color-palettes');
        colorPalettes = await palettesResponse.json();
        
        console.log('📊 Datos iniciales cargados:', {
            contentTypes: contentTypes.length,
            formats: Object.keys(formats).length,
            styles: styles.length,
            colorPalettes: colorPalettes.length
        });
        
        showSmartNotification(`🎨 Sistema premium cargado: ${styles.length} estilos y ${colorPalettes.length} paletas`, 'premium');
    } catch (error) {
        console.error('Error cargando datos iniciales:', error);
        showSmartNotification('Error cargando configuración', 'error');
    }
}

// NUEVA FUNCIÓN: Cargar plantillas premium disponibles
async function loadPremiumTemplates() {
    try {
        const response = await fetch('/api/templates/premium');
        const result = await response.json();
        
        if (result.success) {
            premiumTemplates = result.templates;
            console.log(`✅ ${result.count} plantillas premium cargadas`);
            showSmartNotification(`👑 ${result.count} plantillas premium disponibles`, 'premium', 3000);
            return result.templates;
        }
    } catch (error) {
        console.error('Error loading premium templates:', error);
    }
    return [];
}

// NUEVA FUNCIÓN: Obtener recomendaciones inteligentes
async function getIntelligentRecommendations(params) {
    try {
        const response = await fetch('/api/intelligent-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });
        
        const result = await response.json();
        
        if (result.success && result.recommendations.confidence > 0.5) {
            // Aplicar recomendaciones automáticamente
            applyRecommendations(result.recommendations);
            const confidencePercent = Math.round(result.recommendations.confidence * 100);
            showSmartNotification(`🎨 Recomendaciones aplicadas automáticamente (${confidencePercent}% confianza)`, 'premium');
        }
    } catch (error) {
        console.error('Error getting recommendations:', error);
    }
}

// NUEVA FUNCIÓN: Aplicar recomendaciones automáticamente
function applyRecommendations(recommendations) {
    // Auto-seleccionar paleta recomendada
    if (recommendations.color_palette) {
        const colorSelect = document.querySelector('select[name="colores"]');
        if (colorSelect) {
            // Buscar la opción que coincida
            for (let option of colorSelect.options) {
                if (option.value === recommendations.color_palette || option.text.includes(recommendations.color_palette)) {
                    colorSelect.value = option.value;
                    // Agregar efecto visual de selección
                    colorSelect.classList.add('ring-2', 'ring-purple-400');
                    setTimeout(() => {
                        colorSelect.classList.remove('ring-2', 'ring-purple-400');
                    }, 2000);
                    break;
                }
            }
        }
    }
    
    // Auto-seleccionar estilo recomendado
    if (recommendations.design_style) {
        const styleSelect = document.querySelector('select[name="estilo"]');
        if (styleSelect) {
            // Buscar la opción que coincida
            for (let option of styleSelect.options) {
                if (option.value === recommendations.design_style || option.text.includes(recommendations.design_style)) {
                    styleSelect.value = option.value;
                    // Agregar efecto visual de selección
                    styleSelect.classList.add('ring-2', 'ring-blue-400');
                    setTimeout(() => {
                        styleSelect.classList.remove('ring-2', 'ring-blue-400');
                    }, 2000);
                    break;
                }
            }
        }
    }
}

// NUEVA FUNCIÓN: Preview en tiempo real
async function generateLivePreview() {
    const formData = new FormData(document.getElementById('generation-form'));
    const params = Object.fromEntries(formData.entries());
    params.content_type = currentContentType;

    try {
        showSmartNotification('🔍 Generando preview...', 'info', 2000);
        
        const response = await fetch('/api/design-preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(params)
        });

        const result = await response.json();
        
        if (result.success) {
            showPreviewModal(result.html_preview);
        } else {
            showSmartNotification('Error generando preview', 'error');
        }
    } catch (error) {
        console.error('Error generating preview:', error);
        showSmartNotification('Error en preview', 'error');
    }
}

// NUEVA FUNCIÓN: Mostrar modal de preview
function showPreviewModal(htmlContent) {
    // Crear modal de preview
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm';
    modal.innerHTML = `
        <div class="bg-gray-800 rounded-xl p-6 max-w-5xl w-full mx-4 border border-gray-600 shadow-2xl">
            <div class="flex justify-between items-center mb-6">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-purple-600 rounded-full flex items-center justify-center">
                        <i class="fas fa-eye text-white"></i>
                    </div>
                    <div>
                        <h3 class="text-xl font-bold text-white">📱 Preview del Diseño</h3>
                        <p class="text-gray-400 text-sm">Vista previa de tu contenido</p>
                    </div>
                </div>
                <button onclick="closePreviewModal()" class="text-gray-400 hover:text-white transition-colors p-2">
                    <i class="fas fa-times text-xl"></i>
                </button>
            </div>
            
            <div class="bg-white rounded-lg overflow-hidden shadow-inner mb-6">
                <iframe srcdoc="${htmlContent.replace(/"/g, '&quot;')}" 
                        class="w-full h-96 border-0"></iframe>
            </div>
            
            <div class="flex justify-center space-x-4">
                <button onclick="closePreviewModal()" 
                        class="bg-gray-600 hover:bg-gray-700 text-white px-6 py-3 rounded-lg transition-colors font-medium">
                    <i class="fas fa-times mr-2"></i>Cerrar Preview
                </button>
                <button onclick="generateContent(); closePreviewModal();" 
                        class="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white px-6 py-3 rounded-lg transition-all font-medium shadow-lg">
                    <i class="fas fa-magic mr-2"></i>¡Generar Versión Final!
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    window.currentPreviewModal = modal;
}

// NUEVA FUNCIÓN: Cerrar modal de preview
function closePreviewModal() {
    if (window.currentPreviewModal) {
        document.body.removeChild(window.currentPreviewModal);
        window.currentPreviewModal = null;
    }
}

// NUEVA FUNCIÓN: Configurar detección de cambios en formulario
function setupFormChangeDetection() {
    const form = document.getElementById('generation-form');
    if (form) {
        const temaInput = form.querySelector('input[name="tema"]');
        if (temaInput) {
            temaInput.addEventListener('input', debounce(() => {
                if (currentContentType && temaInput.value.length > 3) {
                    getIntelligentRecommendations({
                        content_type: currentContentType,
                        tema: temaInput.value,
                        formato: form.querySelector('select[name="formato"]')?.value || 'instagram_square'
                    });
                }
            }, 1000));
        }
    }
}

// NUEVA FUNCIÓN: Utility function para debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Navigation functions
function showWelcome() {
    hideAllSections();
    document.getElementById('welcome-section').classList.remove('hidden');
    updateActiveNavButton('welcome');
}

function showIntelligentChat() {
    hideAllSections();
    document.getElementById('chat-section').classList.remove('hidden');
    updateActiveNavButton('chat');
}

function showContentTypes() {
    hideAllSections();
    document.getElementById('generate-section').classList.remove('hidden');
    updateActiveNavButton('generate');
    loadContentTypesGrid();
}

function showHistory() {
    hideAllSections();
    document.getElementById('history-section').classList.remove('hidden');
    updateActiveNavButton('history');
}

function showSettings() {
    hideAllSections();
    document.getElementById('settings-section').classList.remove('hidden');
    updateActiveNavButton('settings');
}

function hideAllSections() {
    const sections = ['welcome-section', 'chat-section', 'generate-section', 'history-section', 'settings-section'];
    sections.forEach(section => {
        const element = document.getElementById(section);
        if (element) {
            element.classList.add('hidden');
        }
    });
}

function updateActiveNavButton(activeSection) {
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('bg-gray-700');
    });
    
    // Add active class to current button
    const activeBtn = document.querySelector(`[data-section="${activeSection}"]`);
    if (activeBtn) {
        activeBtn.classList.add('bg-gray-700');
    }
}

// Content generation functions
function startQuickGeneration() {
    showContentTypes();
}

function startIntelligentChat() {
    showIntelligentChat();
}

function loadContentTypesGrid() {
    const grid = document.getElementById('content-types-grid');
    grid.innerHTML = '';
    
    contentTypes.forEach(type => {
        const card = document.createElement('div');
        card.className = 'bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors cursor-pointer hover:scale-105 transform duration-200';
        card.onclick = () => selectContentType(type.id);
        
        card.innerHTML = `
            <div class="text-center">
                <div class="text-3xl mb-4">${type.emoji}</div>
                <h3 class="font-medium text-white mb-2">${type.name}</h3>
                <p class="text-gray-400 text-sm">Crear ${type.name.toLowerCase()}</p>
            </div>
        `;
        
        grid.appendChild(card);
    });
}

// MODIFICADO: selectContentType con recomendaciones automáticas
function selectContentType(typeId) {
    currentContentType = typeId;
    const typeInfo = contentTypes.find(t => t.id === typeId);
    
    document.getElementById('content-types-grid').classList.add('hidden');
    document.getElementById('content-form').classList.remove('hidden');
    
    generateFormFields(typeId, typeInfo);
    
    // NUEVO: Obtener recomendaciones automáticas después de un breve delay
    setTimeout(() => {
        const tema = document.querySelector('input[name="tema"]')?.value || '';
        if (tema.length > 0) {
            getIntelligentRecommendations({
                content_type: typeId,
                tema: tema,
                formato: 'instagram_square' // default
            });
        }
        
        // Configurar detección de cambios para este formulario específico
        setupFormChangeDetection();
    }, 500);
}

function backToContentTypes() {
    document.getElementById('content-form').classList.add('hidden');
    document.getElementById('content-types-grid').classList.remove('hidden');
    currentContentType = null;
}

// MODIFICADO: generateFormFields con botón de preview
function generateFormFields(typeId, typeInfo) {
    const formFields = document.getElementById('form-fields');
    formFields.innerHTML = '';
    
    // Title
    const titleDiv = document.createElement('div');
    titleDiv.innerHTML = `
        <h3 class="text-xl font-bold mb-6 flex items-center">
            ${typeInfo.emoji} Configurando: ${typeInfo.name}
            <span class="ml-3 bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">PREMIUM</span>
        </h3>
    `;
    formFields.appendChild(titleDiv);
    
    // Theme/Topic
    const themeField = createInputField('tema', 'text', '🎯 Tema/Nicho', 'ej: programación, marketing, diseño', true);
    formFields.appendChild(themeField);
    
    // Content-specific fields
    const specificFields = getContentSpecificFields(typeId);
    specificFields.forEach(field => formFields.appendChild(field));
    
    // Visual style - MEJORADO: Muestra información adicional
    const styleField = createSelectFieldEnhanced('estilo', '🎨 Estilo Visual', styles, 'description');
    formFields.appendChild(styleField);
    
    // Color palette - MEJORADO: Muestra información adicional
    const colorField = createSelectFieldEnhanced('colores', '🌈 Paleta de Colores', colorPalettes, 'description');
    formFields.appendChild(colorField);
    
    // Social format
    const formatOptions = Object.entries(formats).map(([key, value]) => 
        `${value.name} (${value.width}x${value.height}px)`
    );
    const formatField = createSelectField('formato', '📱 Formato de Red Social', formatOptions, Object.keys(formats));
    formFields.appendChild(formatField);
    
    // Filename
    const filenameField = createInputField('nombre_archivo', 'text', '💾 Nombre del archivo', 'sin extensión');
    formFields.appendChild(filenameField);
    
    // NUEVO: Botones mejorados con preview
    const buttonsDiv = document.createElement('div');
    buttonsDiv.className = 'flex flex-wrap gap-4';
    buttonsDiv.innerHTML = `
        <button type="submit" class="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-medium py-3 px-6 rounded-lg transition-all shadow-lg">
            <i class="fas fa-magic mr-2"></i>
            Generar Contenido Premium
        </button>
        <button type="button" onclick="generateLivePreview()" class="bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-6 rounded-lg transition-colors">
            <i class="fas fa-eye mr-2"></i>
            Preview Rápido
        </button>
        <button type="button" onclick="generateRandomIdea()" class="bg-yellow-600 hover:bg-yellow-700 text-white font-medium py-3 px-6 rounded-lg transition-colors">
            <i class="fas fa-dice mr-2"></i>
            Idea Aleatoria
        </button>
    `;
    
    formFields.appendChild(buttonsDiv);
}

function getContentSpecificFields(typeId) {
    const fields = [];
    
    switch (typeId) {
        case 'tip':
            fields.push(createInputField('titulo', 'text', '💡 Título del tip', '', true));
            fields.push(createTextareaField('descripcion', '📝 Describe el tip que quieres compartir', '', true));
            break;
            
        case 'quote':
            fields.push(createInputField('frase', 'text', '✨ Frase inspiracional', '', true));
            fields.push(createInputField('autor', 'text', '👤 Autor (opcional)', ''));
            break;
            
        case 'estadistica':
            fields.push(createInputField('numero', 'text', '📊 Número/Porcentaje', 'ej: 85%', true));
            fields.push(createTextareaField('descripcion', '📝 ¿Qué representa ese número?', '', true));
            break;
            
        case 'lista':
            fields.push(createInputField('titulo', 'text', '📋 Título de la lista', '', true));
            fields.push(createTextareaField('descripcion', '📝 Describe qué tipo de lista', '', true));
            break;
            
        case 'hecho':
            fields.push(createInputField('titulo', 'text', '🔥 Título del hecho', '¿Sabías que...?'));
            fields.push(createTextareaField('descripcion', '📝 El hecho curioso', '', true));
            break;
            
        case 'tutorial':
            fields.push(createInputField('titulo', 'text', '📚 Título del tutorial', 'Cómo hacer...', true));
            fields.push(createInputField('pasos', 'number', '📝 Número de pasos', '3-5', true, {min: 3, max: 10}));
            break;
            
        case 'concepto':
            fields.push(createInputField('concepto', 'text', '🧠 Concepto a explicar', 'ej: Red Neuronal, SOLID', true));
            fields.push(createTextareaField('descripcion', '📝 Breve descripción del concepto', '', true));
            
            const nivelField = createSelectField('nivel', '📚 Nivel de Explicación', 
                ['Básico (principiantes)', 'Intermedio (con algo de experiencia)', 'Avanzado (profesionales)'],
                ['basico', 'intermedio', 'avanzado']
            );
            fields.push(nivelField);
            
            const ejemploField = createCheckboxField('incluir_ejemplo', '¿Incluir ejemplo práctico?');
            fields.push(ejemploField);
            break;
    }
    
    return fields;
}

// Form field creation helpers
function createInputField(name, type, label, placeholder = '', required = false, attributes = {}) {
    const div = document.createElement('div');
    const req = required ? '<span class="text-red-400">*</span>' : '';
    
    let attrStr = '';
    Object.entries(attributes).forEach(([key, value]) => {
        attrStr += ` ${key}="${value}"`;
    });
    
    div.innerHTML = `
        <label class="block text-sm font-medium text-gray-300 mb-2">
            ${label} ${req}
        </label>
        <input type="${type}" name="${name}" placeholder="${placeholder}" 
               class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent text-white placeholder-gray-400 transition-all"
               ${required ? 'required' : ''} ${attrStr}>
    `;
    
    return div;
}

function createTextareaField(name, label, placeholder = '', required = false) {
    const div = document.createElement('div');
    const req = required ? '<span class="text-red-400">*</span>' : '';
    
    div.innerHTML = `
        <label class="block text-sm font-medium text-gray-300 mb-2">
            ${label} ${req}
        </label>
        <textarea name="${name}" placeholder="${placeholder}" rows="3"
                  class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent text-white placeholder-gray-400 transition-all"
                  ${required ? 'required' : ''}></textarea>
    `;
    
    return div;
}

function createSelectField(name, label, options, values = null) {
    const div = document.createElement('div');
    
    let optionsHtml = '';
    options.forEach((option, index) => {
        const value = values ? values[index] : option;
        optionsHtml += `<option value="${value}">${option}</option>`;
    });
    
    div.innerHTML = `
        <label class="block text-sm font-medium text-gray-300 mb-2">${label}</label>
        <select name="${name}" class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent text-white transition-all">
            ${optionsHtml}
        </select>
    `;
    
    return div;
}

// NUEVA FUNCIÓN: Select field mejorado con descripciones
function createSelectFieldEnhanced(name, label, options, descriptionKey) {
    const div = document.createElement('div');
    
    let optionsHtml = '';
    options.forEach((option) => {
        const displayName = option.name || option;
        const description = option[descriptionKey] || '';
        const value = option.id || option.name || option;
        
        const optionText = description ? `${displayName} - ${description}` : displayName;
        optionsHtml += `<option value="${value}" title="${description}">${optionText}</option>`;
    });
    
    div.innerHTML = `
        <label class="block text-sm font-medium text-gray-300 mb-2">
            ${label}
            <span class="text-purple-400 text-xs ml-2">✨ Premium</span>
        </label>
        <select name="${name}" class="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-400 focus:border-transparent text-white transition-all">
            ${optionsHtml}
        </select>
    `;
    
    return div;
}

function createCheckboxField(name, label) {
    const div = document.createElement('div');
    
    div.innerHTML = `
        <label class="flex items-center space-x-3 cursor-pointer">
            <input type="checkbox" name="${name}" class="w-5 h-5 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-400">
            <span class="text-sm font-medium text-gray-300">${label}</span>
        </label>
    `;
    
    return div;
}

// Form submission
document.addEventListener('submit', function(e) {
    if (e.target.id === 'generation-form') {
        e.preventDefault();
        generateContent();
    }
});

function generateContent() {
    const formData = new FormData(document.getElementById('generation-form'));
    const params = Object.fromEntries(formData.entries());
    
    // Add content type
    params.content_type = currentContentType;
    
    // Convert checkbox to boolean
    if (params.incluir_ejemplo !== undefined) {
        params.incluir_ejemplo = formData.has('incluir_ejemplo');
    }
    
    // Show generation status
    showGenerationStatus('🚀 Iniciando generación premium...');
    
    // Send to server via Socket.IO
    socket.emit('generate_content', params);
}

// Generation status functions
function showGenerationStatus(message) {
    const statusDiv = document.getElementById('generation-status');
    const messageSpan = document.getElementById('status-message');
    
    messageSpan.textContent = message;
    statusDiv.classList.remove('hidden');
    
    // Reset progress bar and steps
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('progress-percentage').textContent = '0%';
    resetSteps();
}

function updateGenerationStatus(message, status) {
    const messageSpan = document.getElementById('status-message');
    const progressBar = document.getElementById('progress-bar');
    const progressPercentage = document.getElementById('progress-percentage');
    
    messageSpan.textContent = message;
    
    // Update progress and steps based on status
    const statusConfig = {
        'started': { progress: 10, step: 1 },
        'loading_templates': { progress: 20, step: 1 },
        'creating_prompts': { progress: 30, step: 1 },
        'calling_deepseek': { progress: 40, step: 2 },
        'generating': { progress: 60, step: 2 },
        'processing': { progress: 80, step: 3 },
        'converting': { progress: 90, step: 4 },
        'fallback': { progress: 70, step: 3 }
    };
    
    const config = statusConfig[status] || { progress: 50, step: 2 };
    
    progressBar.style.width = `${config.progress}%`;
    progressPercentage.textContent = `${config.progress}%`;
    
    updateStepIndicators(config.step);
}

function resetSteps() {
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step-${i}`);
        step.className = 'step-indicator step-pending w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold';
    }
}

function updateStepIndicators(currentStep) {
    for (let i = 1; i <= 4; i++) {
        const step = document.getElementById(`step-${i}`);
        
        if (i < currentStep) {
            step.className = 'step-indicator step-completed w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold';
            step.innerHTML = '<i class="fas fa-check"></i>';
        } else if (i === currentStep) {
            step.className = 'step-indicator step-active w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold';
            step.innerHTML = '<div class="generation-spinner w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>';
        } else {
            step.className = 'step-indicator step-pending w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold';
            step.textContent = i;
        }
    }
}

function hideGenerationStatus() {
    document.getElementById('generation-status').classList.add('hidden');
}

// Results modal functions
function showResults(data) {
    const modal = document.getElementById('results-modal');
    
    // Set timestamp
    const timestamp = new Date().toLocaleString('es-ES');
    document.getElementById('generation-timestamp').textContent = timestamp;
    
    // Update file details
    const fileDetails = document.getElementById('file-details');
    const typeText = data.type === 'premium' ? 'Generado con IA Premium' : 'Generado con plantilla';
    const typeColor = data.type === 'premium' ? 'text-purple-400' : 'text-yellow-400';
    const typeIcon = data.type === 'premium' ? 'fas fa-crown' : 'fas fa-template';
    
    fileDetails.innerHTML = `
        <div class="flex items-center justify-between">
            <span class="text-gray-300">Tipo de generación:</span>
            <span class="${typeColor} font-medium flex items-center">
                <i class="${typeIcon} mr-1"></i>
                ${typeText}
            </span>
        </div>
        <div class="flex items-center justify-between">
            <span class="text-gray-300">Archivo HTML:</span>
            <span class="text-green-400 font-mono text-sm">${data.html_file}</span>
        </div>
        <div class="flex items-center justify-between">
            <span class="text-gray-300">Archivo imagen:</span>
            <span class="text-green-400 font-mono text-sm">${data.image_file}</span>
        </div>
        <div class="flex items-center justify-between">
            <span class="text-gray-300">Estado:</span>
            <span class="text-green-400 font-medium flex items-center">
                <i class="fas fa-check-circle mr-1"></i>
                Completado
            </span>
        </div>
    `;
    
    // Load image preview
    loadImagePreview(data.image_file);
    
    // Show modal
    modal.classList.remove('hidden');
}

function loadImagePreview(imagePath) {
    const container = document.getElementById('image-preview-container');
    
    // Create image element
    const img = document.createElement('img');
    img.className = 'image-preview mx-auto';
    img.alt = 'Contenido generado';
    
    // Handle loading states
    img.onload = function() {
        container.innerHTML = '';
        container.appendChild(img);
        
        // Add download hint
        const hint = document.createElement('p');
        hint.className = 'text-gray-400 text-sm mt-3';
        hint.innerHTML = '<i class="fas fa-info-circle mr-1"></i>Haz clic en "Imagen" para descargar';
        container.appendChild(hint);
    };
    
    img.onerror = function() {
        container.innerHTML = `
            <div class="text-red-400 p-4">
                <i class="fas fa-exclamation-triangle text-2xl mb-2"></i>
                <p>Error cargando preview</p>
                <p class="text-sm text-gray-400">La imagen se generó correctamente</p>
            </div>
        `;
    };
    
    // Set image source (this will trigger the load)
    img.src = `/download/${imagePath}`;
}

function closeResultsModal() {
    document.getElementById('results-modal').classList.add('hidden');
}

function downloadHTML() {
    if (generatedFiles && generatedFiles.html) {
        window.open(`/download/${generatedFiles.html}`, '_blank');
        showSmartNotification('Descargando archivo HTML...', 'info');
    }
}

function downloadImage() {
    if (generatedFiles && generatedFiles.image) {
        window.open(`/download/${generatedFiles.image}`, '_blank');
        showSmartNotification('Descargando imagen...', 'info');
    }
}

// New modal functions
function shareOnSocial() {
    if (generatedFiles && generatedFiles.image) {
        // Create a simple share dialog
        const shareUrl = window.location.origin + `/download/${generatedFiles.image}`;
        
        if (navigator.share) {
            navigator.share({
                title: 'Contenido generado con DeepPublisher',
                text: 'Mira este contenido que creé con IA',
                url: shareUrl
            }).catch(err => {
                console.log('Error sharing:', err);
                fallbackShare(shareUrl);
            });
        } else {
            fallbackShare(shareUrl);
        }
    }
}

function fallbackShare(url) {
    // Copy to clipboard as fallback
    navigator.clipboard.writeText(url).then(() => {
        showSmartNotification('URL copiada al portapapeles', 'success');
    }).catch(() => {
        showSmartNotification('No se pudo compartir automáticamente', 'warning');
    });
}

function generateVariation() {
    showSmartNotification('Función de variaciones próximamente...', 'tip');
    // TODO: Implement variation generation
}

function createNew() {
    closeResultsModal();
    showContentTypes();
    showSmartNotification('¿Listo para crear otro post increíble?', 'info');
}

// Random idea generation
async function generateRandomIdea() {
    try {
        showSmartNotification('Generando idea aleatoria...', 'info');
        
        const response = await fetch('/api/random-ideas');
        const ideas = await response.json();
        
        if (ideas.length > 0) {
            const randomIdea = ideas[Math.floor(Math.random() * ideas.length)];
            showIdeaModal(randomIdea);
        } else {
            showSmartNotification('No se pudieron cargar ideas', 'error');
        }
    } catch (error) {
        console.error('Error generating random idea:', error);
        showSmartNotification('Error generando idea aleatoria', 'error');
    }
}

function showIdeaModal(idea) {
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
    modal.innerHTML = `
        <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 border border-gray-700">
            <div class="text-center">
                <h3 class="text-xl font-bold mb-4">💡 Idea Generada</h3>
                <div class="bg-gray-700 rounded-lg p-4 mb-6 text-left">
                    <div class="mb-3">
                        <span class="text-blue-400 font-medium">Tipo:</span>
                        <span class="ml-2">${idea.tipo}</span>
                    </div>
                    <div class="mb-3">
                        <span class="text-green-400 font-medium">Tema:</span>
                        <span class="ml-2">${idea.tema}</span>
                    </div>
                    <div class="mb-3">
                        <span class="text-purple-400 font-medium">Título:</span>
                        <span class="ml-2">${idea.titulo}</span>
                    </div>
                    <div>
                        <span class="text-yellow-400 font-medium">Por qué funciona:</span>
                        <span class="ml-2 text-gray-300">${idea.razon}</span>
                    </div>
                </div>
                <div class="flex space-x-4">
                    <button onclick="useIdea('${idea.content_type}', '${idea.tema}', '${idea.titulo}')" 
                            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                        Usar Esta Idea
                    </button>
                    <button onclick="closeIdeaModal()" 
                            class="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.onclick = function(e) {
        if (e.target === modal) {
            closeIdeaModal();
        }
    };
    
    document.body.appendChild(modal);
    window.currentIdeaModal = modal;
}

function useIdea(contentType, tema, titulo) {
    closeIdeaModal();
    
    // Navigate to content generation
    selectContentType(contentType);
    
    // Pre-fill form fields
    setTimeout(() => {
        const temaField = document.querySelector('input[name="tema"]');
        if (temaField) temaField.value = tema;
        
        const tituloField = document.querySelector('input[name="titulo"]');
        if (tituloField) tituloField.value = titulo;
        
        showSmartNotification('Idea aplicada al formulario', 'success');
    }, 100);
}

function closeIdeaModal() {
    if (window.currentIdeaModal) {
        document.body.removeChild(window.currentIdeaModal);
        window.currentIdeaModal = null;
    }
}

// Settings functions
async function testDeepSeek() {
    const statusDiv = document.getElementById('deepseek-status');
    statusDiv.innerHTML = '<div class="text-yellow-400">🔍 Probando conexión...</div>';
    
    try {
        const response = await fetch('/api/test-deepseek', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            statusDiv.innerHTML = `
                <div class="text-green-400">✅ ${result.message}</div>
                <div class="text-gray-400 mt-1">Respuesta: ${result.response}</div>
            `;
            showSmartNotification('Conexión DeepSeek exitosa', 'success');
        } else {
            statusDiv.innerHTML = `
                <div class="text-red-400">❌ ${result.message}</div>
                <div class="text-gray-400 mt-1">Error: ${result.error}</div>
            `;
            showSmartNotification('Error en conexión DeepSeek', 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="text-red-400">❌ Error de conexión: ${error.message}</div>`;
        showSmartNotification('Error probando DeepSeek', 'error');
    }
}

// MEJORADO: Sistema de notificaciones inteligente
function showSmartNotification(message, type = 'info', duration = 5000) {
    const notification = document.getElementById('notification');
    const icon = document.getElementById('notification-icon');
    const messageSpan = document.getElementById('notification-message');
    
    // Configuración mejorada
    const config = {
        success: { 
            icon: 'fa-check-circle', 
            bgColor: 'bg-green-600', 
            textColor: 'text-white',
            emoji: '✅'
        },
        error: { 
            icon: 'fa-exclamation-circle', 
            bgColor: 'bg-red-600', 
            textColor: 'text-white',
            emoji: '❌'
        },
        info: { 
            icon: 'fa-info-circle', 
            bgColor: 'bg-blue-600', 
            textColor: 'text-white',
            emoji: 'ℹ️'
        },
        warning: { 
            icon: 'fa-exclamation-triangle', 
            bgColor: 'bg-yellow-600', 
            textColor: 'text-white',
            emoji: '⚠️'
        },
        tip: { 
            icon: 'fa-lightbulb', 
            bgColor: 'bg-yellow-600', 
            textColor: 'text-white',
            emoji: '💡'
        },
        premium: { 
            icon: 'fa-crown', 
            bgColor: 'bg-gradient-to-r from-purple-600 to-pink-600', 
            textColor: 'text-white',
            emoji: '👑'
        }
    };
    
    const notificationConfig = config[type] || config.info;
    
    icon.className = `fas ${notificationConfig.icon}`;
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg transition-transform z-50 ${notificationConfig.bgColor} ${notificationConfig.textColor}`;
    messageSpan.innerHTML = `${notificationConfig.emoji} ${message}`;
    
    // Mostrar notificación
    notification.style.transform = 'translateX(0)';
    
    // Ocultar después del tiempo especificado
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
    }, duration);
}

// Mantener compatibilidad con la función anterior
function showNotification(message, type = 'info') {
    showSmartNotification(message, type);
}

// ================================
// FUNCIONES DE CHAT INTELIGENTE
// ================================

function startChatConversation() {
    console.log('Starting intelligent chat...');
    
    // Hide start button, show input
    document.getElementById('chat-start-container').classList.add('hidden');
    document.getElementById('chat-input-container').classList.remove('hidden');
    
    // Show typing indicator
    showTypingIndicator();
    
    // Start chat via SocketIO
    socket.emit('start_intelligent_chat');
    
    chatActive = true;
}

function resetChat() {
    console.log('Resetting chat...');
    
    // Reset interface
    resetChatInterface();
    
    // Reset server state
    socket.emit('reset_intelligent_chat');
    
    chatActive = false;
    currentUserId = null;
}

function resetChatInterface() {
    // Clear messages except welcome
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="flex items-start space-x-3">
            <div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
                <i class="fas fa-robot text-white text-sm"></i>
            </div>
            <div class="bg-gray-800 rounded-lg p-4 max-w-md">
                <p class="text-gray-300 text-sm">👋 ¡Hola! Soy tu asistente inteligente. Haz clic en "Iniciar Chat" para comenzar a crear contenido personalizado.</p>
            </div>
        </div>
    `;
    
    // Show start button, hide input
    document.getElementById('chat-start-container').classList.remove('hidden');
    document.getElementById('chat-input-container').classList.add('hidden');
    
    // Hide options and examples
    document.getElementById('chat-options').classList.add('hidden');
    document.getElementById('chat-examples').classList.add('hidden');
    
    // Clear input
    document.getElementById('chat-input').value = '';
    
    hideTypingIndicator();
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) {
        showSmartNotification('Por favor escribe algo', 'warning');
        return;
    }
    
    // Add user message to chat
    addUserMessage(message);
    
    // Clear input
    input.value = '';
    
    // Hide options and examples
    document.getElementById('chat-options').classList.add('hidden');
    document.getElementById('chat-examples').classList.add('hidden');
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to server
    socket.emit('send_chat_message', { message: message });
}

function sendQuickOption(option) {
    // Add user message
    addUserMessage(option);
    
    // Hide options
    document.getElementById('chat-options').classList.add('hidden');
    document.getElementById('chat-examples').classList.add('hidden');
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to server
    socket.emit('send_chat_message', { message: option });
}

function addUserMessage(message) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3 justify-end';
    
    messageDiv.innerHTML = `
        <div class="bg-purple-600 rounded-lg p-4 max-w-md">
            <p class="text-white text-sm">${escapeHtml(message)}</p>
        </div>
        <div class="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center flex-shrink-0">
            <i class="fas fa-user text-white text-sm"></i>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

function addBotMessage(message, options = [], examples = []) {
    const messagesContainer = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'flex items-start space-x-3';
    
    messageDiv.innerHTML = `
        <div class="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center flex-shrink-0">
            <i class="fas fa-robot text-white text-sm"></i>
        </div>
        <div class="bg-gray-800 rounded-lg p-4 max-w-md">
            <p class="text-gray-300 text-sm">${escapeHtml(message)}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    
    // Show options if provided
    if (options && options.length > 0) {
        showQuickOptions(options);
    }
    
    // Show examples if provided
    if (examples && examples.length > 0) {
        showExamples(examples);
    }
    
    scrollToBottom();
}

function showQuickOptions(options) {
    const optionsContainer = document.getElementById('quick-options');
    const chatOptions = document.getElementById('chat-options');
    
    optionsContainer.innerHTML = '';
    
    options.forEach(option => {
        const button = document.createElement('button');
        button.className = 'px-3 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm rounded-lg transition-colors';
        button.textContent = option;
        button.onclick = () => sendQuickOption(option);
        
        optionsContainer.appendChild(button);
    });
    
    chatOptions.classList.remove('hidden');
}

function showExamples(examples) {
    const examplesList = document.getElementById('examples-list');
    const chatExamples = document.getElementById('chat-examples');
    
    examplesList.innerHTML = examples.join(' • ');
    chatExamples.classList.remove('hidden');
}

function showTypingIndicator() {
    document.getElementById('typing-indicator').classList.remove('hidden');
    scrollToBottom();
}

function hideTypingIndicator() {
    document.getElementById('typing-indicator').classList.add('hidden');
}

function scrollToBottom() {
    const messagesContainer = document.getElementById('chat-messages').parentElement;
    setTimeout(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 100);
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendChatMessage();
    }
}

function showChatCompleted() {
    // Disable input
    document.getElementById('chat-input').disabled = true;
    document.getElementById('send-button').disabled = true;
    
    // Show completion message
    setTimeout(() => {
        addBotMessage('🎉 ¡Excelente! He recopilado toda la información necesaria. Ahora voy a generar tu contenido personalizado...');
    }, 1000);
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}