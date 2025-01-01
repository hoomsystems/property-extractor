import streamlit as st
import requests
from datetime import datetime

def main():
    st.title("📋 Catálogo de Vendedores")
    
    # Botón para agregar nuevo vendedor
    if st.button("➕ Agregar Nuevo Vendedor"):
        st.session_state.adding_vendor = True
    
    # Formulario para agregar/editar vendedor
    if getattr(st.session_state, 'adding_vendor', False):
        with st.form("new_vendor_form"):
            st.subheader("Nuevo Vendedor")
            name = st.text_input("Nombre de la Inmobiliaria")
            internal_contact = st.text_input("Persona de Contacto")
            phone = st.text_input("Teléfono")
            email = st.text_input("Email")
            website = st.text_input("Sitio Web")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Guardar"):
                    try:
                        response = requests.post(
                            "http://localhost:8000/api/agents",
                            json={
                                "name": name,
                                "internal_contact": internal_contact,
                                "phone": phone,
                                "email": email,
                                "website": website
                            }
                        )
                        if response.ok:
                            st.success("Vendedor agregado exitosamente")
                            st.session_state.adding_vendor = False
                            st.rerun()
                        else:
                            st.error("Error al guardar el vendedor")
                    except Exception as e:
                        st.error(f"Error de conexión: {str(e)}")
            
            with col2:
                if st.form_submit_button("❌ Cancelar"):
                    st.session_state.adding_vendor = False
                    st.rerun()
    
    # Lista de vendedores
    try:
        response = requests.get("http://localhost:8000/api/agents")
        if response.ok:
            vendors = response.json()
            
            for vendor in vendors:
                with st.container():
                    st.markdown("""
                        <style>
                        .vendor-card {
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 15px;
                            margin: 10px 0;
                            background-color: white;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f'<div class="vendor-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"### 🏢 {vendor['name']}")
                        if vendor.get('internal_contact'):
                            st.markdown(f"👤 **Contacto:** {vendor['internal_contact']}")
                        if vendor.get('phone'):
                            st.markdown(f"📞 {vendor['phone']}")
                        if vendor.get('email'):
                            st.markdown(f"📧 {vendor['email']}")
                        if vendor.get('website'):
                            st.markdown(f"🌐 [{vendor['website']}]({vendor['website']})")
                    
                    with col2:
                        if st.button("✏️ Editar", key=f"edit_{vendor['id']}"):
                            st.session_state.editing_vendor = vendor['id']
                        
                        if st.button("🗑️ Eliminar", key=f"delete_{vendor['id']}"):
                            if st.warning("¿Estás seguro de eliminar este vendedor?"):
                                try:
                                    delete_response = requests.delete(
                                        f"http://localhost:8000/api/agents/{vendor['id']}"
                                    )
                                    if delete_response.ok:
                                        st.success("Vendedor eliminado")
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Error al eliminar: {str(e)}")
                    
                    # Formulario de edición si está activo
                    if getattr(st.session_state, 'editing_vendor', None) == vendor['id']:
                        with st.form(key=f"edit_form_{vendor['id']}"):
                            edited_name = st.text_input("Nombre", value=vendor['name'])
                            edited_internal_contact = st.text_input("Persona de Contacto", value=vendor.get('internal_contact', ''))
                            edited_phone = st.text_input("Teléfono", value=vendor.get('phone', ''))
                            edited_email = st.text_input("Email", value=vendor.get('email', ''))
                            edited_website = st.text_input("Sitio Web", value=vendor.get('website', ''))
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Guardar cambios"):
                                    try:
                                        response = requests.put(
                                            f"http://localhost:8000/api/agents/{vendor['id']}",
                                            json={
                                                "name": edited_name,
                                                "internal_contact": edited_internal_contact,
                                                "phone": edited_phone,
                                                "email": edited_email,
                                                "website": edited_website
                                            }
                                        )
                                        if response.ok:
                                            st.success("Cambios guardados")
                                            del st.session_state.editing_vendor
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al guardar: {str(e)}")
                            
                            with col2:
                                if st.form_submit_button("❌ Cancelar"):
                                    del st.session_state.editing_vendor
                                    st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Error al cargar los vendedores")
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")

if __name__ == "__main__":
    main() 