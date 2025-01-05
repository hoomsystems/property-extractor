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
    js_code = """javascript:(function(){
        var popup=document.createElement('div');
        popup.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border-radius:8px;box-shadow:0 2px 10px rgba(0,0,0,0.2);z-index:9999;width:600px;max-height:90vh;overflow-y:auto;font-family:Arial';
        var selectedImages=new Set();
        
        window.startImageSelection=function(){
            document.querySelectorAll('img').forEach(function(img){
                if(img.width>100&&img.height>100){
                    img.style.cursor='pointer';
                    img.onclick=function(e){
                        e.preventDefault();
                        e.stopPropagation();
                        if(this.style.border==='2px solid red'){
                            this.style.border='';
                            selectedImages.delete(this.src);
                        }else{
                            this.style.border='2px solid red';
                            selectedImages.add(this.src);
                        }
                        updatePreview();
                    }
                }
            });
        };
        
        function updatePreview(){
            var preview=document.getElementById('imagePreview');
            var images=Array.from(selectedImages);
            preview.innerHTML=images.map(function(url){
                return '<div style="display:inline-block;margin:2px;position:relative">'+
                    '<img src="'+url+'" height="50" style="border:1px solid #ccc">'+
                    '<div style="position:absolute;top:0;right:0;background:rgba(0,0,0,0.5);color:white;padding:2px 5px;font-size:10px">'+
                    (url.split('/').pop()||'').substring(0,10)+'...</div></div>';
            }).join('');
            document.getElementById('imageCount').textContent=images.length;
        }
        
        popup.innerHTML='<h3 style="margin:0 0 15px">Guardar Propiedad</h3>'+
            '<form id="propertyForm">'+
            '<div style="margin-bottom:10px"><label>Precio:</label><input type="text" name="price" style="width:100%;padding:5px" required></div>'+
            '<div style="margin-bottom:10px"><label>Ubicación:</label><input type="text" name="location" style="width:100%;padding:5px" required></div>'+
            '<div style="margin-bottom:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">'+
            '<div><label>Habitaciones:</label><input type="number" name="rooms" min="0" style="width:100%;padding:5px"></div>'+
            '<div><label>Baños:</label><input type="number" name="bathrooms" min="0" step="0.5" style="width:100%;padding:5px"></div>'+
            '<div><label>Niveles:</label><input type="number" name="levels" min="0" style="width:100%;padding:5px"></div>'+
            '</div>'+
            '<div style="margin-bottom:10px"><label>Descripción:</label><textarea name="description" style="width:100%;height:80px;padding:5px" required></textarea></div>'+
            '<div style="margin-bottom:10px">'+
            '<label>Datos del vendedor:</label>'+
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:5px">'+
            '<input type="text" name="agent_name" placeholder="Nombre" style="width:100%;padding:5px">'+
            '<input type="text" name="agent_phone" placeholder="Teléfono" style="width:100%;padding:5px">'+
            '</div>'+
            '<input type="email" name="agent_email" placeholder="Email" style="width:100%;padding:5px;margin-top:5px">'+
            '</div>'+
            '<div style="margin-bottom:10px">'+
            '<label>Imágenes (<span id="imageCount">0</span>):</label>'+
            '<button type="button" onclick="startImageSelection()" style="width:100%;padding:8px;margin:5px 0;background:#2196F3;color:white;border:none;border-radius:4px;cursor:pointer">Seleccionar imágenes</button>'+
            '<div id="imagePreview" style="max-height:100px;overflow-y:auto;padding:5px;border:1px solid #ccc;display:flex;flex-wrap:wrap;gap:5px"></div>'+
            '</div>'+
            '<div style="display:flex;gap:10px;justify-content:flex-end">'+
            '<button type="submit" style="padding:8px 20px;background:#4CAF50;color:white;border:none;border-radius:4px;cursor:pointer">Guardar</button>'+
            '<button type="button" onclick="this.closest(\'form\').parentElement.remove()" style="padding:8px 20px;background:#f44336;color:white;border:none;border-radius:4px;cursor:pointer">Cancelar</button>'+
            '</div>'+
            '</form>';
        
        document.body.appendChild(popup);
        
        document.getElementById('propertyForm').onsubmit=function(e){
            e.preventDefault();
            var formData=new FormData(e.target);
            var data={
                url:window.location.href,
                price:formData.get('price'),
                location:formData.get('location'),
                description:formData.get('description'),
                rooms:formData.get('rooms'),
                bathrooms:formData.get('bathrooms'),
                levels:formData.get('levels'),
                agent:{
                    name:formData.get('agent_name'),
                    phone:formData.get('agent_phone'),
                    email:formData.get('agent_email')
                },
                images:Array.from(selectedImages),
                features:{}
            };
            
            fetch('https://hoomextractor.online/api/properties',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify(data)
            }).then(function(r){
                if(r.ok){alert('Guardado');popup.remove()}
                else{throw new Error('Error al guardar')}
            }).catch(function(e){alert('Error: '+e.message)});
            return false;
        };
    })();"""
    
    # Minificar el código
    return js_code.strip()

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