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
    # Obtener el código JavaScript
    js_code = """(function(){
        // ... tu código JavaScript actual ...
    })();"""
    
    # Minificar el código
    minified = minify_js(js_code)
    
    # Codificar caracteres especiales
    encoded = urllib.parse.quote(minified)
    
    # Retornar el bookmarklet
    return f"javascript:{encoded}"

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