(function() {
    console.log("Iniciando collector.js");
    
    // Actualizar todas las URLs del backend
    const BACKEND_URL = 'https://hoomextractor.online/api';

    // Declarar las funciones que necesitamos exponer globalmente
    window.detectImages = null;
    window.manualImageSelection = null;
    window.showPropertyForm = null;
    window.startAutomatic = null;
    window.startManual = null;
    window.finishSelection = null;

    const siteDetectors = {
        // Detector para Inmuebles24
        'inmuebles24.com': {
            images: function() {
                debugLog("🔍 Iniciando detección de imágenes en inmuebles24.com");
                const images = new Set();
                
                // Esperar a que carguen las imágenes dinámicas
                setTimeout(() => {
                    // Selectores más específicos
                    const selectors = [
                        // Galería principal
                        '[data-qa="POSTING_CARD_GALLERY"] img',
                        '[class*="Gallery"] img',
                        '[class*="gallery"] img',
                        '[class*="PostingCard"] img',
                        // Carrusel
                        '[class*="carousel"] img',
                        '[class*="slider"] img',
                        '[class*="Swiper"] img',
                        // Contenedores específicos
                        '.posting-gallery img',
                        '.gallery-box img',
                        '.property-gallery img',
                        // Atributos de datos
                        'img[data-src]',
                        'img[data-lazy]',
                        'img[data-full]',
                        'img[data-original]',
                        // Selectores adicionales
                        '[role="img"]',
                        '[aria-label*="imagen"]',
                        '[aria-label*="foto"]'
                    ];

                    selectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(img => {
                            const sources = [
                                img.src,
                                img.dataset.src,
                                img.dataset.lazy,
                                img.dataset.full,
                                img.dataset.original,
                                img.currentSrc,
                                img.getAttribute('src'),
                                img.style.backgroundImage?.replace(/url\(['"]?(.*?)['"]?\)/i, '$1')
                            ].filter(Boolean);

                            sources.forEach(src => {
                                if (src && !isThumbnail(src)) {
                                    debugLog(`Imagen encontrada: ${src}`);
                                    images.add(src);
                                }
                            });
                        });
                    });
                }, 2000); // Esperar 2 segundos

                return Array.from(images);
            }
        },
        
        // Detector para Vivanuncios
        'vivanuncios.com.mx': {
            images: function() {
                const images = new Set();
                
                // Selectores específicos de Vivanuncios incluyendo carruseles
                const selectors = [
                    '.gallery-content img',
                    '.re-DetailHeader img',
                    '[class*="PhotoGallery"] img',
                    '[class*="Carousel"] img',
                    // Carruseles específicos de Vivanuncios
                    '.slick-slide img',
                    '.owl-item img',
                    '[class*="slider"] img',
                    // Contenedores de galería
                    '[data-gallery] img',
                    '[class*="lightbox"] img'
                ];

                // Buscar en selectores y atributos de datos
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(img => {
                        const dataSources = [
                            img.getAttribute('src'),
                            img.getAttribute('data-original'),
                            img.getAttribute('data-lazy'),
                            img.getAttribute('data-src'),
                            img.getAttribute('data-full-url')
                        ].filter(Boolean);

                        dataSources.forEach(source => {
                            if (source && !isThumbnail(source)) {
                                images.add(source);
                            }
                        });
                    });
                });

                return processImages(images);
            }
        },

        // Detector para Lamudi
        'lamudi.com.mx': {
            images: function() {
                const images = new Set();
                
                // Selectores específicos de Lamudi
                const selectors = [
                    '.swiper-wrapper img',
                    '.gallery-top img',
                    '.property-gallery img',
                    '[class*="Gallery"] img'
                ];

                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(img => {
                        const src = img.getAttribute('src');
                        if (src && !isThumbnail(src)) {
                            const originalSrc = img.getAttribute('data-lazy') || 
                                             img.getAttribute('data-src') || 
                                             src;
                            images.add(originalSrc);
                        }
                    });
                });

                return processImages(images);
            }
        },

        // Detector genérico (fallback)
        'default': {
            images: function() {
                const images = new Set();
                
                // 1. Buscar en elementos img
                document.querySelectorAll('img').forEach(img => {
                    const src = img.getAttribute('src');
                    if (src && !isThumbnail(src)) {
                        const originalSrc = img.getAttribute('data-original') || 
                                         img.getAttribute('data-lazy') ||
                                         img.getAttribute('data-src') ||
                                         img.getAttribute('data-full') ||
                                         src;
                        images.add(originalSrc);
                    }
                });

                // 2. Buscar en galerías genéricas
                const gallerySelectors = [
                    '[class*="gallery"]', '[class*="carousel"]', '[class*="slider"]',
                    '[class*="galeria"]', '[class*="lightbox"]', '[class*="photo"]',
                    '[id*="gallery"]', '[id*="carousel"]', '[id*="slider"]',
                    '[role="gallery"]', '[role="slider"]'
                ].join(',');

                document.querySelectorAll(gallerySelectors).forEach(element => {
                    element.querySelectorAll('img').forEach(img => {
                        const src = img.getAttribute('src');
                        if (src && !isThumbnail(src)) {
                            images.add(src);
                        }
                    });
                });

                return processImages(images);
            }
        }
    };

    // Función auxiliar para procesar imágenes
    function processImages(images) {
        // Convertir URLs relativas a absolutas y filtrar
        const processedImages = Array.from(images).map(url => {
            try {
                return new URL(url, window.location.href).href;
            } catch (e) {
                return url;
            }
        }).filter(url => {
            return url.match(/\.(jpg|jpeg|png|gif|webp)/i) && 
                   url.startsWith('http') && 
                   !isThumbnail(url);
        });

        // Eliminar duplicados y ordenar por tamaño probable
        const uniqueImages = [...new Set(processedImages)]
            .sort((a, b) => b.length - a.length);

        console.log(`Detectadas ${uniqueImages.length} imágenes únicas:`, uniqueImages);
        return uniqueImages;
    }

    // Función para detectar el sitio y usar el detector apropiado
    function detectSite() {
        const hostname = window.location.hostname;
        for (const site in siteDetectors) {
            if (hostname.includes(site)) {
                return siteDetectors[site];
            }
        }
        return siteDetectors.default;
    }

    // Uso
    function detectImages() {
        console.log("Detectando imágenes...");
        const images = new Set();
        
        // 1. Buscar todas las imágenes en la página
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.dataset.src || img.dataset.lazy || img.getAttribute('src');
            if (src && !isThumbnail(src)) {
                images.add(src);
            }
        });

        // 2. Buscar en carruseles específicos
        const carouselSelectors = [
            '[class*="carousel"] img',
            '[class*="slider"] img',
            '[class*="gallery"] img',
            '.posting-gallery img',
            '.gallery-box img'
        ];

        carouselSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(img => {
                const src = img.src || img.dataset.src || img.dataset.lazy;
                if (src && !isThumbnail(src)) {
                    images.add(src);
                }
            });
        });

        return Array.from(images);
    }

    // Función para detectar el precio
    function detectPrice() {
        console.log("Detectando precio...");
        const pricePatterns = [
            /\$[\d,]+\.?\d*/,  // $1,234.56
            /[\d,]+\s*mil/i,    // 1,234 mil
            /[\d,]+\s*mdp/i,    // 1,234 mdp
            /[\d,]+\s*millones/i, // 1,234 millones
            /[\d,]+\s*mxn/i,    // 1,234 MXN
            /[\d,]+\s*pesos/i   // 1,234 pesos
        ];

        // Buscar en elementos específicos primero
        const priceElements = document.querySelectorAll('[class*="price"],[class*="precio"],[id*="price"],[id*="precio"]');
        for (let element of priceElements) {
            const text = element.textContent.trim();
            console.log("Elemento de precio encontrado:", text);
            for (let pattern of pricePatterns) {
                if (pattern.test(text)) {
                    console.log("Precio detectado:", text);
                    return text;
                }
            }
        }

        // Buscar en todo el texto
        const text = document.body.innerText;
        for (let pattern of pricePatterns) {
            const match = text.match(pattern);
            if (match) {
                console.log("Precio detectado en texto:", match[0]);
                return match[0];
            }
        }
        return '';
    }

    // Función para decodificar texto UTF-8
    function decodeUTF8(text) {
        try {
            return decodeURIComponent(escape(text));
        } catch (e) {
            return text;
        }
    }

    // Función para detectar la ubicación
    function detectLocation() {
        console.log("Detectando ubicación...");
        const locationElements = document.querySelectorAll(
            '[class*="address"],[class*="location"],[class*="ubicacion"],[id*="address"],[id*="location"],[class*="direccion"]'
        );

        for (let element of locationElements) {
            const text = decodeUTF8(element.textContent.trim());
            if (text) {
                console.log("Ubicación detectada:", text);
                return text;
            }
        }
        return '';
    }

    // Función para detectar características numéricas
    function detectFeatures() {
        const features = {
            bathrooms: null,
            bedrooms: null,
            parking_spaces: null,
            lot_size: null,
            construction_size: null,
            floors: null,
            is_new: false
        };

        // Patrones para cada característica
        const patterns = {
            bathrooms: [
                /(\d+\.?\d*)\s*(baños?|wc|sanitarios?)/i,
                /baños?:\s*(\d+\.?\d*)/i
            ],
            bedrooms: [
                /(\d+)\s*(recámaras?|habitaciones?|cuartos?|dormitorios?)/i,
                /recámaras?:\s*(\d+)/i
            ],
            parking_spaces: [
                /(\d+)\s*(cajones?|estacionamientos?|parking)/i,
                /estacionamientos?:\s*(\d+)/i
            ],
            lot_size: [
                /(\d+\.?\d*)\s*m2?\s*(terreno|lote)/i,
                /terreno:\s*(\d+\.?\d*)\s*m2?/i
            ],
            construction_size: [
                /(\d+\.?\d*)\s*m2?\s*(construcción|construidos)/i,
                /construcción:\s*(\d+\.?\d*)\s*m2?/i
            ],
            floors: [
                /(\d+)\s*(pisos?|niveles?|plantas?)/i,
                /niveles?:\s*(\d+)/i
            ]
        };

        // Buscar en elementos específicos primero
        const featureElements = document.querySelectorAll(
            '[class*="feature"],[class*="caracteristica"],[class*="detail"],[class*="detalle"]'
        );

        // Función auxiliar para buscar patrones
        function findMatch(text, patternList) {
            for (let pattern of patternList) {
                const match = text.match(pattern);
                if (match) return parseFloat(match[1]);
            }
            return null;
        }

        // Buscar en elementos específicos
        featureElements.forEach(element => {
            const text = element.textContent.trim();
            for (let [key, patternList] of Object.entries(patterns)) {
                if (features[key] === null) {
                    features[key] = findMatch(text, patternList);
                }
            }
        });

        // Buscar en todo el texto si no se encontró en elementos específicos
        const fullText = document.body.innerText;
        for (let [key, patternList] of Object.entries(patterns)) {
            if (features[key] === null) {
                features[key] = findMatch(fullText, patternList);
            }
        }

        // Detectar si es nueva
        features.is_new = /nueva|estrenar|preventa|pre-?venta/i.test(fullText);

        return features;
    }

    // Función para detectar características generales
    function detectGeneralFeatures() {
        const commonFeatures = {
            general_features: [],
            services: [],
            exterior_features: []
        };

        // Palabras clave para cada categoría
        const keywords = {
            general_features: [
                'aire acondicionado', 'calefacción', 'cocina integral', 'closets',
                'ventilador', 'amueblado', 'vestidor', 'sala', 'comedor'
            ],
            services: [
                'agua', 'luz', 'gas', 'internet', 'cable', 'teléfono',
                'seguridad', 'vigilancia', 'mantenimiento'
            ],
            exterior_features: [
                'jardín', 'piscina', 'alberca', 'terraza', 'balcón',
                'patio', 'área verde', 'roof garden', 'asador'
            ]
        };

        const text = document.body.innerText.toLowerCase();
        
        // Buscar cada característica en el texto
        for (let [category, features] of Object.entries(keywords)) {
            commonFeatures[category] = features.filter(feature => 
                text.includes(feature.toLowerCase())
            );
        }

        return commonFeatures;
    }

    // Función para detectar imágenes
    function detectImages() {
        console.log("Detectando imágenes...");
        const images = new Set();
        
        // 1. Buscar todas las imágenes en la página
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.dataset.src || img.dataset.lazy || img.getAttribute('src');
            if (src && !isThumbnail(src)) {
                images.add(src);
            }
        });

        // 2. Buscar en carruseles específicos
        const carouselSelectors = [
            '[class*="carousel"] img',
            '[class*="slider"] img',
            '[class*="gallery"] img',
            '.posting-gallery img',
            '.gallery-box img'
        ];

        carouselSelectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(img => {
                const src = img.src || img.dataset.src || img.dataset.lazy;
                if (src && !isThumbnail(src)) {
                    images.add(src);
                }
            });
        });

        return Array.from(images);
    }

    // Función para detectar información del agente inmobiliario
    function detectAgentInfo() {
        console.log("Detectando información del agente...");
        const agentInfo = {
            name: '',
            phone: '',
            email: '',
            website: '',
            social_media: {}
        };

        // Buscar elementos que probablemente contengan información del agente
        const agentElements = document.querySelectorAll(
            '[class*="agent"],[class*="broker"],[class*="contact"],[class*="seller"],' +
            '[class*="agente"],[class*="vendedor"],[class*="contacto"]'
        );

        // Patrones para detectar información
        const patterns = {
            phone: /(?:\+?[0-9]{2}[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}/g,
            email: /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g,
            name: /(?:agente|asesor|vendedor|contacto):\s*([A-Za-zÀ-ÿ\s.]+)/i
        };

        // Buscar en elementos específicos primero
        agentElements.forEach(element => {
            const text = element.textContent.trim();
            
            // Buscar teléfono
            const phoneMatch = text.match(patterns.phone);
            if (phoneMatch && !agentInfo.phone) {
                agentInfo.phone = phoneMatch[0];
                console.log("Teléfono detectado:", agentInfo.phone);
            }

            // Buscar email
            const emailMatch = text.match(patterns.email);
            if (emailMatch && !agentInfo.email) {
                agentInfo.email = emailMatch[0];
                console.log("Email detectado:", agentInfo.email);
            }

            // Buscar nombre
            const nameMatch = text.match(patterns.name);
            if (nameMatch && !agentInfo.name) {
                agentInfo.name = nameMatch[1].trim();
                console.log("Nombre detectado:", agentInfo.name);
            }
        });

        // Buscar redes sociales
        document.querySelectorAll('a').forEach(link => {
            const href = link.href.toLowerCase();
            if (href.includes('facebook.com')) {
                agentInfo.social_media.facebook = href;
            } else if (href.includes('instagram.com')) {
                agentInfo.social_media.instagram = href;
            } else if (href.includes('linkedin.com')) {
                agentInfo.social_media.linkedin = href;
            }
        });

        return agentInfo;
    }

    // Función para detectar información específica de inmuebles24.com
    function detectInmuebles24Info() {
        console.log("Detectando información específica de inmuebles24.com...");
        const info = {
            price: '',
            location: '',
            features: {
                bathrooms: null,
                bedrooms: null,
                parking_spaces: null,
                lot_size: null,
                construction_size: null,
                floors: null,
                is_new: false
            },
            agent: {
                name: '',
                phone: '',
                email: '',
                website: '',
                social_media: {}
            }
        };

        try {
            // Detectar precio (específico para inmuebles24)
            const priceElement = document.querySelector('[data-qa="POSTING_CARD_PRICE"]') || 
                               document.querySelector('.price-items') ||
                               document.querySelector('[class*="price"]');
            if (priceElement) {
                info.price = priceElement.textContent.trim();
                console.log("Precio detectado:", info.price);
            }

            // Detectar ubicación
            const locationElement = document.querySelector('[data-qa="POSTING_CARD_LOCATION"]') ||
                                  document.querySelector('.location-items') ||
                                  document.querySelector('[class*="location"]');
            if (locationElement) {
                info.location = locationElement.textContent.trim();
                console.log("Ubicación detectada:", info.location);
            }

            // Detectar características
            const featureElements = document.querySelectorAll('[class*="feature"],[class*="attribute"],[class*="detail"]');
            featureElements.forEach(element => {
                const text = element.textContent.toLowerCase();
                if (text.includes('baño')) {
                    const match = text.match(/(\d+\.?\d*)/);
                    if (match) info.features.bathrooms = parseFloat(match[1]);
                }
                if (text.includes('recámara') || text.includes('dormitorio')) {
                    const match = text.match(/(\d+)/);
                    if (match) info.features.bedrooms = parseInt(match[1]);
                }
                // ... más detecciones específicas
            });

            // Detectar información del agente
            const agentElement = document.querySelector('[class*="broker"],[class*="agent"],[class*="contact"]');
            if (agentElement) {
                const agentText = agentElement.textContent;
                // Buscar nombre del agente
                const nameMatch = agentText.match(/(?:agente|asesor|vendedor):\s*([^,\n]+)/i);
                if (nameMatch) info.agent.name = nameMatch[1].trim();

                // Buscar teléfono
                const phoneMatch = agentText.match(/(?:\+?[0-9]{2}[-.]?)?\(?[0-9]{3}\)?[-.]?[0-9]{3}[-.]?[0-9]{4}/);
                if (phoneMatch) info.agent.phone = phoneMatch[0];

                // Buscar email
                const emailMatch = agentText.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/);
                if (emailMatch) info.agent.email = emailMatch[0];
            }

        } catch (error) {
            console.error("Error detectando información:", error);
        }

        return info;
    }

    // Función para detectar la descripción
    function detectDescription() {
        console.log("Detectando descripción...");
        const descriptionElements = document.querySelectorAll(
            '[class*="description"],[class*="descripcion"],[id*="description"],[id*="descripcion"]'
        );

        for (let element of descriptionElements) {
            const text = decodeUTF8(element.textContent.trim());
            if (text) {
                console.log("Descripción detectada:", text);
                return text;
            }
        }
        return '';
    }

    async function loadAgents() {
        try {
            const response = await fetch(`${BACKEND_URL}/agents`);
            if (response.ok) {
                return await response.json();
            }
            return [];
        } catch (error) {
            console.error("Error cargando vendedores:", error);
            return [];
        }
    }

    async function checkIfUrlExists(url) {
        try {
            const response = await fetch(`${BACKEND_URL}/properties/check_url?url=${encodeURIComponent(url)}`);
            const data = await response.json();
            return data.exists;
        } catch (error) {
            console.error("Error verificando URL:", error);
            return false;
        }
    }

    async function createPopup() {
        const popup = document.createElement('div');
        popup.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 20px;
            border: 1px solid black;
            z-index: 9999;
        `;
        popup.innerHTML = `
            <h3>Selección de Imágenes</h3>
            <p>Elija el método de selección:</p>
            <button onclick="window.startManualSelection()">Selección Manual</button>
            <button onclick="window.startAutoSelection()">Detección Automática</button>
            <button onclick="this.parentElement.remove()">Cancelar</button>
        `;
        document.body.appendChild(popup);
    }

    function debugLog(message, data = null) {
        const timestamp = new Date().toISOString();
        console.log(`[${timestamp}] ${message}`);
        if (data) {
            console.log(data);
        }
    }

    // Función para verificar si una URL es válida
    function isValidImageUrl(url) {
        try {
            const urlObj = new URL(url);
            return /\.(jpg|jpeg|png|gif|webp)/i.test(urlObj.pathname);
        } catch (e) {
            return false;
        }
    }

    function manualImageSelection() {
        console.log("Iniciando selección manual");
        const images = new Set();
        
        // Crear barra de herramientas
        const toolbar = document.createElement('div');
        toolbar.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: white;
            padding: 15px;
            border: 1px solid #ccc;
            border-radius: 8px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            font-family: Arial, sans-serif;
            min-width: 250px;
        `;
        
        toolbar.innerHTML = `
            <div style="margin-bottom: 15px; font-size: 14px;">
                <p style="margin: 0 0 10px 0;">Haga clic en las imágenes para seleccionarlas</p>
                <div style="background: #f5f5f5; padding: 8px; border-radius: 4px;">
                    Imágenes seleccionadas: <span id="selectedCount" style="font-weight: bold;">0</span>
                </div>
            </div>
            <button onclick="window.finishSelection()" 
                    style="width: 100%; padding: 10px; background-color: #4CAF50; color: white; 
                           border: none; border-radius: 4px; cursor: pointer; font-size: 14px;
                           transition: background-color 0.2s;">
                Finalizar Selección
            </button>
        `;
        
        document.body.appendChild(toolbar);

        // Hacer todas las imágenes seleccionables
        document.querySelectorAll('img').forEach(img => {
            if (img.width > 100 && img.height > 100) {
                img.style.cursor = 'pointer';
                img.style.transition = 'all 0.2s';
                
                // Agregar hover effect
                img.addEventListener('mouseover', function() {
                    if (this.style.border !== '2px solid red') {
                        this.style.boxShadow = '0 0 5px rgba(0,0,0,0.3)';
                    }
                });
                
                img.addEventListener('mouseout', function() {
                    if (this.style.border !== '2px solid red') {
                        this.style.boxShadow = 'none';
                    }
                });
                
                img.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    if (this.style.border === '2px solid red') {
                        this.style.border = '';
                        this.style.boxShadow = 'none';
                        images.delete(this.src);
                    } else {
                        this.style.border = '2px solid red';
                        this.style.boxShadow = '0 0 8px rgba(255,0,0,0.3)';
                        images.add(this.src);
                    }
                    document.getElementById('selectedCount').textContent = images.size;
                };
            }
        });

        // Función para finalizar selección
        window.finishSelection = function() {
            console.log("Finalizando selección");
            const selectedImages = Array.from(images);
            console.log("Imágenes seleccionadas:", selectedImages);
            
            if (selectedImages.length === 0) {
                alert('Por favor seleccione al menos una imagen');
                return;
            }
            
            // Limpiar la interfaz de selección
            toolbar.remove();
            document.querySelectorAll('img').forEach(img => {
                img.style.border = '';
                img.style.cursor = '';
                img.onclick = null;
            });
            
            // Mostrar el formulario
            showPropertyForm(selectedImages);
        };
    }

    function showPropertyForm(images) {
        console.log("Mostrando formulario para imágenes:", images);
        const formPopup = document.createElement('div');
        formPopup.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border: 1px solid black;
            z-index: 10000;
            max-height: 90vh;
            overflow-y: auto;
            min-width: 500px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        `;

        // Detectar información automáticamente
        const price = detectPrice() || '';
        const location = detectLocation() || '';
        const description = detectDescription() || '';
        const features = detectGeneralFeatures();

        formPopup.innerHTML = `
            <h3 style="margin-bottom: 20px;">Guardar Propiedad</h3>
            <form id="propertyForm" style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                    <label>Precio:</label>
                    <input type="text" name="price" value="${price}" required style="width: 100%; padding: 5px;">
                </div>
                <div>
                    <label>Ubicación:</label>
                    <input type="text" name="location" value="${location}" required style="width: 100%; padding: 5px;">
                </div>
                <div>
                    <label>Descripción:</label>
                    <textarea name="description" required style="width: 100%; height: 100px; padding: 5px;">${description}</textarea>
                </div>
                <div>
                    <label>Imágenes seleccionadas (${images.length}):</label>
                    <div style="max-height: 200px; overflow-y: auto; display: flex; flex-wrap: wrap; gap: 10px; margin-top: 10px;">
                        ${images.map(img => `
                            <img src="${img}" style="max-width: 100px; height: auto; border: 1px solid #ccc;">
                        `).join('')}
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 20px;">
                    <button type="submit" style="padding: 10px 20px;">Guardar Propiedad</button>
                    <button type="button" onclick="this.closest('.property-form').remove()" style="padding: 10px 20px;">Cancelar</button>
                </div>
            </form>
        `;
        formPopup.className = 'property-form';
        document.body.appendChild(formPopup);

        // Manejar el envío del formulario
        document.getElementById('propertyForm').onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const propertyData = {
                price: formData.get('price'),
                location: formData.get('location'),
                description: formData.get('description'),
                images: images,
                features: features,
                url: window.location.href
            };

            try {
                const response = await fetch(`${BACKEND_URL}/properties`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(propertyData)
                });

                if (response.ok) {
                    alert('Propiedad guardada exitosamente');
                    formPopup.remove();
                } else {
                    throw new Error('Error al guardar la propiedad');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al guardar la propiedad: ' + error.message);
            }
        };
    }

    // Asegurarnos que las funciones se expongan correctamente
    window.manualImageSelection = manualImageSelection;
    window.detectImages = detectImages;
    window.showPropertyForm = showPropertyForm;
    window.finishSelection = finishSelection;
    
    // Definir las funciones de inicio
    window.startAutomatic = function() {
        console.log("Iniciando detección automática");
        const images = window.detectImages();
        if (images && images.length > 0) {
            window.showPropertyForm(images);
        } else {
            alert('No se encontraron imágenes');
        }
    };

    window.startManual = function() {
        console.log("Iniciando selección manual");
        window.manualImageSelection();
    };

    // Verificar que todas las funciones estén disponibles
    const requiredFunctions = [
        'detectImages',
        'manualImageSelection',
        'showPropertyForm',
        'startAutomatic',
        'startManual',
        'finishSelection'
    ];

    const missingFunctions = requiredFunctions.filter(fn => !window[fn]);
    if (missingFunctions.length > 0) {
        console.error('Funciones faltantes:', missingFunctions);
    } else {
        console.log('Todas las funciones requeridas están disponibles');
    }

    console.log("Collector.js cargado completamente. Funciones disponibles:", {
        detectImages: !!window.detectImages,
        manualImageSelection: !!window.manualImageSelection,
        showPropertyForm: !!window.showPropertyForm,
        startAutomatic: !!window.startAutomatic,
        startManual: !!window.startManual,
        finishSelection: !!window.finishSelection
    });
})(); 