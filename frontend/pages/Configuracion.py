import streamlit as st
import urllib.parse

def generate_bookmarklet():
    return """javascript:(function(){
        console.log('Iniciando bookmarklet');
        var script = document.createElement('script');
        script.src = 'https://hoomextractor.online/static/collector.js';
        script.onload = function() {
            console.log('Script cargado');
            
            // Definir las funciones de manejo
            window.startAutomatic = function() {
                const images = detectImages();
                if (images && images.length > 0) {
                    showPropertyForm(images);
                } else {
                    alert('No se encontraron imágenes');
                }
            };
            
            window.startManual = function() {
                manualImageSelection();
            };
            
            // Crear el popup inicial
            const popup = document.createElement('div');
            popup.style.cssText = 'position:fixed;top:20px;right:20px;background:white;padding:20px;border:1px solid black;z-index:9999;box-shadow:0 2px 5px rgba(0,0,0,0.2);';
            popup.innerHTML = `
                <h3>Seleccionar Imágenes</h3>
                <button onclick="startAutomatic()">Detección Automática</button>
                <button onclick="startManual()">Selección Manual</button>
                <button onclick="this.parentElement.remove()">Cancelar</button>
            `;
            document.body.appendChild(popup);
        };
        
        script.onerror = function(e) {
            console.error('Error cargando script:', e);
            alert('Error cargando el script');
        };
        
        document.body.appendChild(script);
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
    
    # Código del bookmarklet con codificación explícita
    bookmarklet_code = generate_bookmarklet()
    
    # Generar el href para el bookmarklet
    bookmarklet_href = f"javascript:{urllib.parse.quote(bookmarklet_code)}"
    
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