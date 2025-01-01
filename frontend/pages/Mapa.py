import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import pandas as pd

def main():
    st.title("🗺️ Mapa de Propiedades")
    
    # Obtener todas las propiedades
    try:
        response = requests.get("http://localhost:8000/api/properties")
        if response.ok:
            data = response.json()
            properties = data["items"]
            
            # Crear mapa centrado en México
            m = folium.Map(location=[23.6345, -102.5528], zoom_start=5)
            
            # Agregar marcadores para propiedades con coordenadas
            for prop in properties:
                if prop.get('latitude') and prop.get('longitude'):
                    # Formatear el popup con información de la propiedad
                    popup_html = f"""
                        <b>{prop['title']}</b><br>
                        Precio: {prop['price']}<br>
                        <a href="/?property={prop['id']}" target="_self">Ver detalles</a>
                    """
                    
                    folium.Marker(
                        [prop['latitude'], prop['longitude']],
                        popup=popup_html,
                        tooltip=prop['title']
                    ).add_to(m)
            
            # Mostrar el mapa
            st_folium(m, width=800, height=600)
            
            # Propiedades sin ubicación
            st.subheader("Propiedades sin ubicación en el mapa")
            unmapped = [p for p in properties if not (p.get('latitude') and p.get('longitude'))]
            if unmapped:
                for prop in unmapped:
                    with st.expander(prop['title']):
                        st.write(f"Ubicación: {prop['location']}")
                        if st.button("Agregar al mapa", key=f"map_{prop['id']}"):
                            st.session_state.mapping_property = prop['id']
                            st.rerun()
            
            # Formulario para agregar ubicación
            if 'mapping_property' in st.session_state:
                prop_id = st.session_state.mapping_property
                prop = next((p for p in properties if p['id'] == prop_id), None)
                
                if prop:
                    st.subheader(f"Agregar ubicación para: {prop['title']}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        lat = st.number_input("Latitud", value=23.6345, format="%.6f")
                    with col2:
                        lon = st.number_input("Longitud", value=-102.5528, format="%.6f")
                    
                    # Mostrar mapa para selección
                    select_map = folium.Map(location=[lat, lon], zoom_start=15)
                    folium.Marker([lat, lon]).add_to(select_map)
                    st_folium(select_map, width=800, height=400)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Guardar ubicación"):
                            try:
                                response = requests.put(
                                    f"http://localhost:8000/api/properties/{prop_id}",
                                    json={
                                        **prop,
                                        "latitude": lat,
                                        "longitude": lon
                                    }
                                )
                                if response.ok:
                                    st.success("Ubicación guardada")
                                    del st.session_state.mapping_property
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {str(e)}")
                    
                    with col2:
                        if st.button("❌ Cancelar"):
                            del st.session_state.mapping_property
                            st.rerun()
                            
    except Exception as e:
        st.error(f"Error al cargar las propiedades: {str(e)}")

if __name__ == "__main__":
    main() 