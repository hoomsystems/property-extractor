from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Crear la conexión a la base de datos
SQLALCHEMY_DATABASE_URL = "sqlite:///./properties.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_database():
    db = SessionLocal()
    try:
        # Consultar todas las propiedades usando text()
        result = db.execute(text("SELECT * FROM properties"))
        properties = result.fetchall()
        
        print(f"\nTotal de propiedades encontradas: {len(properties)}")
        
        for prop in properties:
            print("\n=== Propiedad ===")
            for column, value in zip(result.keys(), prop):
                print(f"{column}: {value}")
            print("================")
            
    except Exception as e:
        print(f"Error al consultar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database() 