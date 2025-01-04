import streamlit as st
import requests
from datetime import datetime
import folium
import streamlit_folium
import os

# Obtener la URL del backend desde las variables de entorno
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://138.197.189.34:8000")

def main():
    st.title("🏠 Property Collector")
    
    # Sidebar para filtros
    with st.sidebar:
        st.header("Filtros")
        search = st.text_input("Buscar por título o notas")
        
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Precio mínimo", min_value=0)
        with col2:
            max_price = st.number_input("Precio máximo", min_value=0)
        
        location = st.text_input("Ubicación")
        
        sort_by = st.selectbox(
            "Ordenar por",
            options=[
                "date_desc", "date_asc",
                "price_desc", "price_asc"
            ],
            format_func=lambda x: {
                "date_desc": "Más recientes",
                "date_asc": "Más antiguos",
                "price_desc": "Mayor precio",
                "price_asc": "Menor precio"
            }[x]
        )
        
        if st.button("Aplicar filtros"):
            st.session_state.filters = {
                "search": search,
                "min_price": min_price,
                "max_price": max_price,
                "location": location,
                "sort_by": sort_by
            }
    
    # Contenido principal
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        st.subheader("Propiedades guardadas")
    with col2:
        items_per_page = st.selectbox("Items por página", [10, 20, 50], key="per_page")
    with col3:
        page = st.number_input("Página", min_value=1, value=1, key="current_page")
    
    # Obtener y mostrar propiedades
    try:
        # Agregar logs para depuración
        st.write("Intentando obtener propiedades...")
        
        filters = getattr(st.session_state, 'filters', {})
        response = requests.get(
            f"{BACKEND_URL}/properties",
            params={
                "page": page,
                "per_page": items_per_page,
                **filters
            }
        )
        

        # Agregar logs de la respuesta
        st.write(f"Status code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            st.write(f"Total de propiedades encontradas: {data['total_items']}")
            
            if not data["items"]:
                st.warning("No se encontraron propiedades.")
                return
            
            # Mostrar propiedades en cards
            for property in data["items"]:
                # Crear un contenedor con bordes y padding
                with st.container():
                    st.markdown("""
                        <style>
                        .property-summary {
                            border: 1px solid #ddd;
                            border-radius: 10px;
                            padding: 10px;
                            margin: 10px 0;
                            background-color: white;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    with st.container():
                        st.markdown('<div class="property-summary">', unsafe_allow_html=True)
                        
                        # Crear dos columnas: una para la imagen y otra para la información
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            # Mostrar imagen principal o primera imagen disponible
                            if property.get('main_image'):
                                st.image(property['main_image'], width=150)
                            elif property.get('images'):
                                st.image(property['images'][0], width=150)
                        
                        with col2:
                            # Título como enlace expandible
                            if st.button(f"📍 {property['title']}", key=f"expand_{property['id']}"):
                                st.session_state.expanded_property = property['id']
                            
                            # Crear una fila para precio, recámaras y baños
                            feat_cols = st.columns(3)
                            
                            with feat_cols[0]:
                                # Formatear precio
                                price = property['price']
                                if isinstance(price, (int, float)) or (isinstance(price, str) and price.replace(',', '').isdigit()):
                                    try:
                                        price_value = float(str(price).replace(',', ''))
                                        formatted_price = "${:,.0f}".format(price_value)
                                    except:
                                        formatted_price = price
                                else:
                                    formatted_price = price
                                st.markdown(f"💰 **{formatted_price}**")
                            
                            with feat_cols[1]:
                                if property.get('bedrooms'):
                                    st.markdown(f"🛏️ **{property['bedrooms']} rec**")
                                else:
                                    st.markdown("🛏️ **--**")
                            
                            with feat_cols[2]:
                                if property.get('bathrooms'):
                                    st.markdown(f"🚿 **{property['bathrooms']} baños**")
                                else:
                                    st.markdown("🚿 **--**")
                            
                            # Información del vendedor si existe
                            if property.get('agent'):
                                agent = property['agent']
                                agent_info = []
                                
                                if agent.get('name'):
                                    agent_info.append(f"👤 {agent['name']}")
                                if agent.get('phone'):
                                    agent_info.append(f"📞 {agent['phone']}")
                                if agent.get('email'):
                                    agent_info.append(f"📧 {agent['email']}")
                                
                                if agent_info:
                                    st.markdown(" | ".join(agent_info))
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Si la propiedad está expandida, mostrar todos los detalles
                if getattr(st.session_state, 'expanded_property', None) == property['id']:
                    with st.expander("Detalles completos", expanded=True):
                        # Formatear precio primero
                        price = property['price']
                        if isinstance(price, (int, float)) or (isinstance(price, str) and price.replace(',', '').isdigit()):
                            try:
                                price_value = float(str(price).replace(',', ''))
                                formatted_price = "${:,.0f}".format(price_value)
                            except:
                                formatted_price = price
                        else:
                            formatted_price = price

                        # Contenedor para imagen principal y título
                        header_cols = st.columns([1, 2])
                        
                        with header_cols[0]:
                            # Mostrar imagen principal si existe
                            if property.get('main_image'):
                                st.image(property['main_image'], use_container_width=True)
                            elif property.get('images'):
                                st.image(property['images'][0], use_container_width=True)
                        
                        with header_cols[1]:
                            # Título principal
                            st.markdown(f"### {property['title']}")
                            # Mostrar solo la fecha
                            fecha = datetime.fromisoformat(property['date'].replace('Z', '+00:00'))
                            fecha_formateada = fecha.strftime("%d/%m/%Y %H:%M")
                            st.markdown(f"**Fecha de guardado:** {fecha_formateada}")
                        
                        # Contenedor principal para el resto de la información
                        main_cols = st.columns([2, 1])
                        
                        with main_cols[0]:
                            # Información principal
                            st.markdown("#### Detalles de la Propiedad")
                            
                            # Formatear precio
                            price = property['price']
                            if isinstance(price, (int, float)) or (isinstance(price, str) and price.replace(',', '').isdigit()):
                                try:
                                    price_value = float(str(price).replace(',', ''))
                                    formatted_price = "${:,.0f}".format(price_value)
                                except:
                                    formatted_price = price
                            else:
                                formatted_price = price
                                
                            st.markdown(f"**Precio:** {formatted_price}")
                            st.markdown(f"**Ubicación:** {property['location']}")
                            
                            # Características numéricas
                            features_cols = st.columns(2)
                            with features_cols[0]:
                                if property.get('construction_size'):
                                    st.markdown(f"**Construcción:** {property['construction_size']} m²")
                                if property.get('lot_size'):
                                    st.markdown(f"**Terreno:** {property['lot_size']} m²")
                                if property.get('bathrooms'):
                                    st.markdown(f"**Baños:** {property['bathrooms']}")
                            
                            with features_cols[1]:
                                if property.get('bedrooms'):
                                    st.markdown(f"**Recámaras:** {property['bedrooms']}")
                                if property.get('parking_spaces'):
                                    st.markdown(f"**Estacionamientos:** {property['parking_spaces']}")
                                if property.get('floors'):
                                    st.markdown(f"**Niveles:** {property['floors']}")
                            
                            # Descripción de la propiedad
                            if property.get('description'):
                                st.markdown("#### Descripción")
                                st.markdown(property['description'])
                            
                            # Información del agente si existe
                            if property.get('agent'):
                                st.markdown("#### Información del Agente")
                                agent = property['agent']
                                if agent.get('name'):
                                    st.markdown(f"**Nombre:** {agent['name']}")
                                if agent.get('phone'):
                                    st.markdown(f"**Teléfono:** {agent['phone']}")
                                if agent.get('email'):
                                    st.markdown(f"**Email:** {agent['email']}")
                            
                            # Notas
                            if property.get('notes'):
                                st.markdown("#### Notas")
                                st.markdown(property['notes'])
                        
                        with main_cols[1]:
                            # Acciones
                            st.markdown("#### Acciones")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if property['id'] == getattr(st.session_state, 'editing_property', None):
                                    if st.button("❌ Cancelar edición", key=f"edit_{property['id']}"):
                                        del st.session_state.editing_property
                                        st.rerun()
                                else:
                                    if st.button("✏️ Editar", key=f"edit_{property['id']}"):
                                        st.session_state.editing_property = property['id']
                                        st.rerun()
                            
                            with col2:
                                if st.button("🗑️ Eliminar", key=f"delete_{property['id']}"):
                                    try:
                                        response = requests.delete(
                                            f"{BACKEND_URL}/properties/{property['id']}"
                                        )
                                        if response.ok:
                                            st.success("Propiedad eliminada")
                                            st.rerun()
                                    except Exception as e:
                                        st.error(f"Error al eliminar: {str(e)}")
                            
                            # Agregar sección de ubicación en mapa
                            st.markdown("#### 📍 Ubicación en Mapa")
                            
                            # Configuración de Mapbox
                            mapbox_token = st.secrets["MAPBOX_TOKEN"]
                            mapbox_style = "mapbox://styles/mapbox/streets-v11"

                            if property.get('latitude') and property.get('longitude'):
                                # Crear mapa con Mapbox
                                m = folium.Map(
                                    location=[property['latitude'], property['longitude']],
                                    zoom_start=15,
                                    tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}",
                                    attr='Mapbox',
                                )
                                
                                # Agregar marcador personalizado
                                folium.Marker(
                                    [property['latitude'], property['longitude']],
                                    popup=property['title'],
                                    icon=folium.Icon(color='red', icon='home', prefix='fa')
                                ).add_to(m)
                                
                                # Mostrar el mapa
                                st_folium(m, width=400, height=300)
                                
                                # Botón para modificar ubicación
                                if st.button("🗺️ Modificar ubicación"):
                                    st.session_state.editing_location = True
                            else:
                                # Botón para agregar ubicación
                                if st.button("📍 Agregar al mapa"):
                                    st.session_state.editing_location = True
                            
                            # Si estamos editando la ubicación
                            if getattr(st.session_state, 'editing_location', False):
                                st.markdown("#### Seleccionar ubicación")
                                
                                # Geocodificación con Mapbox
                                location_search = st.text_input("Buscar ubicación", value=property.get('location', ''))
                                if location_search:
                                    try:
                                        geocode_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location_search}.json?access_token={mapbox_token}"
                                        response = requests.get(geocode_url)
                                        if response.ok:
                                            results = response.json()
                                            if results['features']:
                                                feature = results['features'][0]
                                                lon, lat = feature['center']
                                                st.success(f"Ubicación encontrada: {feature['place_name']}")
                                            else:
                                                lat, lon = 19.4326, -99.1332  # Coordenadas por defecto (CDMX)
                                    except Exception as e:
                                        st.error(f"Error en la búsqueda: {str(e)}")
                                        lat, lon = 19.4326, -99.1332
                                else:
                                    lat = property.get('latitude', 19.4326)
                                    lon = property.get('longitude', -99.1332)
                                
                                # Mapa para seleccionar ubicación con Mapbox
                                select_map = folium.Map(
                                    location=[lat, lon],
                                    zoom_start=15,
                                    tiles=f"https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{{z}}/{{x}}/{{y}}?access_token={mapbox_token}",
                                    attr='Mapbox'
                                )
                                folium.Marker([lat, lon]).add_to(select_map)
                                map_data = st_folium(select_map, width=400, height=300)
                                
                                # Actualizar coordenadas si se hace clic en el mapa
                                if map_data['last_clicked']:
                                    lat = map_data['last_clicked']['lat']
                                    lon = map_data['last_clicked']['lng']
                                
                                # Botones para guardar/cancelar
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("💾 Guardar ubicación"):
                                        try:
                                            response = requests.put(
                                                f"{BACKEND_URL}/properties/{property['id']}",
                                                json={
                                                    **property,
                                                    "latitude": lat,
                                                    "longitude": lon
                                                }
                                            )
                                            if response.ok:
                                                st.success("Ubicación guardada")
                                                del st.session_state.editing_location
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"Error al guardar: {str(e)}")
                                
                                with col2:
                                    if st.button("❌ Cancelar"):
                                        del st.session_state.editing_location
                                        st.rerun()
                            
                            # Link a la propiedad original
                            st.markdown(f"[🔗 Ver propiedad original]({property['url']})")
                        
                        # Galería de imágenes
                        if property.get('images'):
                            st.markdown("#### Imágenes")
                            # Botones para seleccionar imagen principal
                            st.markdown("**Selecciona la imagen principal:**")
                            image_cols = st.columns(3)
                            for idx, img_url in enumerate(property['images']):
                                with image_cols[idx % 3]:
                                    st.image(img_url, use_container_width=True)
                                    if st.button("Establecer como principal", key=f"main_{property['id']}_{idx}"):
                                        try:
                                            response = requests.put(
                                                f"{BACKEND_URL}/properties/{property['id']}",
                                                json={
                                                    **property,
                                                    "main_image": img_url
                                                }
                                            )
                                            if response.ok:
                                                st.success("Imagen principal actualizada")
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"Error al actualizar: {str(e)}")
                        
                        # Formulario de edición si está activo
                        if getattr(st.session_state, 'editing_property', None) == property['id']:
                            st.markdown("### Editar Propiedad")
                            with st.form(key=f"edit_form_{property['id']}"):
                                edited_title = st.text_input("Título", value=property['title'])
                                edited_price = st.text_input("Precio", value=property['price'])
                                edited_location = st.text_input("Ubicación", value=property['location'])
                                edited_description = st.text_area("Descripción", value=property.get('description', ''))
                                edited_notes = st.text_area("Notas personales", value=property.get('notes', ''))
                                
                                # Características numéricas
                                col1, col2 = st.columns(2)
                                with col1:
                                    edited_bathrooms = st.number_input("Baños", 
                                        value=float(property.get('bathrooms', 0) or 0),
                                        step=0.5)
                                    edited_bedrooms = st.number_input("Recámaras", 
                                        value=int(property.get('bedrooms', 0) or 0))
                                    edited_parking = st.number_input("Estacionamientos", 
                                        value=int(property.get('parking_spaces', 0) or 0))
                                
                                with col2:
                                    edited_construction = st.number_input("Construcción (m²)", 
                                        value=float(property.get('construction_size', 0) or 0))
                                    edited_lot = st.number_input("Terreno (m²)", 
                                        value=float(property.get('lot_size', 0) or 0))
                                    edited_floors = st.number_input("Niveles", 
                                        value=int(property.get('floors', 0) or 0))
                                
                                # Modificar los botones del formulario
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.form_submit_button("💾 Guardar cambios"):
                                        try:
                                            updated_data = {
                                                "title": edited_title,
                                                "price": edited_price,
                                                "location": edited_location,
                                                "description": edited_description,
                                                "notes": edited_notes,
                                                "url": property['url'],
                                                "images": property.get('images', []),
                                                "main_image": property.get('main_image'),
                                                "bathrooms": edited_bathrooms,
                                                "bedrooms": edited_bedrooms,
                                                "parking_spaces": edited_parking,
                                                "construction_size": edited_construction,
                                                "lot_size": edited_lot,
                                                "floors": edited_floors
                                            }
                                            
                                            response = requests.put(
                                                f"{BACKEND_URL}/properties/{property['id']}",
                                                json=updated_data
                                            )
                                            
                                            if response.ok:
                                                st.success("✅ Cambios guardados exitosamente")
                                                del st.session_state.editing_property
                                                st.rerun()
                                            else:
                                                st.error(f"❌ Error al guardar los cambios: {response.text}")
                                        except Exception as e:
                                            st.error(f"❌ Error de conexión: {str(e)}")
                                
                                with col2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        del st.session_state.editing_property
                                        st.rerun()

            # Paginación
            st.write(f"Página {data['current_page']} de {data['total_pages']}")
            cols = st.columns(2)
            with cols[0]:
                if data['current_page'] > 1:
                    if st.button("← Anterior"):
                        st.session_state.current_page -= 1
                        st.rerun()
            with cols[1]:
                if data['current_page'] < data['total_pages']:
                    if st.button("Siguiente →"):
                        st.session_state.current_page += 1
                        st.rerun()
                        
    except Exception as e:
        st.error(f"Error al cargar las propiedades: {str(e)}")
        # Mostrar el error completo para depuración
        st.exception(e)

def delete_property(property_id: int) -> bool:
    try:
        response = requests.delete(f"{BACKEND_URL}/properties/{property_id}")
        return response.ok
    except:
        return False

if __name__ == "__main__":
    main() 