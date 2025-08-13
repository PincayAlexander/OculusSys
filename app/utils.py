from functools import wraps
from flask import session, redirect, url_for, current_app
from app.database import db
from app.database.models import usuario, notificacion
from sqlalchemy.exc import SQLAlchemyError
from passlib.hash import scrypt
from datetime import datetime


def get_current_user(filter_sensitive=True):
    """Devuelve el usuario de la sesión, opcionalmente sin datos sensibles."""
    uid = session.get('userID')
    if not uid:
        return None
    
    user = usuario.query.get(uid)
    if not user:
        return None
    
    if filter_sensitive:
        return {
            'idUsuario': user.idUsuario,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'rol': user.rol
            # Excluye: password, tokens, etc.
        }
    return user

def login_required(func):
    """Decorador para rutas que requieren login."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'userID' not in session:
            # redirige a la ruta de login
            return redirect(url_for('auth.mostrar_login'))
        return func(*args, **kwargs)
    return wrapper

def crear_superadmin():
    try:
        admin_existente = usuario.query.filter_by(username='superAdmin').first()
        if not admin_existente:
            admin = usuario(
                foto_perfil=None,
                first_name='Super',
                last_name='Admin',
                username='superAdmin',
                email='admin.oculus@system.com',
                password=scrypt.hash('admin123'),
                rol='admin',
                estado='activo'
            )
            db.session.add(admin)
            db.session.commit()
            print(" * SuperAdmin creado exitosamente")
        else:
            print(" * SuperAdmin ya existe")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(" * Error creando superadmin:", str(e))

def init_template_user_injector(app):
    """
    Función para que en todas las plantillas exista 
    'usuario' con el objeto actual (o None).
    """
    @app.context_processor
    def inject_usuario():
        return {'usuario': get_current_user()}

def guardar_notificacion(idUsuario, titulo, tipo, mensaje):
    try:
        nueva_notificacion = notificacion(
            idUsuario=idUsuario,
            titulo=titulo,
            tipo=tipo,
            mensaje=mensaje,
            fecha=datetime.utcnow(),
            leido=False
        )
        db.session.add(nueva_notificacion)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error guardando notificación: {e}")
