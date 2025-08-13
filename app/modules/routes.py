from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.utils import login_required, get_current_user, guardar_notificacion
from app.database import db
from app.database.models import usuario, notificacion, camara, deteccionPlaga, tipoPlaga, ubicacion
from passlib.hash import scrypt
import re
import os
import base64
from datetime import datetime
import requests

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
        flash("Usuario o contraseña incorrectos", "error")
        return redirect(url_for('auth.mostrar_login'))

    if user.estado == 'inactivo':
        flash("Cuenta inactiva. Contacta al administrador.", "error")
        return redirect(url_for('auth.mostrar_login'))

    session.clear()
    session['userID'] = user.idUsuario
    session['username'] = user.username
    session['email'] = user.email
    session['rol'] = user.rol

    if remember_me:
        session.permanent = True

    guardar_notificacion(user.idUsuario, "Inicio de sesión", "info", f"Usuario {user.username} inició sesión correctamente.")

    flash(f"Bienvenido, {user.username}!", "success")
    return redirect(url_for('inicio.menu_inicio'))

@usuario_bp.route('/logOut', methods=['GET'])
@login_required
def cerrar_sesion():
    user_id = session.get('userID')
    session.clear()
    # if user_id:
    #     guardar_notificacion(user_id, "Cierre de sesión", "info", "Sesión cerrada exitosamente.")
    flash("Sesión cerrada exitosamente", "success")
    return redirect(url_for('auth.mostrar_login'))

@usuario_bp.route('/signIn', methods=['GET'])
def mostrar_signin():
    if 'userID' in session:
        return redirect(url_for('inicio.menu_inicio'))
    return render_template('LogIn-SignIn/signIn.html')

@usuario_bp.route('/register', methods=['POST'])
def procesar_registro():
    data = request.form.to_dict()

    if usuario.query.filter_by(email=data.get('email')).first():
        flash("El correo electrónico ya está registrado", "error")
        return redirect(url_for('auth.mostrar_signin'))

    username = data.get('username') or data.get('email', '').split('@')[0]
    if usuario.query.filter_by(username=username).first():
        flash("El nombre de usuario ya existe", "error")
        return redirect(url_for('auth.mostrar_signin'))

    if data.get('password') != data.get('confirm_password'):
        flash("Las contraseñas no coinciden", "error")
        return redirect(url_for('auth.mostrar_signin'))

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

        flash("Registro exitoso. ¡Bienvenido!", "success")
        return redirect(url_for('auth.mostrar_login'))
    except Exception as e:
        db.session.rollback()
        print(f"Error en registro: {e}")
        flash("Error al registrar usuario", "error")
        return redirect(url_for('auth.mostrar_signin'))

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
        flash("Usuario no encontrado", "error")
        return redirect(url_for('auth.mostrar_login'))

    data = request.form.to_dict()
    if 'username' in data and data['username'] != user.username:
        if usuario.query.filter_by(username=data['username']).first():
            flash("El nombre de usuario ya está en uso", "error")
            return redirect(url_for('auth.vista_perfil'))
    if 'email' in data and data['email'] != user.email:
        if usuario.query.filter_by(email=data['email']).first():
            flash("El correo electrónico ya está en uso", "error")
            return redirect(url_for('auth.vista_perfil'))

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
        flash("Perfil actualizado correctamente", "success")
        return redirect(url_for('auth.vista_perfil'))
    except Exception as e:
        db.session.rollback()
        print(f"Error actualizando perfil: {e}")
        flash("Error al actualizar perfil", "error")
        return redirect(url_for('auth.vista_perfil'))


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
    limit = request.args.get('limit', type=int)  # None si no viene
    query = (notificacion.query
             .filter_by(idUsuario=user_id)
             .order_by(notificacion.fecha.desc()))
    
    if limit:  # solo aplicas si viene
        query = query.limit(limit)
    
    notifs = query.all()
    return jsonify([n.to_dict() for n in notifs])


@notificacion_bp.route('/notificaciones/<notif_id>/leido', methods=['POST'])
@login_required
def marcar_notificacion_leida(notif_id):
    user_id = session.get('userID')

    if notif_id == "all":
        # Marcar todas las no leídas
        pendientes = notificacion.query.filter_by(idUsuario=user_id, leido=False).all()
        for notif in pendientes:
            notif.leido = True
        if pendientes:
            db.session.commit()
            print(f"Todas las notificaciones marcadas como leídas para usuario {user_id}")
        return '', 204

    # Intentar convertir notif_id a int
    try:
        notif_id = int(notif_id)
    except ValueError:
        return '', 400

    notif = notificacion.query.filter_by(idNotificacion=notif_id, idUsuario=user_id).first()
    if notif:
        if not notif.leido:  # Solo actualizar si no estaba ya leída
            notif.leido = True
            db.session.commit()
            print(f"Notificación {notif_id} marcada como leída por usuario {user_id}")
        return '', 204

    return '', 404

@notificacion_bp.route('/notificaciones/<notif_id>/no-leido', methods=['POST'])
@login_required
def marcar_notificacion_no_leida(notif_id):
    user_id = session.get('userID')

    try:
        notif_id = int(notif_id)
    except ValueError:
        return '', 400

    notif = notificacion.query.filter_by(idNotificacion=notif_id, idUsuario=user_id).first()
    if notif:
        if notif.leido:  # Solo actualizar si estaba leída
            notif.leido = False
            db.session.commit()
            print(f"Notificación {notif_id} marcada como NO leída por usuario {user_id}")
        return '', 204

    return '', 404


@notificacion_bp.route('/notificaciones/<notif_id>/delete', methods=['DELETE'])
@login_required
def borrar_notificacion(notif_id):
    user_id = session.get('userID')

    if notif_id == "all":
        notifs = notificacion.query.filter_by(idUsuario=user_id).all()
        for n in notifs:
            db.session.delete(n)
        db.session.commit()
        return '', 204

    try:
        notif_id = int(notif_id)
    except ValueError:
        return '', 400

    notif = notificacion.query.filter_by(idNotificacion=notif_id, idUsuario=user_id).first()
    if notif:
        db.session.delete(notif)
        db.session.commit()
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

@camara_bp.route('/registrar_camara', methods=['POST'])
@login_required
def registrar_camara():
    nombre = request.form.get('nombre')
    ubicacion = request.form.get('ubicacion')
    url_camara = request.form.get('url')

    if not nombre or not url_camara:
        flash("El nombre y la URL de la cámara son obligatorios", "error")
        return redirect(url_for('camara.vista_camara'))

    try:
        nueva_camara = camara(
            nombre=nombre,
            ubicacion_fisica=ubicacion,
            url=url_camara,
            idUsuario=session['userID']
        )
        db.session.add(nueva_camara)
        db.session.commit()

        guardar_notificacion(session['userID'], "Registro de cámara", "success",
                              f"Cámara '{nombre}' registrada correctamente.")
        flash("Cámara registrada correctamente", "success")
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar cámara: {e}")
        flash("Error al registrar la cámara", "error")

    return redirect(url_for('camara.vista_camara'))

# Listar cámaras del usuario
@camara_bp.route('/listar_camara', methods=['GET'])
@login_required
def listar_camaras():
    camaras = camara.query.filter_by(idUsuario=session['userID']).all()
    return jsonify([{
        'id': c.idCamara,
        'nombre': c.nombre,
        'url': c.url,
        'ubicacion': c.ubicacion_fisica,
    } for c in camaras])


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Guardar foto
@camara_bp.route('/guardar_foto/<int:idCamara>', methods=['POST'])
@login_required
def guardar_foto(idCamara):
    print(f"Guardando foto para cámara {idCamara}")
    data = request.get_json()
    imagen_b64 = data.get('imagen', '').split(',')[1]
    img_bytes = base64.b64decode(imagen_b64)

    folder = os.path.join(BASE_DIR, 'static', 'capturas')
    os.makedirs(folder, exist_ok=True)

    filename = f"{idCamara}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(folder, filename)
    
    print("Guardando en:", os.path.abspath(path))
        
    with open(path, 'wb') as f:
        f.write(img_bytes)


    return jsonify({'status': 'ok', 'filename': filename})

zoom_states = {}

@camara_bp.route('/control_camara/<int:idCamara>', methods=['POST'])
@login_required
def control_camara(idCamara):
    data = request.get_json()
    accion = data.get('accion')

    camara_obj = camara.query.get(idCamara)
    if not camara_obj:
        return jsonify({"error": "Cámara no encontrada"}), 404

    ip_url = camara_obj.url
    # Extraemos IP y puerto de la url
    from urllib.parse import urlparse
    parsed = urlparse(ip_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"  # http://192.168.100.42:8000

    current_zoom = zoom_states.get(idCamara, 0)

    if accion == "zoomIn":
        current_zoom = min(100, current_zoom + 10)
    elif accion == "zoomOut":
        current_zoom = max(0, current_zoom - 10)
    else:
        return jsonify({"error": "Acción inválida"}), 400

    zoom_states[idCamara] = current_zoom

    try:
        r = requests.get(f"{base_url}/ptz?zoom={current_zoom}", timeout=2)
        r.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"No se pudo controlar la cámara: {e}"}), 500

    return jsonify({"status": "ok", "zoom": current_zoom})