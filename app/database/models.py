from app.database import db
from datetime import datetime

class usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idUsuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    foto_perfil = db.Column(db.LargeBinary)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('admin', 'invitado'), nullable=False, default='invitado')
    estado = db.Column(db.Enum('activo', 'inactivo'), default='activo')
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    remember_token = db.Column(db.String(255))  # Para "Recuérdame"

    # Relaciones
    notificacion = db.relationship('notificacion', back_populates='usuario', cascade='all, delete-orphan')
    camara = db.relationship('camara', back_populates='usuario', cascade='all, delete-orphan')
    deteccion = db.relationship('deteccionPlaga', back_populates='usuario', cascade='all, delete-orphan')

    def to_dict(self):
        data = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        if self.foto_perfil:
            import base64
            data['foto_perfil'] = base64.b64encode(self.foto_perfil).decode('utf-8')
        return data


class notificacion(db.Model):
    __tablename__ = 'notificacion'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idNotificacion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.Enum('info', 'warning', 'error', 'success'), default='info')
    leido = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario', ondelete='CASCADE'), nullable=False)

    usuario = db.relationship('usuario', back_populates='notificacion')

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class camara(db.Model):
    __tablename__ = 'camara'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idCamara = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion_fisica = db.Column(db.String(150))
    url = db.Column(db.String(255), nullable=False)  # URL de la cámara
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    usuario = db.relationship('usuario', back_populates='camara')
    deteccion = db.relationship('deteccionPlaga', back_populates='camara', cascade='all, delete-orphan')


class tipoPlaga(db.Model):
    __tablename__ = 'tipo_plaga'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.Text, nullable=False)

    deteccion = db.relationship('deteccionPlaga', back_populates='tipo_plaga', cascade='all, delete-orphan')


class ubicacion(db.Model):
    __tablename__ = 'ubicacion'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idUbicacion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parcela = db.Column(db.String(10), nullable=False)
    region = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(150))

    deteccion = db.relationship('deteccionPlaga', back_populates='ubicacion', cascade='all, delete-orphan')


class deteccionPlaga(db.Model):
    __tablename__ = 'deteccion_plaga'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_collate': 'utf8mb4_spanish_ci'}

    idDeteccion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idCamara = db.Column(db.Integer, db.ForeignKey('camara.idCamara'), nullable=False)
    ubicacion_id = db.Column(db.Integer, db.ForeignKey('ubicacion.idUbicacion'), nullable=False)
    tipo_plaga_id = db.Column(db.Integer, db.ForeignKey('tipo_plaga.id'), nullable=False)

    grado_afectacion = db.Column(db.Integer, nullable=False, default=0)  # 0-5
    etiqueta_gravedad = db.Column(db.String(50), nullable=False, default="Sana")

    fecha_deteccion = db.Column(db.DateTime, default=datetime.utcnow)
    descripcion = db.Column(db.Text, nullable=True)
    estado_control = db.Column(db.Enum('No controlada', 'En control', 'Erradicada'), default='No controlada')
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    usuario = db.relationship('usuario', back_populates='deteccion')
    tipo_plaga = db.relationship('tipoPlaga', back_populates='deteccion')
    ubicacion = db.relationship('ubicacion', back_populates='deteccion')
    camara = db.relationship('camara', back_populates='deteccion')
