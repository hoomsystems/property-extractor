from backend.database import engine
from backend.models import Base

def check_database():
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de datos verificada y tablas creadas si no existían")
    except Exception as e:
        print(f"Error al verificar la base de datos: {e}")

if __name__ == "__main__":
    check_database() 