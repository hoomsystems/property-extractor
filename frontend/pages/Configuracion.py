import streamlit as st
import urllib.parse

def generate_bookmarklet():
    return """javascript:(function(){
        console.log('Iniciando bookmarklet');
        var s=document.createElement('script');
        s.src='https://hoomextractor.online/static/collector.js';
        s.onload=function(){
            if(!window.manualImageSelection || !window.detectImages || !window.showPropertyForm){
                console.error('Funciones no encontradas:', {
                    manualImageSelection: !!window.manualImageSelection,
                    detectImages: !!window.detectImages,
                    showPropertyForm: !!window.showPropertyForm
                });
                alert('Error: No se pudo cargar el script correctamente');
                return;
            }
            var d=document.createElement('div');
            d.style.cssText='position:fixed;top:20px;right:20px;background:white;padding:20px;border:1px solid #ccc;border-radius:8px;z-index:9999;box-shadow:0 2px 10px rgba(0,0,0,0.2);font-family:Arial,sans-serif';
            var b='display:block;width:100%;margin:8px 0;padding:10px;border:none;border-radius:4px;font-size:14px;cursor:pointer;color:white';
            d.innerHTML='<h3 style="margin:0 0 15px 0;font-size:16px">Seleccionar Imágenes</h3>'+
                '<button onclick="window.startAutomatic()" style="'+b+';background:#4CAF50">Detección Automática</button>'+
                '<button onclick="window.startManual()" style="'+b+';background:#2196F3">Selección Manual</button>'+
                '<button onclick="this.parentElement.remove()" style="'+b+';background:#f44336">Cancelar</button>';
            document.body.appendChild(d);
        };
        s.onerror=function(e){
            console.error('Error cargando script:', e);
            alert('Error cargando el script. Por favor intente de nuevo.');
        };
        document.body.appendChild(s);
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
    
    # Generar el href para el bookmarklet (sin codificar)
    bookmarklet_href = bookmarklet_code
    
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
    
    # Enlace para arrastrar (usar el código directamente)
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