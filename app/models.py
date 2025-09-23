from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

# Define el enum para estado acorde a tu tabla MySQL
class EstadoCitaEnum(enum.Enum):
    pendiente = "pendiente"
    entregado = "entregado"
    cancelado = "cancelado"
    en_proceso = "en_proceso"
    finalizado ="finalizado"


class Cita(db.Model):
    __tablename__ = 'citas'  # nombre exacto de la tabla en MySQL
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    servicio_id = db.Column(db.Integer, db.ForeignKey('servicios.id'), nullable=False)
    tecnico_id = db.Column(db.Integer, db.ForeignKey('tecnicos.id'), nullable=True)
    cantidad = db.Column(db.Integer, nullable = False)
    descripcion = db.Column(db.String(100), nullable =True)

    fecha_ingreso = db.Column(db.DateTime, default=datetime.utcnow)  # fecha de reservacion
    fecha_entrega = db.Column(db.DateTime, nullable=False) #fecha estimada de entrega
    fecha_recibo = db.Column(db.DateTime, nullable=True) #fecha de recibo en taller
    ##agregar fecha_finalizado
   
    estado = db.Column(db.Enum(EstadoCitaEnum), nullable=False)

    # Relaciones para facilitar consultas
    usuario = db.relationship('Usuario', backref='citas')
    servicio = db.relationship('Servicio', backref='citas')
    tecnico = db.relationship('Tecnico', backref='citas')

    def __repr__(self):
        return f"<Cita {self.id} - Usuario ID {self.usuario_id} - Estado {self.estado.value}>"

class rolEnum(enum.Enum):
    cliente = 'cliente'
    admin = 'admin'

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    domicilio = db.Column(db.String(100), nullable =False)
    telefono = db.Column(db.String(20), nullable = False)
    contrasena = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.Enum(rolEnum), default=rolEnum.cliente, nullable=False)




    def set_password(self, password): #genera un hash seguro para la contraseña
        self.contrasena = generate_password_hash(password)

    def check_password(self, password):#compara la contraseña con el hash guardado
        return check_password_hash(self.contrasena, password)

    def __repr__(self):
        return f"<Usuario {self.id} - {self.email}>"
    
class Servicio(db.Model):
    __tablename__ = 'servicios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(100), nullable=False)
    duracion_horas = db.Column(db.Integer, nullable=False)

class Tecnico(db.Model):
    __tablename__ = 'tecnicos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Integer, nullable=False)
    especialidad = db.Column(db.String(100), nullable=False)


class Bici(db.Model):
    __tablename__= 'bicis'
    id_bici = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)
    talla = db.Column(db.String(10), nullable=False)
    rodada = db.Column(db.String(10), nullable=False)
    serie = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30), nullable=False)

    usuario = db.relationship("Usuario", backref="bicis")
    mantenimientos = db.relationship(
        "MantenimientoBici",
        backref="bici",
        cascade="all, delete-orphan"
    )



class MantenimientoBici(db.Model):
    __tablename__ = 'bicis_cita'
    id_bici_cita = db.Column(db.Integer, primary_key=True)
    id_cita = db.Column(db.Integer, db.ForeignKey("citas.id"), nullable=False)
    id_bici = db.Column(db.Integer, db.ForeignKey("bicis.id_bici"), nullable=False)

     # Relación con la tabla Citas
    cita = db.relationship("Cita", backref="mantenimiento_bici")

   
