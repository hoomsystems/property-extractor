import os

def check_db_file():
    # Obtener el directorio actual
    current_dir = os.getcwd()
    print(f"Directorio actual: {current_dir}")
    
    # Buscar el archivo properties.db
    db_path = os.path.join(current_dir, "properties.db")
    if os.path.exists(db_path):
        print(f"Base de datos encontrada en: {db_path}")
        print(f"Tamaño: {os.path.getsize(db_path)} bytes")
    else:
        print("No se encontró el archivo properties.db")
        
        # Buscar en subdirectorios
        print("\nBuscando properties.db en subdirectorios...")
        for root, dirs, files in os.walk(current_dir):
            if "properties.db" in files:
                found_path = os.path.join(root, "properties.db")
                print(f"Base de datos encontrada en: {found_path}")
                print(f"Tamaño: {os.path.getsize(found_path)} bytes")

if __name__ == "__main__":
    check_db_file() 