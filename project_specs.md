# Property Collector - Especificaciones del Proyecto

## Objetivo General
Crear una herramienta web que permita a los usuarios guardar y organizar propiedades inmobiliarias encontradas en diferentes sitios web, sin necesidad de instalar extensiones del navegador.

## Nueva Arquitectura
- **Frontend**: Streamlit (reemplaza el frontend anterior en HTML/JS)
- **Backend**: FastAPI + SQLAlchemy
- **Base de datos**: SQLite (escalable a PostgreSQL)
- **Bookmarklet**: JavaScript (se mantiene para la captura de datos)

## Nueva Estructura del Proyecto

### Frontend

#### `index.html`
- Página principal del dashboard
- Contiene el bookmarklet para ser arrastrado a favoritos
- Muestra la lista de propiedades guardadas
- Incluye estilos básicos para el popup

#### `static/collector.js`
- Script que se inyecta en las páginas web al usar el bookmarklet
- Crea un popup flotante para capturar información de la propiedad
- Maneja la recolección y envío de datos al backend
- Incluye estilos inline para el popup
- Campos que captura:
  - Título (automático desde el título de la página)
  - Precio
  - Ubicación
  - Notas
  - URL (automático)
  - Fecha (automático)

#### `static/app.js`
- Script principal del dashboard
- Maneja la carga y visualización de propiedades guardadas
- Realiza peticiones al backend para obtener los datos
- Renderiza las propiedades en formato de tarjetas

### Backend

#### `backend/main.py`
- Punto de entrada principal de la aplicación FastAPI
- Configura CORS para permitir peticiones del frontend
- Monta los archivos estáticos
- Inicializa la base de datos

#### `backend/models.py`
- Define el modelo de datos usando SQLAlchemy
- Establece la conexión con la base de datos SQLite
- Define la tabla 'properties' con sus campos:
  - id (Primary Key)
  - title: String
  - price: String
  - location: String
  - url: String
  - notes: String (opcional)
  - images: JSON (lista de URLs de imágenes)
  - date: DateTime

#### `backend/routes.py`
- Define los endpoints de la API:
  - POST /api/properties: Crear nueva propiedad
  - GET /api/properties: Obtener todas las propiedades
  - PUT /api/properties/{id}: Actualizar una propiedad
  - DELETE /api/properties/{id}: Eliminar una propiedad
  - POST /api/properties/{id}/images: Subir imágenes
- Maneja la lógica de negocio para cada endpoint
- Gestiona el almacenamiento de imágenes en el servidor

#### `backend/schemas.py`
- Define los modelos Pydantic para validación de datos:
  - PropertyBase: Esquema base con campos comunes
  - PropertyCreate: Esquema para crear propiedades
  - PropertyUpdate: Esquema para actualizar propiedades
  - PropertyResponse: Esquema para respuestas de la API
  - PaginatedResponse: Esquema para respuestas paginadas

#### `backend/database.py`
- Configura la sesión de la base de datos
- Proporciona un generador de dependencias para las rutas

## Estructura de la Base de Datos
### Tabla: properties
- id: Integer (Primary Key)
- title: String
- price: String
- location: String
- url: String
- notes: String (opcional)
- date: DateTime

## Funcionalidades Principales
1. Captura de datos mediante bookmarklet
2. Almacenamiento local de propiedades
3. Visualización en dashboard
4. Edición y eliminación de propiedades
5. Filtrado y búsqueda

## Funcionalidades de Filtrado (Implementado)
- Búsqueda por texto en título y notas
- Filtrado por rango de precios (min_price, max_price)
- Filtrado por ubicación
- Ordenamiento por:
  - Fecha (ascendente/descendente)
  - Precio (ascendente/descendente)

### Componentes de Filtrado Implementados
#### Frontend (`index.html` y `app.js`)
- Barra de búsqueda de texto implementada
- Campos numéricos para rango de precios
- Campo de texto para filtrar por ubicación
- Selector de ordenamiento con opciones:
  - Más recientes primero (date_desc)
  - Más antiguos primero (date_asc)
  - Menor precio (price_asc)
  - Mayor precio (price_desc)
- Botones funcionales:
  - "Aplicar Filtros": Aplica los filtros seleccionados
  - "Limpiar Filtros": Resetea todos los campos

#### Backend (`routes.py`)
- Endpoint GET /api/properties actualizado con parámetros:
  - search: búsqueda en título y notas (Optional[str])
  - min_price: precio mínimo (Optional[float])
  - max_price: precio máximo (Optional[float])
  - location: ubicación (Optional[str])
  - sort_by: criterio de ordenamiento (Optional[str], default="date_desc")

### Implementación Técnica
- Filtros implementados usando SQLAlchemy queries
- Búsqueda de texto usando ILIKE para case-insensitive matching
- Ordenamiento implementado usando funciones desc() y asc() de SQLAlchemy
- Frontend construye URLs con parámetros usando URLSearchParams
- Actualización dinámica del listado sin recargar la página

## Funcionalidades de Paginación (Implementado)
### Backend
- Endpoint GET /api/properties actualizado con parámetros de paginación:
  - page: número de página (default: 1)
  - per_page: items por página (default: 10, max: 100)
- Respuesta incluye metadata de paginación:
  - total_items: total de registros
  - total_pages: total de páginas
  - current_page: página actual
  - per_page: items por página

### Frontend
- Controles de navegación:
  - Botón "Anterior"
  - Botón "Siguiente"
  - Indicador de página actual
  - Selector de items por página
- Actualización dinámica al cambiar de página
- Integración con sistema de filtros existente

## Sistema de Edición (Implementado)
### Frontend
- Formulario de edición integrado en las tarjetas de propiedades
- Campos editables:
  - Título
  - Precio
  - Ubicación
  - Notas
  - Imágenes
- Botones de acción:
  - Guardar cambios
  - Cancelar edición
  - Eliminar propiedad

### Backend
- Endpoint PUT para actualización de propiedades
- Validación de datos mediante Pydantic
- Actualización parcial de campos permitida

## Sistema de Imágenes (Implementado)
### Almacenamiento
- Directorio: static/uploads/
- Nomenclatura: {property_id}_{timestamp}_{filename}
- Acceso vía URL: /static/uploads/{filename}

### Frontend
- Previsualización de imágenes en tarjetas
- Subida múltiple de imágenes
- Visualización en galería
- Integración con formulario de edición

### Backend
- Endpoint específico para subida de imágenes
- Almacenamiento en sistema de archivos
- Referencias guardadas en base de datos
- Manejo de múltiples archivos

## Próximos Pasos
- [x] Agregar paginación al listado de propiedades
- [x] Implementar sistema de edición de propiedades
- [x] Agregar captura de imágenes
- [ ] Mejorar el diseño visual del dashboard
- [ ] Implementar sistema de etiquetas/categorías 