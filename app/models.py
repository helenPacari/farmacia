# app/models.py
from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relación con medicamentos (quién los creó/modificó)
    medicamentos_creados = db.relationship('Medicamento', foreign_keys='Medicamento.creado_por_id', backref='creado_por_usuario', lazy='dynamic')
    medicamentos_actualizados = db.relationship('Medicamento', foreign_keys='Medicamento.actualizado_por_id', backref='actualizado_por_usuario', lazy='dynamic')
    
    def set_password(self, password):
        """Crea el hash de la contraseña"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verifica la contraseña contra el hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellidos}>'

class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    nombre_generico = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    presentacion = db.Column(db.String(50), nullable=True)
    concentracion = db.Column(db.String(50), nullable=True)
    laboratorio = db.Column(db.String(100), nullable=True)
    precio_compra = db.Column(db.Float, nullable=False, default=0)
    precio_venta = db.Column(db.Float, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    stock_maximo = db.Column(db.Integer, nullable=True)
    ubicacion = db.Column(db.String(50), nullable=True)
    requiere_receta = db.Column(db.Boolean, default=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    # Auditoría
    creado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def valor_inventario(self):
        """Calcula el valor total del inventario de este medicamento"""
        return self.stock * self.precio_compra
    
    @property
    def ganancia_potencial(self):
        """Calcula la ganancia potencial si se vende todo el stock"""
        return self.stock * (self.precio_venta - self.precio_compra)
    
    @property
    def margen_ganancia(self):
        """Calcula el porcentaje de margen de ganancia"""
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
    
    @property
    def stock_bajo(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.stock <= self.stock_minimo
    
    def __repr__(self):
        return f'<Medicamento {self.nombre}>'