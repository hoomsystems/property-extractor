import streamlit as st
import urllib.parse
import re
import json

def minify_js(code):
    # Eliminar comentarios y espacios en blanco
    code = re.sub(r'\s*//.*?\n', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'\s+', ' ', code)
    
    # Eliminar espacios alrededor de operadores y puntuación
    code = re.sub(r'\s*([=+\-*/<>!&|,{}()[\];:])\s*', r'\1', code)
    
    # Eliminar espacios después de palabras clave
    code = re.sub(r'\b(var|function|if|else|return|new|for|while|do|switch|case|try|catch|finally)\s+', r'\1', code)
    
    # Eliminar espacios innecesarios en strings template literals
    code = re.sub(r'`\s+', '`', code)
    code = re.sub(r'\s+`', '`', code)
    
    return code.strip()

def generate_bookmarklet():
    return """javascript:(function(){
        // Función para extraer texto limpio
        function getText(selector) {
            var el = document.querySelector(selector);
            return el ? el.textContent.trim() : '';
        }
        
        // Función para extraer números de un texto
        function getNumber(text) {
            var match = text.match(/\\d+(\\.\\d+)?/);
            return match ? match[0] : '';
        }
        
        // Detectar datos básicos
        var data = {
            title: document.title,
            description: getText('meta[name="description"]') || getText('[class*="description"],[class*="Description"]'),
            rooms: getNumber(getText('[class*="room"],[class*="Room"],[class*="recamara"],[class*="Recamara"]')),
            bathrooms: getNumber(getText('[class*="bath"],[class*="Bath"],[class*="baño"],[class*="Baño"]')),
            construction: getNumber(getText('[class*="construction"],[class*="Construction"],[class*="construc"],[class*="Construc"]')),
            land: getNumber(getText('[class*="land"],[class*="Land"],[class*="terreno"],[class*="Terreno"]')),
            location: getText('[class*="location"],[class*="Location"],[class*="ubicacion"],[class*="Ubicacion"],[class*="address"],[class*="Address"]'),
            url: window.location.href
        };
        
        // Crear formulario
        var form = document.createElement('div');
        form.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.2);z-index:9999;width:400px;font-family:Arial';
        
        form.innerHTML = `
            <h3 style="margin:0 0 15px">Guardar Propiedad</h3>
            <form id="propertyForm">
                <div style="margin-bottom:10px">
                    <label>Título:</label>
                    <input type="text" name="title" value="${data.title}" style="width:100%;padding:5px">
                </div>
                <div style="margin-bottom:10px">
                    <label>Ubicación:</label>
                    <input type="text" name="location" value="${data.location}" style="width:100%;padding:5px">
                </div>
                <div style="margin-bottom:10px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
                    <div>
                        <label>Recámaras:</label>
                        <input type="number" name="rooms" value="${data.rooms}" style="width:100%;padding:5px">
                    </div>
                    <div>
                        <label>Baños:</label>
                        <input type="number" name="bathrooms" value="${data.bathrooms}" style="width:100%;padding:5px">
                    </div>
                </div>
                <div style="margin-bottom:10px;display:grid;grid-template-columns:1fr 1fr;gap:10px">
                    <div>
                        <label>M² Construcción:</label>
                        <input type="number" name="construction" value="${data.construction}" style="width:100%;padding:5px">
                    </div>
                    <div>
                        <label>M² Terreno:</label>
                        <input type="number" name="land" value="${data.land}" style="width:100%;padding:5px">
                    </div>
                </div>
                <div style="margin-bottom:10px">
                    <label>Descripción:</label>
                    <textarea name="description" style="width:100%;height:80px;padding:5px">${data.description}</textarea>
                </div>
                <div style="display:flex;gap:10px;justify-content:flex-end">
                    <button type="submit" style="padding:8px 20px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer">
                        Guardar
                    </button>
                    <button type="button" onclick="this.closest('div').remove()" style="padding:8px 20px;background:#f44336;color:white;border:none;border-radius:4px;cursor:pointer">
                        Cancelar
                    </button>
                </div>
            </form>
        `;
        
        document.body.appendChild(form);
        
        document.getElementById('propertyForm').onsubmit = function(e) {
            e.preventDefault();
            var formData = new FormData(e.target);
            var data = {
                title: formData.get('title'),
                location: formData.get('location'),
                rooms: formData.get('rooms'),
                bathrooms: formData.get('bathrooms'),
                construction: formData.get('construction'),
                land: formData.get('land'),
                description: formData.get('description'),
                url: window.location.href
            };
            
            fetch('https://hoomextractor.online/api/properties', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(function(r) {
                if(r.ok) {
                    alert('Propiedad guardada');
                    form.remove();
                } else {
                    throw new Error('Error al guardar');
                }
            })
            .catch(function(e) {
                alert('Error: ' + e.message);
            });
        };
    })();"""

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
    
    # Para mostrar el código sin codificar (para depuración)
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
    st.markdown(f'<a href="{bookmarklet_code}" class="bookmarklet">🏠 Guardar Propiedad</a>', unsafe_allow_html=True)
    
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