from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app.database import db
from app.database.models import usuario
from passlib.hash import scrypt
import re

usuario_bp = Blueprint('auth', __name__, template_folder='app/templates')

# --- Rutas de autenticación ---
@usuario_bp.route('/logIn', methods=['GET'])
def mostrar_login():
    if 'userID' in session:
        return redirect(url_for('inicio.menu_inicio'))
    return render_template('LogIn-SignIn/login.html')

@usuario_bp.route('/autenticate', methods=['POST'])
def autenticar_usuario():
    result = autenticar_login_usuario(request)
    flash(*result['mensaje'])
    
    if result['mensaje'][1] == 'success':
        return redirect(url_for('inicio.menu_inicio'))
    return redirect(url_for('auth.mostrar_login'))

@usuario_bp.route('/logOut', methods=['GET'])
def cerrar_sesion():
    session.clear()
    flash('Sesión cerrada exitosamente.', 'success')
    return redirect(url_for('index'))

@usuario_bp.route('/signIn', methods=['GET'])
def mostrar_signin():
    if 'userID' in session:
        return redirect(url_for('inicio.menu_inicio'))
    return render_template('LogIn-SignIn/signIn.html')

@usuario_bp.route('/register', methods=['POST'])
def procesar_registro():
    is_json = request.content_type == 'application/json'
    data = request.get_json() if is_json else request.form

    resultado = registrar_nuevo_usuario(data)

    if is_json:
        status_code = 200 if resultado['mensaje'][1] == 'success' else 400
        return jsonify(resultado), status_code

    flash(*resultado['mensaje'])

    if resultado['mensaje'][1] == 'success':
        return redirect(url_for('index'))
    return redirect(url_for('auth.mostrar_signin'))


@usuario_bp.route('/perfil', methods=['GET'])
def vista_perfil():
    if 'userID' in session:
        return render_template('perfil.html')
    return redirect(url_for('auth.mostrar_login'))

@usuario_bp.route('/perfil/datos', methods=['GET'])
def obtener_perfil():
    if 'userID' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    usuario_actual = usuario.query.get(session['userID'])
    if not usuario_actual:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    return jsonify(usuario_actual.to_dict())

@usuario_bp.route('/perfil/actualizar', methods=['POST'])
def actualizar_perfil():
    if 'userID' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    usuario_actual = usuario.query.get(session['userID'])
    if not usuario_actual:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    data = request.get_json() if request.is_json else request.form
    
    # Validar campos únicos
    if 'username' in data and data['username'] != usuario_actual.username:
        if usuario.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya está en uso'}), 400
    
    if 'email' in data and data['email'] != usuario_actual.email:
        if usuario.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El correo electrónico ya está en uso'}), 400
    
    # Actualizar campos
    if 'first_name' in data:
        usuario_actual.first_name = data['first_name']
    if 'last_name' in data:
        usuario_actual.last_name = data['last_name']
    if 'username' in data:
        usuario_actual.username = data['username']
        session['username'] = data['username']
    if 'email' in data:
        usuario_actual.email = data['email']
        session['email'] = data['email']
    if 'password' in data and data['password']:
        usuario_actual.password = scrypt.hash(data['password'])
    
    try:
        db.session.commit()
        return jsonify({
            'success': 'Perfil actualizado correctamente',
            'usuario': usuario_actual.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500




# --- Funciones de autenticación ---
def autenticar_login_usuario(request):
    if request.method == 'POST':
        profile = request.form['Profile']
        password = request.form['Password']
        remember_me = 'remember_me' in request.form

        # Verificar si el input es email
        is_email = re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", profile)
        user = None
        
        if is_email:
            user = usuario.query.filter_by(email=profile).first()
        else:
            user = usuario.query.filter_by(username=profile).first()

        if not user or not scrypt.verify(password, user.password):
            return {'mensaje': ('Usuario o contraseña incorrectos', 'danger')}
        
        if user.estado == 'inactivo':
            return {'mensaje': ('Cuenta inactiva. Contacta al administrador.', 'danger')}

        # Configurar sesión
        session.clear()
        session['userID'] = user.userID
        session['username'] = user.username
        session['email'] = user.email
        session['rol'] = user.rol
        
        if remember_me:
            session.permanent = True  # Sesión persistente
            
        return {'mensaje': (f'Bienvenido, {user.first_name}!', 'success')}

def registrar_nuevo_usuario(data):
    try:
        if usuario.query.filter_by(email=data['email']).first():
            return {'mensaje': ('El correo electrónico ya está registrado', 'danger')}
        
        if usuario.query.filter_by(username=data.get('username', '')).first():
            return {'mensaje': ('El nombre de usuario ya existe', 'danger')}
        
        if data['password'] != data['confirm_password']:
            return {'mensaje': ('Las contraseñas no coinciden', 'danger')}

        new_user = usuario(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=data.get('username') or data['email'].split('@')[0],
            email=data['email'],
            password=scrypt.hash(data['password']),
            rol='invitado',
            estado='activo'
        )

        db.session.add(new_user)
        db.session.commit()

        return {
            'mensaje': ('Registro exitoso. ¡Bienvenido!', 'success'),
            'user': new_user.to_dict()
        }

    except Exception as e:
        db.session.rollback()
        print("Error en el registro:", str(e))
        return {'mensaje': (f'Error en el registro: {str(e)}', 'danger')}

# --- Crear superusuario si no existe ---
def crear_superadmin():
    try:
        # Verifica si ya existe un usuario con username 'superAdmin'
        admin_existente = usuario.query.filter_by(username='superAdmin').first()
        
        if not admin_existente:
            admin = usuario(
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
