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
