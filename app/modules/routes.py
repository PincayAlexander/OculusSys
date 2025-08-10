from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.utils import login_required, get_current_user, guardar_notificacion
from app.database import db
from app.database.models import usuario, notificacion
from passlib.hash import scrypt
import re
from datetime import datetime

# -------------------------
# RUTAS INICIO
# -------------------------
inicio_bp = Blueprint('inicio', __name__, template_folder='app/templates')

@inicio_bp.route('/inicio', methods=['GET'])
@login_required
def menu_inicio():
    user = get_current_user(filter_sensitive=True)
    return render_template('inicio.html', usuario=user)


# -------------------------
# RUTAS USUARIO (auth)
# -------------------------
usuario_bp = Blueprint('auth', __name__, template_folder='app/templates')

@usuario_bp.route('/logIn', methods=['GET'])
def mostrar_login():
    if 'userID' in session:
        return redirect(url_for('inicio.menu_inicio'))
    return render_template('LogIn-SignIn/login.html')

@usuario_bp.route('/autenticate', methods=['POST'])
def autenticar_usuario():
    profile = request.form.get('Profile')
    password = request.form.get('Password')
    remember_me = 'remember_me' in request.form

    is_email = re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", profile)
    user = usuario.query.filter_by(email=profile).first() if is_email else usuario.query.filter_by(username=profile).first()

    if not user or not scrypt.verify(password, user.password):
        return jsonify({"message": "Usuario o contraseña incorrectos", "category": "error", "errorType": "password"}), 400

    if user.estado == 'inactivo':
        return jsonify({"message": "Cuenta inactiva. Contacta al administrador.", "category": "error", "errorType": "inactivo"}), 400

    session.clear()
    session['userID'] = user.idUsuario
    session['username'] = user.username
    session['email'] = user.email
    session['rol'] = user.rol

    if remember_me:
        session.permanent = True

    guardar_notificacion(user.idUsuario, "Inicio de sesión", "info", f"Usuario {user.username} inició sesión correctamente.")

    return jsonify({"message": f"Bienvenido, {user.first_name}!", "category": "success", "errorType": None})

@usuario_bp.route('/logOut', methods=['GET'])
@login_required
def cerrar_sesion():
    user_id = session.get('userID')
    session.clear()
#    if user_id:  guardar_notificacion(user_id, "Cierre de sesión", "info", "Sesión cerrada exitosamente.")
    return jsonify({"message": "Sesión cerrada exitosamente", "category": "success", "errorType": None})

@usuario_bp.route('/signIn', methods=['GET'])
def mostrar_signin():
    if 'userID' in session:
        return redirect(url_for('inicio.menu_inicio'))
    return render_template('LogIn-SignIn/signIn.html')

@usuario_bp.route('/register', methods=['POST'])
def procesar_registro():
    is_json = request.content_type == 'application/json'
    data = request.get_json() if is_json else request.form.to_dict()

    # Validar email existente
    if usuario.query.filter_by(email=data.get('email')).first():
        return jsonify({
            "message": "El correo electrónico ya está registrado",
            "category": "error",
            "errorType": "email"
        }), 400

    # Validar username existente
    username = data.get('username') or data.get('email', '').split('@')[0]
    if usuario.query.filter_by(username=username).first():
        return jsonify({
            "message": "El nombre de usuario ya existe",
            "category": "error",
            "errorType": "username"
        }), 400

    # Validar contraseñas coincidan
    if data.get('password') != data.get('confirm_password'):
        return jsonify({
            "message": "Las contraseñas no coinciden",
            "category": "error",
            "errorType": "password"
        }), 400

    # Registro en base de datos
    try:
        new_user = usuario(
            first_name=data['first_name'],
            last_name=data['last_name'],
            username=username,
            email=data['email'],
            password=scrypt.hash(data['password']),
            rol='invitado',
            estado='activo'
        )
        db.session.add(new_user)
        db.session.commit()

        guardar_notificacion(new_user.idUsuario, "Registro", "success", f"Usuario {new_user.username} registrado exitosamente.")

        return jsonify({
            "message": "Registro exitoso. ¡Bienvenido!",
            "category": "success",
            "errorType": None
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {e}")
        return jsonify({
            "message": "Error al registrar usuario",
            "category": "error",
            "errorType": None
        }), 500

@usuario_bp.route('/perfil', methods=['GET'])
@login_required
def vista_perfil():
    user = get_current_user(filter_sensitive=False)
    if not user:
        return redirect(url_for('auth.mostrar_login'))
    return render_template('perfil.html', usuario=user)

@usuario_bp.route('/perfil/datos', methods=['GET'])
@login_required
def obtener_perfil():
    user = usuario.query.get(session['userID'])
    if not user:
        return jsonify({"message": "Usuario no encontrado", "category": "error", "errorType": None}), 404
    return jsonify(user.to_dict())

@usuario_bp.route('/perfil/actualizar', methods=['POST'])
@login_required
def actualizar_perfil():
    user = usuario.query.get(session['userID'])
    if not user:
        return jsonify({"message": "Usuario no encontrado", "category": "error", "errorType": None}), 404

    data = request.get_json() if request.is_json else request.form.to_dict()
    if 'username' in data and data['username'] != user.username:
        if usuario.query.filter_by(username=data['username']).first():
            return jsonify({"message": "El nombre de usuario ya está en uso", "category": "error", "errorType": "username"}), 400
    if 'email' in data and data['email'] != user.email:
        if usuario.query.filter_by(email=data['email']).first():
            return jsonify({"message": "El correo electrónico ya está en uso", "category": "error", "errorType": "email"}), 400

    for campo in ['first_name', 'last_name', 'username', 'email']:
        if campo in data:
            setattr(user, campo, data[campo])
            if campo in ['username', 'email']:
                session[campo] = data[campo]
                
    if 'password' in data and data['password']:
        user.password = scrypt.hash(data['password'])

    try:
        db.session.commit()
        guardar_notificacion(user.idUsuario, "Perfil actualizado", "info", "Perfil actualizado correctamente.")
        return jsonify({"message": "Perfil actualizado correctamente", "category": "success", "errorType": None})
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando perfil: {e}")
        return jsonify({"message": "Error al actualizar perfil", "category": "error", "errorType": None}), 500


# -------------------------
# RUTAS NOTIFICACIONES
# -------------------------
notificacion_bp = Blueprint('notificacion', __name__, template_folder='app/templates')

@notificacion_bp.route('/notificaciones', methods=['GET'])
@login_required
def vista_notificaciones():
    return render_template('notificaciones.html')

@notificacion_bp.route('/get_user_notification/', methods=['GET'])
@login_required
def get_notificaciones():
    user_id = session.get('userID')
    notifs = notificacion.query.filter_by(idUsuario=user_id).order_by(notificacion.fecha.desc()).all()
    return jsonify([n.to_dict() for n in notifs])

@notificacion_bp.route('/notificaciones/<int:notif_id>/leido', methods=['POST'])
@login_required
def marcar_notificacion_leida(notif_id):
    user_id = session.get('userID')
    notif = notificacion.query.filter_by(idNotificacion=notif_id, idUsuario=user_id).first()
    if notif:
        notif.leido = True
        db.session.commit()
        print(f"Notificación {notif_id} marcada como leída por usuario {user_id}")
        return '', 204
    return '', 404


# -------------------------
# RUTAS CAMARA
# -------------------------
camara_bp = Blueprint('camara', __name__, template_folder='app/templates')

@camara_bp.route('/live', methods=['GET'])
@login_required
def vista_camara():
    return render_template('camara.html')


# -------------------------
# RUTAS DETECCIONES
# -------------------------
detecciones_bp = Blueprint('deteccion', __name__, template_folder='app/templates')

@detecciones_bp.route('/detection', methods=['GET'])
@login_required
def vista_detecciones():
    return render_template('deteccion.html')
