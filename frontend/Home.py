import streamlit as st
import requests

st.set_page_config(
    page_title="Hoom Extractor",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Propiedades Guardadas")

try:
    response = requests.get("https://hoomextractor.online/api/properties")
    if response.ok:
        properties = response.json()
        for prop in properties:
            with st.expander(f"{prop['title']} - {prop['location']}"):
                cols = st.columns(3)
                with cols[0]:
                    st.write("**Recámaras:**", prop.get('rooms', 'N/A'))
                    st.write("**Baños:**", prop.get('bathrooms', 'N/A'))
                with cols[1]:
                    st.write("**Construcción:**", f"{prop.get('construction', 'N/A')} m²")
                    st.write("**Terreno:**", f"{prop.get('land', 'N/A')} m²")
                with cols[2]:
                    st.write("**URL:**", prop['url'])
                st.write("**Descripción:**", prop['description'])
except Exception as e:
    st.error(f"Error al cargar las propiedades: {str(e)}") 