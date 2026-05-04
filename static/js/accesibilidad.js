// ========================
// ACCESIBILIDAD AVANZADA
// ========================

class AccessibilityManager {
    constructor() {
        // Estado de las opciones
        this.state = {
            grayscale: false,
            highContrast: false,
            invertColors: false,
            readingMask: false,
            readingGuide: false,
            highlightLinks: false,
            dyslexicFont: false,
            darkTheme: false,
            lineSpacing: 1.5,
            letterSpacing: 0,
            fontSize: 16,
            screenReader: false
        };
        
        this.panel = null;
        this.isOpen = false;
        this.speechSynthesis = window.speechSynthesis;
        this.speechUtterance = null;
        this.screenReaderActive = false;
        this.currentReadingTimeout = null;
        this.init();
    }
    
    init() {
        this.createPanel();
        this.loadSettings();
        this.applyAllSettings();
        this.setupEventListeners();
        this.syncWithConfigPage();
        
        // Escuchar cambios de página para mantener el modo oscuro
        this.observePageChanges();
    }
    
    createPanel() {
        // Crear botón flotante si no existe
        if (!document.querySelector('.btn-accesibilidad')) {
            const btn = document.createElement('button');
            btn.className = 'btn-accesibilidad';
            btn.setAttribute('aria-label', 'Abrir panel de accesibilidad');
            btn.innerHTML = '<i class="fa-solid fa-universal-access"></i>';
            document.body.appendChild(btn);
            
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.togglePanel();
            });
        }
        
        // Crear panel si no existe
        if (!document.querySelector('.accesibilidad-panel')) {
            const panel = document.createElement('div');
            panel.className = 'accesibilidad-panel';
            panel.innerHTML = `
                <div class="accesibilidad-panel-header">
                    <i class="fa-solid fa-universal-access"></i>
                    <h3>Opciones de Accesibilidad</h3>
                    <button class="btn-cerrar-panel" aria-label="Cerrar panel">
                        <i class="fa-solid fa-times"></i>
                    </button>
                </div>
                <div class="accesibilidad-panel-body">
                    <!-- Ajustes Visuales -->
                    <div class="accesibilidad-seccion">
                        <h4><i class="fa-solid fa-eye icon-accesibilidad"></i> Ajustes Visuales</h4>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-chart-simple icon-accesibilidad"></i> Escala de Grises</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-grayscale">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-circle-half-stroke icon-accesibilidad"></i> Alto Contraste</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-highContrast">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-palette icon-accesibilidad"></i> Invertir Colores</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-invertColors">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Herramientas de Lectura -->
                    <div class="accesibilidad-seccion">
                        <h4><i class="fa-solid fa-book-open-reader icon-accesibilidad"></i> Herramientas de Lectura</h4>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-ear-listen icon-accesibilidad"></i> Lector de Pantalla</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-screenReader">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-mask icon-accesibilidad"></i> Máscara de Lectura</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-readingMask">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-ruler icon-accesibilidad"></i> Guía de Lectura</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-readingGuide">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-link icon-accesibilidad"></i> Resaltar Enlaces</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-highlightLinks">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                    </div>
                    
                    <!-- Tipografía -->
                    <div class="accesibilidad-seccion">
                        <h4><i class="fa-solid fa-font icon-accesibilidad"></i> Tipografía</h4>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-text-size icon-accesibilidad"></i> Fuente para Dislexia</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-dyslexicFont">
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-arrow-up-wide-short icon-accesibilidad"></i> Espaciado Vertical</span>
                            <div class="range-control">
                                <button class="btn-range" data-action="decrease" data-target="lineSpacing">
                                    <i class="fa-solid fa-minus"></i>
                                </button>
                                <span id="lineSpacingValue" class="range-value">1.5</span>
                                <button class="btn-range" data-action="increase" data-target="lineSpacing">
                                    <i class="fa-solid fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-arrow-left-right icon-accesibilidad"></i> Espaciado Horizontal</span>
                            <div class="range-control">
                                <button class="btn-range" data-action="decrease" data-target="letterSpacing">
                                    <i class="fa-solid fa-minus"></i>
                                </button>
                                <span id="letterSpacingValue" class="range-value">0px</span>
                                <button class="btn-range" data-action="increase" data-target="letterSpacing">
                                    <i class="fa-solid fa-plus"></i>
                                </button>
                            </div>
                        </div>
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-text-height icon-accesibilidad"></i> Tamaño del Texto</span>
                            <div class="range-control">
                                <button class="btn-range" data-action="decrease" data-target="fontSize">
                                    <i class="fa-solid fa-minus"></i>
                                </button>
                                <span id="fontSizeValue" class="range-value">16px</span>
                                <button class="btn-range" data-action="increase" data-target="fontSize">
                                    <i class="fa-solid fa-plus"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Cursor -->
                    <div class="accesibilidad-seccion">
                        <h4><i class="fa-solid fa-mouse-pointer icon-accesibilidad"></i> Tamaño del Cursor</h4>
                        <div class="accesibilidad-opcion cursor-selector">
                            <span><i class="fa-solid fa-arrow-pointer"></i> Tamaño</span>
                            <div class="cursor-size-selector">
                                <button class="cursor-opt" data-size="small" title="Cursor pequeño">◉</button>
                                <button class="cursor-opt" data-size="medium" title="Cursor mediano">◉</button>
                                <button class="cursor-opt" data-size="large" title="Cursor grande">◉</button>
                                <button class="cursor-opt" data-size="xlarge" title="Cursor extra grande">◉</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="accesibilidad-footer">
                        <button class="btn-reset" id="resetAccessibility">
                            <i class="fa-solid fa-undo"></i> Restaurar valores predeterminados
                        </button>
                    </div>
                </div>
            `;
            document.body.appendChild(panel);
        }
        
        this.panel = document.querySelector('.accesibilidad-panel');
        
        const closeBtn = this.panel.querySelector('.btn-cerrar-panel');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closePanel());
        }
        
        document.addEventListener('click', (e) => {
            const btn = document.querySelector('.btn-accesibilidad');
            if (this.isOpen && !this.panel.contains(e.target) && (!btn || !btn.contains(e.target))) {
                this.closePanel();
            }
        });
    }
    
    togglePanel() {
        if (this.isOpen) {
            this.closePanel();
        } else {
            this.openPanel();
        }
    }
    
    openPanel() {
        this.panel.classList.add('active');
        this.isOpen = true;
    }
    
    closePanel() {
        this.panel.classList.remove('active');
        this.isOpen = false;
    }
    
    setupEventListeners() {
        const toggles = [
            { id: 'acc-grayscale', prop: 'grayscale' },
            { id: 'acc-highContrast', prop: 'highContrast' },
            { id: 'acc-invertColors', prop: 'invertColors' },
            { id: 'acc-readingMask', prop: 'readingMask' },
            { id: 'acc-readingGuide', prop: 'readingGuide' },
            { id: 'acc-highlightLinks', prop: 'highlightLinks' },
            { id: 'acc-dyslexicFont', prop: 'dyslexicFont' },
            { id: 'acc-screenReader', prop: 'screenReader' }
        ];
        
        toggles.forEach(({ id, prop }) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    // Exclusión mutua entre invertColors y darkTheme
                    if (id === 'acc-invertColors' && e.target.checked) {
                        const darkThemeToggle = document.getElementById('darkTheme');
                        if (darkThemeToggle && darkThemeToggle.checked) {
                            darkThemeToggle.checked = false;
                            this.state.darkTheme = false;
                            this.applySetting('darkTheme');
                        }
                    }
                    
                    this.state[prop] = e.target.checked;
                    this.applySetting(prop);
                    this.saveSettings();
                    this.dispatchChangeEvent(prop, e.target.checked);
                });
            }
        });
        
        const ranges = [
            { target: 'lineSpacing', min: 1, max: 2.5, step: 0.1, unit: '' },
            { target: 'letterSpacing', min: 0, max: 5, step: 0.5, unit: 'px' },
            { target: 'fontSize', min: 12, max: 28, step: 1, unit: 'px' }
        ];
        
        ranges.forEach(({ target, min, max, step, unit }) => {
            const decreaseBtn = this.panel.querySelector(`[data-action="decrease"][data-target="${target}"]`);
            const increaseBtn = this.panel.querySelector(`[data-action="increase"][data-target="${target}"]`);
            const valueSpan = document.getElementById(`${target}Value`);
            
            if (decreaseBtn && increaseBtn) {
                decreaseBtn.addEventListener('click', () => {
                    let newValue = this.state[target] - step;
                    if (newValue >= min) {
                        this.state[target] = parseFloat(newValue.toFixed(1));
                        this.applySetting(target);
                        this.saveSettings();
                        if (valueSpan) {
                            valueSpan.textContent = this.state[target] + unit;
                        }
                        this.dispatchChangeEvent(target, this.state[target]);
                    }
                });
                
                increaseBtn.addEventListener('click', () => {
                    let newValue = this.state[target] + step;
                    if (newValue <= max) {
                        this.state[target] = parseFloat(newValue.toFixed(1));
                        this.applySetting(target);
                        this.saveSettings();
                        if (valueSpan) {
                            valueSpan.textContent = this.state[target] + unit;
                        }
                        this.dispatchChangeEvent(target, this.state[target]);
                    }
                });
            }
        });
        
        const cursorOpts = this.panel.querySelectorAll('.cursor-opt');
        cursorOpts.forEach(opt => {
            opt.addEventListener('click', () => {
                const size = opt.getAttribute('data-size');
                this.setCursorSize(size);
                cursorOpts.forEach(o => o.classList.remove('active'));
                opt.classList.add('active');
                this.dispatchChangeEvent('cursorSize', size);
            });
        });
        
        const resetBtn = document.getElementById('resetAccessibility');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetAll());
        }
    }
    
    applySetting(key) {
        const body = document.body;
        
        switch(key) {
            case 'grayscale':
                body.classList.toggle('grayscale', this.state.grayscale);
                break;
            case 'highContrast':
                body.classList.toggle('high-contrast', this.state.highContrast);
                break;
            case 'invertColors':
                body.classList.toggle('invert-colors', this.state.invertColors);
                break;
            case 'darkTheme':
                body.classList.toggle('dark-theme', this.state.darkTheme);
                break;
            case 'readingMask':
                body.classList.toggle('reading-mask', this.state.readingMask);
                break;
            case 'readingGuide':
                body.classList.toggle('reading-guide', this.state.readingGuide);
                break;
            case 'highlightLinks':
                body.classList.toggle('highlight-links', this.state.highlightLinks);
                break;
            case 'dyslexicFont':
                body.classList.toggle('dyslexic-font', this.state.dyslexicFont);
                break;
            case 'screenReader':
                if (this.state.screenReader) {
                    this.enableScreenReader();
                } else {
                    this.disableScreenReader();
                }
                break;
            case 'lineSpacing':
                body.style.lineHeight = this.state.lineSpacing;
                break;
            case 'letterSpacing':
                body.style.letterSpacing = this.state.letterSpacing + 'px';
                break;
            case 'fontSize':
                body.style.fontSize = this.state.fontSize + 'px';
                this.applyFontSizeToAll();
                break;
        }
    }
    
    applyFontSizeToAll() {
        const fontSize = this.state.fontSize;
        const scaleFactor = fontSize / 16;
        
        const elementsToScale = [
            'body', '.titulo', '.subtitulo', '.seccion-titulo', 
            '.tarjeta-numero', '.tarjeta-texto', '.pregunta-enunciado',
            '.evaluacion-titulo', '.evaluacion-descripcion', '.mensaje-bot',
            '.mensaje-usuario', '.form-group label', '.form-group input',
            '.btn', '.barra-lateral-link', '.tabla-preguntas td',
            '.tabla-preguntas th', '.perfil-nombre-completo', '.perfil-campo span',
            '.estadistica-valor', '.metrica-valor', '.config-card-header h3'
        ];
        
        elementsToScale.forEach(selector => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(el => {
                if (!el.getAttribute('data-original-font-size')) {
                    const computed = window.getComputedStyle(el).fontSize;
                    el.setAttribute('data-original-font-size', computed);
                }
                const originalSize = parseFloat(el.getAttribute('data-original-font-size'));
                if (!isNaN(originalSize)) {
                    el.style.fontSize = (originalSize * scaleFactor) + 'px';
                }
            });
        });
    }
    
    applyAllSettings() {
        Object.keys(this.state).forEach(key => {
            this.applySetting(key);
        });
        this.updatePanelValues();
    }
    
    updatePanelValues() {
        const toggleMap = {
            grayscale: 'acc-grayscale',
            highContrast: 'acc-highContrast',
            invertColors: 'acc-invertColors',
            readingMask: 'acc-readingMask',
            readingGuide: 'acc-readingGuide',
            highlightLinks: 'acc-highlightLinks',
            dyslexicFont: 'acc-dyslexicFont',
            screenReader: 'acc-screenReader'
        };
        
        Object.entries(toggleMap).forEach(([prop, id]) => {
            const element = document.getElementById(id);
            if (element) {
                element.checked = this.state[prop];
            }
        });
        
        const lineSpacingSpan = document.getElementById('lineSpacingValue');
        const letterSpacingSpan = document.getElementById('letterSpacingValue');
        const fontSizeSpan = document.getElementById('fontSizeValue');
        
        if (lineSpacingSpan) lineSpacingSpan.textContent = this.state.lineSpacing;
        if (letterSpacingSpan) letterSpacingSpan.textContent = this.state.letterSpacing + 'px';
        if (fontSizeSpan) fontSizeSpan.textContent = this.state.fontSize + 'px';
        
        const cursorSize = localStorage.getItem('cursorSize') || 'small';
        const cursorOpts = this.panel.querySelectorAll('.cursor-opt');
        cursorOpts.forEach(opt => {
            if (opt.getAttribute('data-size') === cursorSize) {
                opt.classList.add('active');
            } else {
                opt.classList.remove('active');
            }
        });
    }
    
    setCursorSize(size) {
        let cursorSizePx;
        switch(size) {
            case 'small': cursorSizePx = 'auto'; break;
            case 'medium': cursorSizePx = '24px'; break;
            case 'large': cursorSizePx = '32px'; break;
            case 'xlarge': cursorSizePx = '48px'; break;
            default: cursorSizePx = 'auto';
        }
        
        if (cursorSizePx !== 'auto') {
            document.body.style.cursor = `url('data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="${parseInt(cursorSizePx)}" height="${parseInt(cursorSizePx)}" viewBox="0 0 24 24"%3E%3Cpath fill="black" d="M5 3l14 9-5.5 2.5L12 20l-3-6-4-11z"/%3E%3C/svg%3E') ${parseInt(cursorSizePx) / 2} 0, auto`;
        } else {
            document.body.style.cursor = '';
        }
        
        localStorage.setItem('cursorSize', size);
    }
    
    enableScreenReader() {
        if (this.screenReaderActive) return;
        
        this.screenReaderActive = true;
        
        // Leer el contenido de la página
        setTimeout(() => {
            this.readPageContent();
        }, 500);
    }
    
    readPageContent() {
        if (!this.screenReaderActive) return;
        
        // Obtener el contenido principal
        const mainContent = document.querySelector('.principal') || document.querySelector('main') || document.body;
        
        // Extraer texto relevante
        const textToRead = this.extractReadableText(mainContent);
        
        if (textToRead && textToRead.trim()) {
            this.speak(textToRead, true);
        }
    }
    
    extractReadableText(element) {
        if (!element) return '';
        
        const clone = element.cloneNode(true);
        
        const excludeSelectors = [
            'nav', '.barra-lateral', '.menu-dropdown', '.accesibilidad-panel',
            '.btn-accesibilidad', '.btn-chatbot', '#ventana-chatbot',
            'script', 'style', 'noscript', 'iframe', 'svg',
            'button', '.btn', '.toggle-switch', '.range-control'
        ];
        
        excludeSelectors.forEach(selector => {
            const elements = clone.querySelectorAll(selector);
            elements.forEach(el => el.remove());
        });
        
        let text = clone.innerText || clone.textContent || '';
        text = text.replace(/\s+/g, ' ').replace(/\n+/g, ' ').trim();
        
        return text;
    }
    
    disableScreenReader() {
        if (!this.screenReaderActive) return;
        
        this.screenReaderActive = false;
        
        if (this.currentReadingTimeout) {
            clearTimeout(this.currentReadingTimeout);
            this.currentReadingTimeout = null;
        }
        
        if (this.speechSynthesis) {
            this.speechSynthesis.cancel();
        }
        
        this.speak('Lector de pantalla desactivado.');
    }
    
    speak(text, isLongText = false) {
        if (!this.speechSynthesis) {
            console.warn('Este navegador no soporta síntesis de voz');
            return;
        }
        
        if (!this.screenReaderActive && !isLongText) return;
        
        this.speechSynthesis.cancel();
        
        if (isLongText && text.length > 500) {
            this.speakLongText(text);
            return;
        }
        
        this.speechUtterance = new SpeechSynthesisUtterance(text);
        this.speechUtterance.lang = 'es-MX';
        this.speechUtterance.rate = 0.9;
        this.speechUtterance.pitch = 1;
        this.speechUtterance.volume = 1;
        
        this.speechSynthesis.speak(this.speechUtterance);
    }
    
    speakLongText(text) {
        const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
        let index = 0;
        
        const speakNext = () => {
            if (!this.screenReaderActive) return;
            if (index >= sentences.length) return;
            
            const sentence = sentences[index].trim();
            if (sentence) {
                const utterance = new SpeechSynthesisUtterance(sentence);
                utterance.lang = 'es-MX';
                utterance.rate = 0.9;
                utterance.pitch = 1;
                utterance.volume = 1;
                
                utterance.onend = () => {
                    index++;
                    speakNext();
                };
                
                this.speechSynthesis.speak(utterance);
            } else {
                index++;
                speakNext();
            }
        };
        
        speakNext();
    }
    
    resetAll() {
        this.state = {
            grayscale: false,
            highContrast: false,
            invertColors: false,
            readingMask: false,
            readingGuide: false,
            highlightLinks: false,
            dyslexicFont: false,
            darkTheme: false,
            lineSpacing: 1.5,
            letterSpacing: 0,
            fontSize: 16,
            screenReader: false
        };
        
        const body = document.body;
        body.classList.remove(
            'grayscale', 'high-contrast', 'invert-colors', 'dark-theme',
            'reading-mask', 'reading-guide', 'highlight-links', 'dyslexic-font'
        );
        
        body.style.lineHeight = '';
        body.style.letterSpacing = '';
        body.style.fontSize = '';
        body.style.cursor = '';
        
        const elementsWithOriginalSize = document.querySelectorAll('[data-original-font-size]');
        elementsWithOriginalSize.forEach(el => {
            el.style.fontSize = '';
            el.removeAttribute('data-original-font-size');
        });
        
        if (this.screenReaderActive) {
            this.disableScreenReader();
        }
        
        this.updatePanelValues();
        this.saveSettings();
        localStorage.removeItem('cursorSize');
        this.dispatchChangeEvent('reset', true);
    }
    
    saveSettings() {
        localStorage.setItem('accessibilitySettings', JSON.stringify(this.state));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('accessibilitySettings');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                this.state = { ...this.state, ...parsed };
            } catch(e) {
                console.error('Error loading accessibility settings:', e);
            }
        }
        
        const cursorSize = localStorage.getItem('cursorSize');
        if (cursorSize) {
            this.setCursorSize(cursorSize);
        }
    }
    
    dispatchChangeEvent(key, value) {
        const event = new CustomEvent('accessibilityChanged', {
            detail: { key, value }
        });
        window.dispatchEvent(event);
    }
    
    observePageChanges() {
        // Observar cambios de URL para navegación SPA
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                setTimeout(() => {
                    this.applyAllSettings();
                    if (this.screenReaderActive) {
                        setTimeout(() => this.readPageContent(), 1000);
                    }
                }, 100);
            }
        }).observe(document, { subtree: true, childList: true });
    }
    
    syncWithConfigPage() {
        const syncElements = () => {
            const configToggles = {
                grayscale: 'grayscale',
                highContrast: 'highContrast',
                invertColors: 'invertColors',
                darkTheme: 'darkTheme',
                readingMask: 'readingMask',
                readingGuide: 'readingGuide',
                highlightLinks: 'highlightLinks',
                dyslexicFont: 'dyslexicFont',
                screenReader: 'screenReader'
            };
            
            Object.entries(configToggles).forEach(([prop, id]) => {
                const element = document.getElementById(id);
                if (element) {
                    element.checked = this.state[prop];
                    
                    element.addEventListener('change', (e) => {
                        this.state[prop] = e.target.checked;
                        this.applySetting(prop);
                        this.saveSettings();
                        this.updatePanelValues();
                        
                        const panelToggle = document.getElementById(`acc-${prop}`);
                        if (panelToggle) {
                            panelToggle.checked = e.target.checked;
                        }
                    });
                }
            });
            
            const configRanges = [
                { id: 'lineSpacing', prop: 'lineSpacing' },
                { id: 'letterSpacing', prop: 'letterSpacing' },
                { id: 'fontSize', prop: 'fontSize' }
            ];
            
            configRanges.forEach(({ id, prop }) => {
                const element = document.getElementById(id);
                if (element) {
                    element.value = this.state[prop];
                    
                    element.addEventListener('input', (e) => {
                        let value = parseFloat(e.target.value);
                        this.state[prop] = value;
                        this.applySetting(prop);
                        this.saveSettings();
                        this.updatePanelValues();
                    });
                }
            });
        };
        
        window.addEventListener('accessibilityChanged', (e) => {
            const { key, value } = e.detail;
            
            const configElement = document.getElementById(key);
            if (configElement) {
                if (configElement.type === 'checkbox') {
                    configElement.checked = value;
                } else {
                    configElement.value = value;
                }
            }
        });
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', syncElements);
        } else {
            syncElements();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager = new AccessibilityManager();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}