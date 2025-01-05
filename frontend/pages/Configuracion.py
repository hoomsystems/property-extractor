import streamlit as st
import urllib.parse

def generate_bookmarklet():
    # Primero definimos el código JavaScript
    js_code = """(function(){
        // Crear el formulario principal
        var d = document.createElement('div');
        d.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:1px solid #ccc;border-radius:8px;z-index:9999;box-shadow:0 2px 10px rgba(0,0,0,0.2);font-family:Arial,sans-serif;width:600px;max-height:90vh;overflow-y:auto';
        
        // Array para almacenar las imágenes seleccionadas
        var selectedImages = new Set();
        
        // Función para seleccionar imágenes
        window.enableImageSelection = function() {
            document.querySelectorAll('img').forEach(img => {
                if (img.width > 100 && img.height > 100) {
                    img.style.cursor = 'pointer';
                    img.style.transition = 'all 0.2s';
                    img.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        if (this.style.border === '2px solid red') {
                            this.style.border = '';
                            this.style.boxShadow = 'none';
                            selectedImages.delete(this.src);
                        } else {
                            this.style.border = '2px solid red';
                            this.style.boxShadow = '0 0 8px rgba(255,0,0,0.3)';
                            selectedImages.add(this.src);
                        }
                        updateImagePreview();
                    };
                    
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
                }
            });
        };
        
        // Función para actualizar la vista previa de imágenes
        function updateImagePreview() {
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = Array.from(selectedImages).map(url => 
                `<img src="${url}" style="height:50px;margin:2px;border:1px solid #ccc;">`
            ).join('');
            document.getElementById('selectedCount').textContent = selectedImages.size;
        }
        
        d.innerHTML = `
            <h3 style="margin:0 0 15px">Guardar Propiedad</h3>
            <form id="propertyForm" style="display:flex;flex-direction:column;gap:15px">
                <div>
                    <label>URL:</label>
                    <input type="text" name="url" value="${window.location.href}" readonly style="width:100%;padding:5px">
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                    <div>
                        <label>Precio:</label>
                        <input type="text" name="price" required style="width:100%;padding:5px">
                    </div>
                    <div>
                        <label>Ubicación:</label>
                        <input type="text" name="location" required style="width:100%;padding:5px">
                    </div>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
                    <div>
                        <label>Habitaciones:</label>
                        <input type="number" name="rooms" min="0" style="width:100%;padding:5px">
                    </div>
                    <div>
                        <label>Baños:</label>
                        <input type="number" name="bathrooms" min="0" step="0.5" style="width:100%;padding:5px">
                    </div>
                    <div>
                        <label>Niveles:</label>
                        <input type="number" name="levels" min="0" style="width:100%;padding:5px">
                    </div>
                </div>
                <div>
                    <label>Descripción:</label>
                    <textarea name="description" required style="width:100%;height:80px;padding:5px"></textarea>
                </div>
                <div>
                    <label>Datos del vendedor:</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
                        <input type="text" name="agent_name" placeholder="Nombre" style="width:100%;padding:5px">
                        <input type="text" name="agent_phone" placeholder="Teléfono" style="width:100%;padding:5px">
                    </div>
                    <input type="email" name="agent_email" placeholder="Email" style="width:100%;padding:5px;margin-top:5px">
                </div>
                <div>
                    <label>Imágenes: <span id="selectedCount">0</span> seleccionadas</label>
                    <button type="button" onclick="window.enableImageSelection()" style="width:100%;padding:10px;margin:5px 0;background:#2196F3;color:white;border:none;border-radius:4px;cursor:pointer">
                        Seleccionar imágenes
                    </button>
                    <div id="imagePreview" style="max-height:100px;overflow-y:auto;padding:5px;border:1px solid #ccc;margin:5px 0;display:flex;flex-wrap:wrap;gap:5px"></div>
                </div>
                <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:10px">
                    <button type="submit" style="padding:10px 20px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer">Guardar</button>
                    <button type="button" onclick="this.closest('div').parentElement.parentElement.remove()" style="padding:10px 20px;background:#f44336;color:white;border:none;border-radius:4px;cursor:pointer">Cancelar</button>
                </div>
            </form>
        `;
        
        document.body.appendChild(d);
        
        document.getElementById('propertyForm').onsubmit = async function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = {
                url: formData.get('url'),
                price: formData.get('price'),
                location: formData.get('location'),
                description: formData.get('description'),
                rooms: formData.get('rooms'),
                bathrooms: formData.get('bathrooms'),
                levels: formData.get('levels'),
                agent: {
                    name: formData.get('agent_name'),
                    phone: formData.get('agent_phone'),
                    email: formData.get('agent_email')
                },
                images: Array.from(selectedImages),
                features: {}
            };
            
            try {
                const response = await fetch('https://hoomextractor.online/api/properties', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                if (response.ok) {
                    alert('Propiedad guardada exitosamente');
                    d.remove();
                } else {
                    throw new Error('Error al guardar la propiedad');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        };
    })();"""

    # Minificar el código y asegurarnos que esté bien formado
    minified = js_code.strip().replace('\n', ' ').replace('    ', '')
    
    # Retornar el bookmarklet con el prefijo javascript:
    return f"javascript:{minified}"

def main():
    # Forzar UTF-8 en la página
    st.set_page_config(
        page_title="Configuración",
        page_icon="⚙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("⚙️ Configuración")
    
    # Sección del Bookmarklet
    st.header("🔖 Bookmarklet")
    st.markdown("""
        El bookmarklet es una herramienta que te permite guardar propiedades 
        directamente desde cualquier sitio web inmobiliario.
    """)
    
    # Código del bookmarklet
    bookmarklet_code = generate_bookmarklet()
    
    # Generar el href para el bookmarklet (sin espacios ni saltos de línea)
    bookmarklet_href = bookmarklet_code.strip().replace('\n', '').replace('    ', '')
    
    # Mostrar el código completo para copiar
    st.code(bookmarklet_code, language="javascript")
    
    if st.button("📋 Copiar Código"):
        st.toast("¡Código copiado!")
    
    st.markdown("""
    2. **Agregar a los marcadores:**
        - Haz clic derecho en la barra de marcadores de tu navegador
        - Selecciona "Añadir marcador" o "Nuevo marcador"
        - En el campo "Nombre" escribe: "Guardar Propiedad"
        - En el campo "URL" pega el código que copiaste
        - Guarda el marcador
        
    3. **Alternativa: Arrastrar y soltar**
        - También puedes arrastrar directamente este botón a tu barra de marcadores:
    """)
    
    # Enlace para arrastrar
    st.markdown(f'<a href="{bookmarklet_href}" class="bookmarklet">🏠 Guardar Propiedad</a>', unsafe_allow_html=True)
    
    # Instrucciones de uso
    st.subheader("📝 Cómo usar")
    st.markdown("""
    1. **Navega a una propiedad:**
        - Ve a cualquier sitio web inmobiliario
        - Encuentra una propiedad que te interese
        
    2. **Guarda la propiedad:**
        - Haz clic en el marcador "Guardar Propiedad"
        - Se abrirá un formulario con la información detectada
        - Revisa y ajusta los datos si es necesario
        - Haz clic en "Guardar"
        
    3. **Gestiona tus propiedades:**
        - Todas las propiedades guardadas aparecerán en la página principal
        - Puedes editarlas, eliminarlas o agregar notas
    """)
    
    # Agregar estilo para el enlace del bookmarklet
    st.markdown("""
    <style>
    .bookmarklet {
        display: inline-block;
        padding: 8px 16px;
        background-color: #f0f2f6;
        border-radius: 4px;
        color: #262730;
        text-decoration: none;
        margin: 10px 0;
        border: 1px solid #ccc;
    }
    .bookmarklet:hover {
        background-color: #e0e2e6;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 