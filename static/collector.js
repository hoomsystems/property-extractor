(function() {
    // Actualizar todas las URLs del backend
    const BACKEND_URL = 'https://hoomextractor.online/api';

    const siteDetectors = {
        // Detector para Inmuebles24
        'inmuebles24.com': {
            images: function() {
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
                        console.log("Error parsing script:", e);
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
        const detector = detectSite();
        return detector.images();
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

    // Función para detectar la ubicación
    function detectLocation() {
        console.log("Detectando ubicación...");
        const locationElements = document.querySelectorAll(
            '[class*="address"],[class*="location"],[class*="ubicacion"],[id*="address"],[id*="location"],[class*="direccion"]'
        );

        for (let element of locationElements) {
            const text = element.textContent.trim();
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

    function detectDescription() {
        console.log("Detectando descripción...");
        const descriptionElements = document.querySelectorAll(
            '[class*="description"],[class*="descripcion"],[class*="detail"],[class*="detalle"],' +
            '[class*="about"],[class*="content"],[itemprop="description"]'
        );

        for (let element of descriptionElements) {
            const text = element.textContent.trim();
            if (text.length > 20) { // Asegurarnos de que es una descripción válida
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
        console.log("Creando popup...");
        const currentURL = window.location.href;
        
        // Verificar si la URL ya existe
        const urlExists = await checkIfUrlExists(currentURL);
        if (urlExists) {
            alert('Esta propiedad ya está guardada en el sistema.');
            return;
        }
        
        const detectedInfo = detectInmuebles24Info();
        const images = detectImages();
        const description = detectDescription();
        
        // Cargar lista de vendedores
        const agents = await loadAgents();
        console.log("Vendedores cargados:", agents);
        
        const popup = document.createElement('div');
        popup.className = 'property-collector-popup';
        popup.innerHTML = `
            <div class="popup-form">
                <h3>Guardar Propiedad</h3>
                <form id="propertyForm">
                    <h4>Información de la Propiedad</h4>
                    <input type="text" id="title" placeholder="Título" value="${document.title}" required>
                    <input type="text" id="price" placeholder="Precio" value="${detectedInfo.price}" required>
                    <input type="text" id="location" placeholder="Ubicación" value="${detectedInfo.location}" required>
                    <input type="hidden" id="url" value="${currentURL}">
                    
                    <h4>Características</h4>
                    <div class="form-row">
                        <input type="number" id="construction_size" placeholder="M² de Construcción" 
                            value="${detectedInfo.features.construction_size || ''}" step="0.01">
                        <input type="number" id="lot_size" placeholder="M² de Terreno" 
                            value="${detectedInfo.features.lot_size || ''}" step="0.01">
                    </div>
                    <div class="form-row">
                        <input type="number" id="bedrooms" placeholder="Número de Recámaras" 
                            value="${detectedInfo.features.bedrooms || ''}" step="1">
                        <input type="number" id="bathrooms" placeholder="Número de Baños" 
                            value="${detectedInfo.features.bathrooms || ''}" step="0.5">
                    </div>
                    <div class="form-row">
                        <input type="number" id="parking_spaces" placeholder="Espacios de Estacionamiento" 
                            value="${detectedInfo.features.parking_spaces || ''}" step="1">
                        <input type="number" id="floors" placeholder="Número de Niveles" 
                            value="${detectedInfo.features.floors || ''}" step="1">
                    </div>
                    
                    <h4>Descripción de la Propiedad</h4>
                    <textarea id="description" placeholder="Descripción de la propiedad" rows="4">${description}</textarea>
                    
                    <h4>Notas Personales</h4>
                    <textarea id="notes" placeholder="Agrega tus notas personales sobre esta propiedad" rows="4"></textarea>
                    
                    <h4>Vendedor</h4>
                    <div class="agent-section">
                        <select id="agent_select" class="full-width">
                            <option value="">Seleccionar vendedor existente</option>
                            ${agents.map(agent => `
                                <option value="${agent.id}">${agent.name} (${agent.email || agent.phone || 'Sin contacto'})</option>
                            `).join('')}
                            <option value="new">+ Agregar nuevo vendedor</option>
                        </select>
                        
                        <div id="new_agent_fields" style="display: none; margin-top: 10px;">
                            <input type="text" id="new_agent_name" placeholder="Nombre del vendedor">
                            <input type="tel" id="new_agent_phone" placeholder="Teléfono">
                            <input type="email" id="new_agent_email" placeholder="Email">
                            <input type="url" id="new_agent_website" placeholder="Sitio web">
                        </div>
                    </div>
                    
                    <h4>Imágenes Detectadas (${images.length})</h4>
                    <div class="images-grid">
                        ${images.map((img, index) => `
                            <div class="image-item">
                                <img src="${img}" alt="Property image ${index + 1}">
                                <label>
                                    <input type="checkbox" name="selected_images" value="${img}" checked>
                                    Incluir
                                </label>
                                <label>
                                    <input type="radio" name="main_image" value="${img}" ${index === 0 ? 'checked' : ''}>
                                    Imagen principal
                                </label>
                            </div>
                        `).join('')}
                    </div>
                    
                    <button type="submit">Guardar</button>
                    <button type="button" onclick="this.parentElement.parentElement.remove()">Cerrar</button>
                </form>
            </div>
        `;

        // Agregar estilos adicionales
        const style = document.createElement('style');
        style.textContent = `
            .property-collector-popup {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                z-index: 999999;
                max-height: 90vh;
                overflow-y: auto;
                width: 400px;
            }
            .property-collector-popup input,
            .property-collector-popup textarea {
                display: block;
                width: 100%;
                margin: 5px 0;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            .form-row {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }
            .form-row input {
                flex: 1;
            }
            .images-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin: 10px 0;
            }
            .image-item img {
                max-width: 100%;
                height: auto;
                margin-bottom: 5px;
            }
            h4 {
                margin-top: 15px;
                margin-bottom: 10px;
            }
            .agent-section {
                margin: 10px 0;
            }
            .full-width {
                width: 100%;
                padding: 8px;
                margin: 5px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(popup);

        // Manejar cambio en select de vendedor
        const agentSelect = popup.querySelector('#agent_select');
        const newAgentFields = popup.querySelector('#new_agent_fields');
        
        agentSelect.addEventListener('change', (e) => {
            if (e.target.value === 'new') {
                newAgentFields.style.display = 'block';
            } else {
                newAgentFields.style.display = 'none';
                if (e.target.value) {
                    const selectedAgent = agents.find(a => a.id === parseInt(e.target.value));
                    if (selectedAgent) {
                        // No necesitamos llenar los campos antiguos ya que los eliminamos
                    }
                }
            }
        });

        // Modificar el manejador del formulario
        popup.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log("Enviando formulario...");

            // Obtener imágenes seleccionadas
            const selectedImages = Array.from(
                document.querySelectorAll('input[name="selected_images"]:checked')
            ).map(input => input.value);

            // Obtener imagen principal
            const mainImage = document.querySelector('input[name="main_image"]:checked')?.value || selectedImages[0];

            let agentData = null;
            const agentSelectValue = document.getElementById('agent_select').value;

            if (agentSelectValue === 'new') {
                agentData = {
                    name: document.getElementById('new_agent_name').value,
                    phone: document.getElementById('new_agent_phone').value,
                    email: document.getElementById('new_agent_email').value,
                    website: document.getElementById('new_agent_website').value
                };
            } else if (agentSelectValue) {
                agentData = agents.find(a => a.id === parseInt(agentSelectValue));
            }

            const formData = {
                title: document.getElementById('title').value,
                price: document.getElementById('price').value,
                location: document.getElementById('location').value,
                url: document.getElementById('url').value,
                description: document.getElementById('description').value,
                notes: document.getElementById('notes').value,
                images: selectedImages,
                main_image: mainImage,
                
                // Dimensiones
                lot_size: parseFloat(document.getElementById('lot_size').value) || null,
                construction_size: parseFloat(document.getElementById('construction_size').value) || null,
                
                // Características numéricas
                bathrooms: parseFloat(document.getElementById('bathrooms').value) || null,
                bedrooms: parseInt(document.getElementById('bedrooms').value) || null,
                parking_spaces: parseInt(document.getElementById('parking_spaces').value) || null,
                floors: parseInt(document.getElementById('floors').value) || null,
                
                // Información del agente
                agent: agentData
            };

            console.log("Datos a enviar:", formData);

            try {
                const response = await fetch(`${BACKEND_URL}/properties`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const result = await response.json();
                    console.log("Propiedad guardada:", result);
                    alert('Propiedad guardada exitosamente');
                    popup.remove();
                } else {
                    const errorText = await response.text();
                    console.error("Error response:", response.status, errorText);
                    alert(`Error al guardar la propiedad: ${response.status} - ${errorText}`);
                }
            } catch (error) {
                console.error("Error de conexión:", error);
                alert('Error de conexión. Por favor, intenta de nuevo más tarde.');
            }
        });
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