from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import make_url
from datetime import date
import traceback
import os

# Intentar importar los modelos ya sea como paquete o como módulo local
try:
    from app.models import Base, Product
except ModuleNotFoundError:
    try:
        from models import Base, Product
    except Exception:
        traceback.print_exc()
        raise

# Cambia credenciales DATABASE_URL en el entorno
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:root@localhost:3306/inventory?charset=utf8mb4")


def ensure_database():
    """Create the database if it doesn't exist (MySQL)."""
    try:
        url = make_url(DATABASE_URL)
    except Exception:
        return
    # Solo manejar MySQL
    if not str(url.drivername).startswith("mysql"):
        return

    dbname = url.database
    host = os.getenv("DB_HOST", url.host or "localhost")
    port = int(os.getenv("DB_PORT", url.port or 3306))
    admin_user = os.getenv("DB_ADMIN_USER", url.username or "root")
    admin_pass = os.getenv("DB_ADMIN_PASS", url.password or "")

    try:
        import mysql.connector
        cnx = mysql.connector.connect(host=host, user=admin_user, password=admin_pass, port=port)
        cnx.autocommit = True
        cur = cnx.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cur.close()
        cnx.close()
        print(f"Asegurada base de datos: {dbname}")
    except Exception:
        traceback.print_exc()
        raise

# Asegurar la base de datos antes de crear el engine
try:
    ensure_database()
except Exception:
    traceback.print_exc()

# Crear el engine con manejo de excepciones para ver trazas si falla
try:
    engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
except Exception:
    traceback.print_exc()
    raise

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Crear tablas (solo crea si no existen)
Base.metadata.create_all(bind=engine)

# Comprobación rápida de tablas
insp = inspect(engine)
print("Tablas en la BD:", insp.get_table_names())

