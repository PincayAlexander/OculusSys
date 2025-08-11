from .routes import inicio_bp, usuario_bp, notificacion_bp, camara_bp
from .reportes import reporte_bp, detecciones_bp

all_routes = [
    (usuario_bp, '/app/auth'),
    (inicio_bp, '/app'),
    (notificacion_bp, '/app/notificaciones'),
    (camara_bp, '/app/camara'),
    (detecciones_bp, '/app/deteccion'),
    (reporte_bp, '/app/reporte')
]
