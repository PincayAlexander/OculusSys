from .usuario import usuario_bp 
from .inicio import inicio_bp
from .live import live_bp
from .reporte import reporte_bp, Detecciones_bp

all_routes = [
    (usuario_bp, '/app/auth'),
    (inicio_bp, '/app'),
    (live_bp, '/app/camara'),
    (Detecciones_bp, '/app/deteccion'),
    (reporte_bp, '/app/reporte')
]
