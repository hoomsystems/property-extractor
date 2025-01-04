import streamlit as st

def main():
    st.title("⚙️ Configuración")
    
    # Sección del Bookmarklet
    st.header("🔖 Bookmarklet")
    st.markdown("""
        El bookmarklet es una herramienta que te permite guardar propiedades 
        directamente desde cualquier sitio web inmobiliario.
    """)
    
    # Código del bookmarklet
    bookmarklet_code = """javascript:(function(){
        var s = document.createElement('script');
        s.type = 'text/javascript';
        s.charset = 'UTF-8';
        document.characterSet = 'UTF-8';  // Forzar UTF-8 en el documento
        s.src = 'https://hoomextractor.online/static/collector.js';
        s.onload = function() {
            if (typeof detectImages === 'undefined') {
                console.error('Error: collector.js no se cargó correctamente');
            } else {
                console.log('Iniciando extractor de propiedades...');
                try {
                    createPopup();
                } catch (e) {
                    console.error('Error al crear popup:', e);
                }
            }
        };
        s.onerror = function(e) {
            console.error('Error al cargar collector.js:', e);
        };
        document.body.appendChild(s);
    })();"""
    
    # Eliminar saltos de línea y espacios para el href
    bookmarklet_href = bookmarklet_code.replace('\n', '').replace(' ', '')
    
    # Instrucciones de instalación
    st.subheader("📥 Instalación")
    st.markdown("""
    1. **Copiar el código del bookmarklet:**
    """)
    
    # Mostrar el código para copiar
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