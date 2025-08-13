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

    # --- Ruta global de inicio ---
    @app.route('/')
    def index():
        if 'userID' not in session:
            return render_template('index.html')
        return redirect(url_for('inicio.menu_inicio'))
    
    # --- Pagina en Construccion ---
    @app.route('/pagina_en_construccion')
    def construccion():
        return render_template('other/enConstruccion.html')
    
    
    # --- Errores personalizados ---
    @app.errorhandler(404)
    def error_404(error):
        return render_template('handler/404.html'), 404

    @app.errorhandler(500)
    def error_500(error):
        return render_template('handler/500.html'), 500
    
    # Crear usuario superAdmin inicial
    with app.app_context():
        from app.utils import crear_superadmin
        crear_superadmin()
    
    print("\nLista de rutas registradas:")
    for rule in app.url_map.iter_rules():
        print(f" * Endpoint: {rule.endpoint} -> URL: {rule}")
    
    
    #from .datosPrueba import generar_datos_prueba
    #with app.app_context():
    #    generar_datos_prueba()
    
    return app
