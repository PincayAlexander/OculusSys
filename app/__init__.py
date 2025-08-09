from flask import Flask, session, request, redirect, url_for, render_template, jsonify
from .config import get_config_by_name
from .modules import all_routes
from .database import start_mysql

def create_app(config=None) -> Flask:
    app = Flask(__name__)
    if config:
        app.config.from_object(get_config_by_name(config))

    # Inizializar la base de datos de mysql
    start_mysql(app)
    
    # Registrar blueprints (rutas de la aplicación)
    for modulo, url in all_routes:
        app.register_blueprint(modulo, url_prefix=url)
    
    # Inizializar rutas globales para la aplicación
    from .database.models import usuario, notificacion

    @app.route('/')
    def index():
        if 'userID' not in session:
            return render_template('index.html')
        return redirect(url_for('inicio.menu_inicio'))

    # --- Usuario en plantilla ---
    @app.context_processor
    def inject_usuario():
        user = None
        if 'userID' in session:
            user = usuario.query.get(session['userID'])
        return dict(usuario=user)

    # --- Control de sesión ---
    @app.before_request
    def validar_sesion():
        session.permanent = True
        
        rutas_permitidas = [
            'auth.mostrar_login',  
            'auth.autenticar_usuario', 
            'auth.cerrar_sesion', 
            'auth.mostrar_signin',
            'auth.procesar_registro',
            'index',
            'static',
        ]
        
        # Excluir rutas de error (opcional pero recomendado)
        if request.endpoint in ['error_404', 'error_500']:
            return
        
        # Permitir acceso a rutas públicas o si hay sesión
        if request.endpoint in rutas_permitidas or 'userID' in session:
            return
        
        # Redirigir a index si no cumple las condiciones anteriores
        return redirect(url_for('index'))       
    
    # --- Notificaciones ---
    @app.route('/notificaciones', methods=['GET'])
    def get_notificaciones():
        if 'userID' not in session:
            return jsonify([])
        notifs = notificacion.query.filter_by(
            userID=session['userID']
        ).order_by(notificacion.fecha_creacion.desc()).all()
        return jsonify([{
            'id': n.id,
            'mensaje': n.mensaje,
            'tipo': n.tipo,
            'fecha': n.fecha_creacion.isoformat(),
            'leido': n.leido
        } for n in notifs])

    @app.route('/notificaciones/<int:notif_id>/leido', methods=['POST'])
    def marcar_notificacion_leida(notif_id):
        if 'userID' not in session:
            return jsonify({'error': 'No autorizado'}), 401
        notif = notificacion.query.filter_by(
            id=notif_id, userID=session['userID']
        ).first()
        if notif:
            notif.leido = True
            from app.database import db
            db.session.commit()
            return jsonify({'status': 'ok'})
        return jsonify({'error': 'No encontrada'}), 404

    # --- Errores personalizados ---
    @app.errorhandler(404)
    def error_404(error):
        return render_template('handler/404.html'), 404

    @app.errorhandler(500)
    def error_500(error):
        return render_template('handler/500.html'), 500
    
    # Crear usuario superAdmin inicial
    with app.app_context():
        from .modules.usuario import crear_superadmin
        crear_superadmin()
    
    print("\nLista de rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f" * Endpoint: {rule.endpoint} -> URL: {rule}")
    
    return app
