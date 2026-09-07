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
        this.createSkipLink();
        this.createPanel();
        this.loadSettings();
        this.applyAllSettings();
        this.setupEventListeners();
        this.syncWithConfigPage();
        this.setupMouseTracking();
        
        // Escuchar cambios de página para mantener el modo oscuro
        this.observePageChanges();
        
        // Navegación por teclado en modales
        this.setupModalKeyboardNav();
    }
    
    createSkipLink() {
        if (document.getElementById('skip-to-main')) return;
        const skip = document.createElement('a');
        skip.id = 'skip-to-main';
        skip.href = '#principal';
        skip.className = 'skip-link';
        skip.textContent = 'Saltar al contenido principal';
        document.body.insertBefore(skip, document.body.firstChild);
        
        // Asignar id al contenido principal (prioriza .principal sobre .contenido)
        document.addEventListener('DOMContentLoaded', () => {
            const main = document.querySelector('.principal') || document.querySelector('main') || document.querySelector('.contenido');
            if (main && !main.id) main.id = 'principal';
        });
    }
    
    setupMouseTracking() {
        this._mouseX = window.innerWidth / 2;
        this._mouseY = window.innerHeight / 2;
        
        document.addEventListener('mousemove', (e) => {
            this._mouseX = e.clientX;
            this._mouseY = e.clientY;
            this.updateReadingTools();
        });
    }
    
    updateReadingTools() {
        if (this.state.readingMask) {
            let mask = document.getElementById('acc-reading-mask');
            if (mask) mask.style.top = this._mouseY + 'px';
        }
        if (this.state.readingGuide) {
            let guide = document.getElementById('acc-reading-guide');
            if (guide) guide.style.top = this._mouseY + 'px';
        }
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
                        <div class="accesibilidad-opcion">
                            <span><i class="fa-solid fa-moon icon-accesibilidad"></i> Tema Oscuro</span>
                            <label class="toggle-switch">
                                <input type="checkbox" id="acc-darkTheme">
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

        // Trap focus dentro del panel
        this.panel.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            const focusable = this.panel.querySelectorAll('input, button, [tabindex]:not([tabindex="-1"])');
            if (focusable.length === 0) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
        
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
        const firstFocusable = this.panel.querySelector('input, button, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) setTimeout(() => firstFocusable.focus(), 100);
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
            { id: 'acc-screenReader', prop: 'screenReader' },
            { id: 'acc-darkTheme', prop: 'darkTheme' }
        ];
        
        toggles.forEach(({ id, prop }) => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', (e) => {
                    // Exclusión mutua entre invertColors y darkTheme
                    if (id === 'acc-invertColors' && e.target.checked) {
                        this.state.darkTheme = false;
                        this.applySetting('darkTheme');
                        const darkPanelToggle = document.getElementById('acc-darkTheme');
                        if (darkPanelToggle) darkPanelToggle.checked = false;
                        const darkConfigToggle = document.getElementById('darkTheme');
                        if (darkConfigToggle) darkConfigToggle.checked = false;
                    }
                    if (id === 'acc-darkTheme' && e.target.checked) {
                        this.state.invertColors = false;
                        this.applySetting('invertColors');
                        const invPanelToggle = document.getElementById('acc-invertColors');
                        if (invPanelToggle) invPanelToggle.checked = false;
                        const invConfigToggle = document.getElementById('invertColors');
                        if (invConfigToggle) invConfigToggle.checked = false;
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
            { target: 'letterSpacing', min: 0, max: 5, step: 0.5, unit: 'px' }
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
                if (this.state.readingMask) {
                    if (!document.getElementById('acc-reading-mask')) {
                        const el = document.createElement('div');
                        el.id = 'acc-reading-mask';
                        el.style.cssText = `position:fixed;left:0;right:0;height:60px;background:rgba(207,160,89,0.25);border-top:2px solid #cfa059;border-bottom:2px solid #cfa059;pointer-events:none;z-index:9999;transform:translateY(-50%);top:${this._mouseY||window.innerHeight/2}px;transition:top 0.05s linear;`;
                        document.body.appendChild(el);
                    }
                } else {
                    const el = document.getElementById('acc-reading-mask');
                    if (el) el.remove();
                }
                break;
            case 'readingGuide':
                body.classList.toggle('reading-guide', this.state.readingGuide);
                if (this.state.readingGuide) {
                    if (!document.getElementById('acc-reading-guide')) {
                        const el = document.createElement('div');
                        el.id = 'acc-reading-guide';
                        el.style.cssText = `position:fixed;left:0;right:0;height:2px;background:#cfa059;opacity:0.8;pointer-events:none;z-index:9998;top:${this._mouseY||window.innerHeight/2}px;transition:top 0.05s linear;box-shadow:0 0 15px rgba(207,160,89,0.4);`;
                        document.body.appendChild(el);
                    }
                } else {
                    const el = document.getElementById('acc-reading-guide');
                    if (el) el.remove();
                }
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
        }
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
            darkTheme: 'acc-darkTheme',
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
        
        if (lineSpacingSpan) lineSpacingSpan.textContent = this.state.lineSpacing;
        if (letterSpacingSpan) letterSpacingSpan.textContent = this.state.letterSpacing + 'px';
    }
    
    enableScreenReader() {
        if (this.screenReaderActive) return;
        this.screenReaderActive = true;
        setTimeout(() => { this.readPageContent(); }, 500);
    }
    
    readPageContent() {
        if (!this.screenReaderActive) return;
        
        // Orden: barra superior → accesibilidad → chatbot → barra lateral → contenido principal → footer
        const orden = [
            { selector: '.barra-superior', label: 'Barra de navegación superior' },
            { selector: '.btn-accesibilidad', label: 'Botón de accesibilidad' },
            { selector: '.btn-chatbot',    label: 'Botón de chatbot' },
            { selector: '.barra-lateral',  label: 'Menú lateral de navegación' },
            { selector: '.contenido',       label: 'Contenido principal' },
            { selector: '.contenedor-footer, footer', label: null }
        ];
        
        let fullText = '';
        const vistas = new Set();
        
        orden.forEach(({ selector, label }) => {
            const el = document.querySelector(selector);
            if (el && !vistas.has(el)) {
                vistas.add(el);
                const text = this.extractReadableText(el);
                if (text.trim()) {
                    fullText += (label ? label + '. ' : '') + text + '. ';
                }
            }
        });
        
        if (fullText.trim()) {
            this.speak(fullText.trim(), true);
        }
    }
    
    extractReadableText(element) {
        if (!element) return '';
        const clone = element.cloneNode(true);
        
        const excludeSelectors = [
            '.accesibilidad-panel',
            '#ventana-chatbot',
            'script', 'style', 'noscript', 'iframe', 'svg',
            '.toggle-switch', '.range-control'
        ];
        
        excludeSelectors.forEach(sel => {
            clone.querySelectorAll(sel).forEach(el => el.remove());
        });
        
        // Incluir aria-label cuando no hay texto visible
        clone.querySelectorAll('[aria-label]').forEach(el => {
            if (!el.textContent.trim()) el.textContent = el.getAttribute('aria-label');
        });
        
        let text = clone.innerText || clone.textContent || '';
        return text.replace(/\s+/g, ' ').replace(/\n+/g, ' ').trim();
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
        // Preservar darkTheme — restablecer solo afecta opciones de accesibilidad
        const currentDarkTheme = this.state.darkTheme;
        
        this.state = {
            grayscale: false,
            highContrast: false,
            invertColors: false,
            readingMask: false,
            readingGuide: false,
            highlightLinks: false,
            dyslexicFont: false,
            darkTheme: currentDarkTheme,  // se conserva
            lineSpacing: 1.5,
            letterSpacing: 0,
            screenReader: false
        };
        
        const body = document.body;
        // NO tocar dark-theme al restablecer
        body.classList.remove(
            'grayscale', 'high-contrast', 'invert-colors',
            'reading-mask', 'reading-guide', 'highlight-links', 'dyslexic-font'
        );
        
        body.style.lineHeight = '';
        body.style.letterSpacing = '';
        
        // Remover elementos de herramientas de lectura
        const mask = document.getElementById('acc-reading-mask');
        if (mask) mask.remove();
        const guide = document.getElementById('acc-reading-guide');
        if (guide) guide.remove();
        
        if (this.screenReaderActive) {
            this.disableScreenReader();
        }
        
        this.updatePanelValues();
        this.saveSettings();
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
    }
    
    dispatchChangeEvent(key, value) {
        const event = new CustomEvent('accessibilityChanged', {
            detail: { key, value }
        });
        window.dispatchEvent(event);
    }
    
    setupModalKeyboardNav() {
        // Cerrar modales con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Escape') return;
            const modalSelectors = '.modal.active, .modal-overlay.active, .modal-creacion-evaluacion.active, .modal-agregar-pregunta.active';
            document.querySelectorAll(modalSelectors).forEach(modal => {
                modal.classList.remove('active');
            });
        });

        // Focus trap en modales
        document.addEventListener('keydown', (e) => {
            if (e.key !== 'Tab') return;
            const activeModal = document.querySelector('.modal.active, .modal-overlay.active, .modal-creacion-evaluacion.active, .modal-agregar-pregunta.active');
            if (!activeModal) return;

            const focusable = activeModal.querySelectorAll('input:not([type="hidden"]), button, select, textarea, a[href], [tabindex]:not([tabindex="-1"])');
            if (focusable.length === 0) return;

            const first = focusable[0];
            const last = focusable[focusable.length - 1];

            if (e.shiftKey && document.activeElement === first) {
                e.preventDefault();
                last.focus();
            } else if (!e.shiftKey && document.activeElement === last) {
                e.preventDefault();
                first.focus();
            }
        });
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
                { id: 'letterSpacing', prop: 'letterSpacing' }
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