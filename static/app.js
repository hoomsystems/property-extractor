document.addEventListener('DOMContentLoaded', async () => {
    const propertiesList = document.getElementById('properties-list');
    const applyFiltersBtn = document.getElementById('applyFilters');
    const clearFiltersBtn = document.getElementById('clearFilters');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const currentPageSpan = document.getElementById('currentPage');
    const totalPagesSpan = document.getElementById('totalPages');
    const perPageSelect = document.getElementById('perPage');

    let currentPage = 1;
    let totalPages = 1;

    async function loadProperties(filters = {}) {
        try {
            const params = new URLSearchParams();
            if (filters.searchText) params.append('search', filters.searchText);
            if (filters.minPrice) params.append('min_price', filters.minPrice);
            if (filters.maxPrice) params.append('max_price', filters.maxPrice);
            if (filters.location) params.append('location', filters.location);
            if (filters.sortBy) params.append('sort_by', filters.sortBy);
            
            // Agregar parámetros de paginación
            params.append('page', currentPage);
            params.append('per_page', perPageSelect.value);

            const url = `http://138.197.176.62:8000/api/properties?${params.toString()}`;
            const response = await fetch(url);
            const data = await response.json();
            
            // Actualizar información de paginación
            totalPages = data.total_pages;
            currentPageSpan.textContent = currentPage;
            totalPagesSpan.textContent = totalPages;
            prevPageBtn.disabled = currentPage <= 1;
            nextPageBtn.disabled = currentPage >= totalPages;

            // Renderizar propiedades
            propertiesList.innerHTML = data.items.map(property => renderProperty(property)).join('');
        } catch (error) {
            console.error('Error al cargar las propiedades:', error);
            propertiesList.innerHTML = '<p>Error al cargar las propiedades</p>';
        }
    }

    function getFilters() {
        return {
            searchText: document.getElementById('searchText').value,
            minPrice: document.getElementById('minPrice').value,
            maxPrice: document.getElementById('maxPrice').value,
            location: document.getElementById('location').value,
            sortBy: document.getElementById('sortBy').value
        };
    }

    applyFiltersBtn.addEventListener('click', () => {
        loadProperties(getFilters());
    });

    clearFiltersBtn.addEventListener('click', () => {
        // Limpiar todos los campos de filtro
        document.getElementById('searchText').value = '';
        document.getElementById('minPrice').value = '';
        document.getElementById('maxPrice').value = '';
        document.getElementById('location').value = '';
        document.getElementById('sortBy').value = 'date_desc';
        // Recargar propiedades sin filtros
        loadProperties();
    });

    // Eventos de paginación
    prevPageBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            loadProperties(getFilters());
        }
    });

    nextPageBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            loadProperties(getFilters());
        }
    });

    perPageSelect.addEventListener('change', () => {
        currentPage = 1;
        loadProperties(getFilters());
    });

    // Cargar propiedades inicialmente
    loadProperties();

    function createEditForm(property) {
        return `
            <form class="edit-form" onsubmit="updateProperty(event, ${property.id})">
                <input type="text" name="title" value="${property.title}" required>
                <input type="text" name="price" value="${property.price}" required>
                <input type="text" name="location" value="${property.location}" required>
                <textarea name="notes">${property.notes || ''}</textarea>
                <input type="hidden" name="url" value="${property.url}">
                <div class="image-upload">
                    <input type="file" multiple accept="image/*" onchange="uploadImages(${property.id}, this.files)">
                </div>
                <div class="images-preview">
                    ${property.images.map(img => `
                        <div class="image-thumbnail">
                            <img src="${img}" alt="Property image">
                        </div>
                    `).join('')}
                </div>
                <button type="submit">Guardar cambios</button>
                <button type="button" onclick="cancelEdit(${property.id})">Cancelar</button>
            </form>
        `;
    }

    async function updateProperty(event, propertyId) {
        event.preventDefault();
        const form = event.target;
        const formData = {
            title: form.title.value,
            price: form.price.value,
            location: form.location.value,
            notes: form.notes.value,
            url: form.url.value,
            images: Array.from(document.querySelectorAll(`#property-${propertyId} .images-preview img`))
                .map(img => img.src)
        };

        try {
            const response = await fetch(`http://hoomextractor.online/api/properties/${propertyId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                loadProperties(getFilters());
            } else {
                alert('Error al actualizar la propiedad');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al actualizar la propiedad');
        }
    }

    async function uploadImages(propertyId, files) {
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            const response = await fetch(`http://hoomextractor.online/api/properties/${propertyId}/images`, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                const previewDiv = document.querySelector(`#property-${propertyId} .images-preview`);
                data.uploaded_images.forEach(imgUrl => {
                    previewDiv.innerHTML += `
                        <div class="image-thumbnail">
                            <img src="${imgUrl}" alt="Property image">
                        </div>
                    `;
                });
            } else {
                alert('Error al subir las imágenes');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error al subir las imágenes');
        }
    }

    function renderProperty(property) {
        return `
            <div id="property-${property.id}" class="property-card">
                <div class="property-content">
                    <h3>${property.title}</h3>
                    <p>Precio: ${property.price}</p>
                    <p>Ubicación: ${property.location}</p>
                    <p>Fecha: ${new Date(property.date).toLocaleDateString()}</p>
                    <p>Notas: ${property.notes || ''}</p>
                    <div class="property-images">
                        ${property.images.map(img => `
                            <img src="${img}" alt="Property image">
                        `).join('')}
                    </div>
                    <a href="${property.url}" target="_blank">Ver propiedad</a>
                    <button onclick="startEdit(${property.id})">Editar</button>
                    <button onclick="deleteProperty(${property.id})">Eliminar</button>
                </div>
            </div>
        `;
    }
}); 