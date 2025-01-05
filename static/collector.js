(function() {
    // Actualizar todas las URLs del backend
    const BACKEND_URL = 'https://hoomextractor.online/api';

    const siteDetectors = {
        // Detector para Inmuebles24
        'inmuebles24.com': {
            images: function() {
                debugLog("🔍 Iniciando detección de imágenes en inmuebles24.com");
                const images = new Set();
                
                // Selectores específicos de inmuebles24 incluyendo carruseles
                const selectors = [
                    '[data-qa="POSTING_CARD_GALLERY"] img',
                    '[class*="Gallery"] img',
                    '[class*="PostingCard"] img',
                    '.posting-gallery img',
                    '.gallery-box img',
                    // Carruseles específicos de inmuebles24
                    '[class*="carousel"] img',
                    '[class*="slider"] img',
                    '[class*="Swiper"] img',
                    // Atributos de datos comunes en inmuebles24
                    'img[data-src]',
                    'img[data-lazy]',
                    'img[data-full]'
                ];

                // Buscar en selectores específicos
                selectors.forEach(selector => {
                    debugLog(`Buscando imágenes con selector: ${selector}`);
                    document.querySelectorAll(selector).forEach(img => {
                        const src = img.getAttribute('src');
                        // Buscar en múltiples atributos de datos
                        const dataSources = [
                            img.getAttribute('data-original'),
                            img.getAttribute('data-lazy'),
                            img.getAttribute('data-src'),
                            img.getAttribute('data-full'),
                            img.getAttribute('data-zoom'),
                            img.getAttribute('data-high-res'),
                            src
                        ].filter(Boolean); // Eliminar valores null/undefined

                        // Agregar todas las fuentes válidas
                        dataSources.forEach(source => {
                            if (source && !isThumbnail(source)) {
                                debugLog(`Imagen encontrada: ${source}`);
                                images.add(source);
                            }
                        });
                    });
                });

                // Buscar en scripts (para carruseles dinámicos)
                document.querySelectorAll('script').forEach(script => {
                    try {
                        const content = script.textContent;
                        const jsonMatch = content.match(/window\.__INITIAL_STATE__\s*=\s*({.*?});/);
                        if (jsonMatch) {
                            const data = JSON.parse(jsonMatch[1]);
                            // Buscar URLs de imágenes en el estado inicial
                            JSON.stringify(data).match(/"(https?:\/\/[^"]+\.(?:jpg|jpeg|png|gif|webp))"/gi)
                                ?.forEach(url => {
                                    const cleanUrl = url.replace(/['"]/g, '');
                                    if (!isThumbnail(cleanUrl)) {
                                        images.add(cleanUrl);
                                    }
                                });
                        }
                    } catch (e) {
                        debugLog("Error parsing script:", e);
                    }
                });

                return processImages(images);
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
        debugLog("🚀 Iniciando detección de imágenes");
        return new Promise((resolve) => {
            // Esperar 2 segundos para que carguen las imágenes
            setTimeout(() => {
                const detector = detectSite();
                const images = detector.images();
                debugLog(`🎯 Detección finalizada. ${images.length} imágenes encontradas`);
                resolve(images);
            }, 2000);
        });
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
        const images = new Set(); // Usar Set para evitar duplicados

        // 1. Buscar imágenes en elementos img directamente
        document.querySelectorAll('img').forEach(img => {
            const src = img.getAttribute('src');
            if (src && !isThumbnail(src)) {
                // Buscar la versión de mayor calidad
                const originalSrc = img.getAttribute('data-original') || 
                                  img.getAttribute('data-lazy') ||
                                  img.getAttribute('data-src') ||
                                  img.getAttribute('data-full') ||
                                  src;
                images.add(originalSrc);
            }
        });

        // 2. Buscar en elementos de galería específicamente
        const gallerySelectors = [
            '[class*="gallery"]', '[class*="carousel"]', '[class*="slider"]',
            '[class*="galeria"]', '[class*="lightbox"]', '[class*="photo"]',
            '[id*="gallery"]', '[id*="carousel"]', '[id*="slider"]',
            '[role="gallery"]', '[role="slider"]'
        ].join(',');

        document.querySelectorAll(gallerySelectors).forEach(element => {
            // Buscar en atributos data-*
            const dataAttributes = [
                'data-src', 'data-lazy', 'data-original', 'data-full',
                'data-image', 'data-zoom', 'data-large', 'data-modal',
                'data-big', 'data-zoom-image', 'data-srcset', 'data-sizes'
            ];

            dataAttributes.forEach(attr => {
                const value = element.getAttribute(attr);
                if (value && !isThumbnail(value)) {
                    images.add(value);
                }
            });
        });

        // 3. Buscar en scripts (para galerías dinámicas)
        document.querySelectorAll('script').forEach(script => {
            try {
                const content = script.textContent;
                // Buscar URLs de imágenes en el contenido del script
                const urlMatches = content.match(/"(https?:\/\/[^"]+\.(?:jpg|jpeg|png|gif|webp))"/gi);
                if (urlMatches) {
                    urlMatches.forEach(url => {
                        const cleanUrl = url.replace(/['"]/g, '');
                        if (!isThumbnail(cleanUrl)) {
                            images.add(cleanUrl);
                        }
                    });
                }
            } catch (e) {
                console.log("Error parsing script:", e);
            }
        });

        // Función para verificar si es una miniatura
        function isThumbnail(url) {
            const thumbnailPatterns = [
                /thumb/i, /small/i, /mini/i, /tiny/i, /icon/i,
                /\b(\d{2,3}x\d{2,3})\b/, // patrones como "100x100"
                /thumbnail/i, /preview/i, /miniatura/i,
                /\b(50|60|70|80|90|100|120|150)\b/ // tamaños comunes de miniaturas
            ];
            return thumbnailPatterns.some(pattern => pattern.test(url));
        }

        // 4. Convertir URLs relativas a absolutas y filtrar
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

        // 5. Eliminar duplicados y ordenar por tamaño probable
        const uniqueImages = [...new Set(processedImages)]
            .sort((a, b) => b.length - a.length);

        console.log(`Detectadas ${uniqueImages.length} imágenes únicas de alta calidad:`, uniqueImages);
        return uniqueImages;
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
        try {
            console.log("🏁 Iniciando createPopup");
            
            // Verificar URL
            const currentURL = window.location.href;
            
            // Crear popup con opción manual
            const popup = document.createElement('div');
            popup.style.position = 'fixed';
            popup.style.top = '20px';
            popup.style.right = '20px';
            popup.style.backgroundColor = 'white';
            popup.style.padding = '20px';
            popup.style.border = '1px solid black';
            popup.style.zIndex = '9999';
            popup.innerHTML = `
                <h3>Selección de Imágenes</h3>
                <p>Elija el método de selección:</p>
                <button onclick="startManualSelection()">Selección Manual</button>
                <button onclick="startAutoSelection()">Detección Automática</button>
                <button onclick="this.parentElement.remove()">Cancelar</button>
            `;
            document.body.appendChild(popup);
            
            // Hacer las funciones disponibles
            window.startManualSelection = async function() {
                popup.remove();
                alert('Haga clic en las imágenes que desea seleccionar. Las imágenes seleccionadas tendrán un borde rojo.');
                const selectedImages = manualImageSelection();
                // Continuar con el proceso normal usando las imágenes seleccionadas
                showPropertyForm(selectedImages);
            };
            
            window.startAutoSelection = async function() {
                popup.remove();
                const images = await detectImages();
                showPropertyForm(images);
            };
            
        } catch (error) {
            console.error("❌ Error en createPopup:", error);
            alert('Error: ' + error.message);
        }
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
        const images = new Set();
        document.querySelectorAll('img').forEach(img => {
            img.style.cursor = 'pointer';
            img.onclick = function() {
                if (this.style.border === '2px solid red') {
                    this.style.border = '';
                    images.delete(this.src);
                } else {
                    this.style.border = '2px solid red';
                    images.add(this.src);
                }
            }
        });
        return Array.from(images);
    }

    // Hacer las funciones disponibles globalmente
    window.detectImages = detectImages;
    window.createPopup = createPopup;
    window.detectPrice = detectPrice;
    window.detectLocation = detectLocation;
    window.detectFeatures = detectFeatures;
    window.detectGeneralFeatures = detectGeneralFeatures;
    
    // No ejecutar createPopup automáticamente
    // Dejar que el bookmarklet lo haga
    console.log("Collector.js cargado correctamente");
})(); 