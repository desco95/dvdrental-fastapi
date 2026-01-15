import os
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'database': os.getenv('DB_NAME', 'dvdrental')
}

# Pool de conexiones
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    **DB_CONFIG
)

@contextmanager
def get_db_connection():
    """
    Context manager para obtener una conexión de la base de datos.
    Maneja automáticamente el cierre de la conexión.
    """
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        connection_pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager para obtener un cursor con formato de diccionario.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cursor
            if commit:
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()