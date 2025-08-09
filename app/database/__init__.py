from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()


def start_mysql(app: Flask):
    """Inizializar la base de datos de MySQL."""
    
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER','admin')}:"
        f"{os.getenv('MYSQL_PASSWORD', 'ad123.')}@"
        f"{os.getenv('MYSQL_HOST', '127.0.0.1')}/"
        f"{os.getenv('MYSQL_DB', 'db_OCULUS')}"
    )    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializar la extensión
    db.init_app(app)

    # Solo ejecutar verificación y creación si estás en modo desarrollo
    if app.config.get('DEBUG') == True:
        with app.app_context():
            try:
                # Verificar conexion con la bd
                db.session.execute(text("SELECT 1"))
                print(" * Conexión a la base de datos establecida.")
                
                 # Crear tablas si no existen
                db.create_all()
                print(" * Base de datos generada correctamente.")
            except Exception as e:
                print(f" * Error al generar la base de datos: {e}")
