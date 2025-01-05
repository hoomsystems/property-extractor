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
        var url = window.location.href;
        var form = document.createElement('div');
        form.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.2);z-index:9999;width:300px;font-family:Arial';
        
        form.innerHTML = `
            <h3 style="margin:0 0 15px">Extraer Propiedad</h3>
            <p>¿Desea extraer la información de esta propiedad?</p>
            <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:20px">
                <button onclick="window.extractProperty('${url}')" style="padding:8px 20px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer">
                    Extraer
                </button>
                <button onclick="this.closest('div').remove()" style="padding:8px 20px;background:#f44336;color:white;border:none;border-radius:4px;cursor:pointer">
                    Cancelar
                </button>
            </div>
        `;
        
        window.extractProperty = async function(url) {
            try {
                const response = await fetch('https://hoomextractor.online/api/scrape?url=' + encodeURIComponent(url));
                const data = await response.json();
                if (data.status === 'success') {
                    alert('Información extraída exitosamente');
                    form.remove();
                } else {
                    throw new Error('Error al extraer información');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        };
        
        document.body.appendChild(form);
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