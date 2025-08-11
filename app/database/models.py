from app.database import db
from datetime import datetime

class usuario(db.Model):
    __tablename__ = 'usuarios'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'invitado'), nullable=False, default='invitado')
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    remember_token = db.Column(db.String(255))  # Para "Recuérdame"
    
    # Relación con notificaciones
    notificaciones = db.relationship('notificacion', back_populates='usuario', cascade='all, delete-orphan')

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class notificacion(db.Model):
    __tablename__ = 'notificaciones'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idNotificacion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('info', 'warning', 'error', 'success'), default='info')
    leido = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUsuario', ondelete='CASCADE'), nullable=False)
    
    usuario = db.relationship('usuario', back_populates='notificaciones')

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class Camara(db.Model):
    __tablename__ = 'camaras'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idCamara = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion_fisica = db.Column(db.String(150))
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUsuario'), nullable=False)

    # Relaciones
    usuario = db.relationship('usuario', back_populates='camaras')
    detecciones = db.relationship('deteccionPlaga', back_populates='camara', cascade='all, delete-orphan')


class tipoPlaga(db.Model):
    __tablename__ = 'tipos_plagas'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False)
    grado_afectacion = db.Column(db.Integer, nullable=False)  # 0-5
    etiqueta_gravedad = db.Column(db.String(50), nullable=False)

    detecciones = db.relationship('deteccionPlaga', back_populates='tipo_plaga', cascade='all, delete-orphan')


class ubicacion(db.Model):
    __tablename__ = 'ubicaciones'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idUbicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parcela = db.Column(db.String(10), nullable=False)
    region = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(150))

    detecciones = db.relationship('deteccionPlaga', back_populates='ubicacion', cascade='all, delete-orphan')


class deteccionPlaga(db.Model):
    __tablename__ = 'detecciones_plagas'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idDeteccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCamara = db.Column(db.Integer, db.ForeignKey('camaras.idCamara'), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicaciones.idUbicacion'), nullable=False)
    tipo_plaga_id = db.Column(db.Integer, db.ForeignKey('tipos_plagas.id'), nullable=False)
    nivel_plaga = db.Column(db.Integer, nullable=False, default=0)  # 0=sin afectación
    fecha_deteccion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=True)
    estado_control = db.Column(db.Enum('No controlada', 'En control', 'Erradicada'), default='No controlada')
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuarios.idUsuario'), nullable=False)

    usuario = db.relationship('usuario', back_populates='detecciones')
    tipo_plaga = db.relationship('tipoPlaga', back_populates='detecciones')
    ubicacion = db.relationship('ubicacion', back_populates='detecciones')
    camara = db.relationship('Camara', back_populates='detecciones')