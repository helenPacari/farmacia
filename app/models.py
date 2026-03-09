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
    rol = db.Column(db.String(20), default='vendedor')  # admin, vendedor, bodeguero
    
    # Relaciones
    medicamentos_creados = db.relationship('Medicamento', foreign_keys='Medicamento.creado_por_id', backref='creado_por_usuario', lazy='dynamic')
    medicamentos_actualizados = db.relationship('Medicamento', foreign_keys='Medicamento.actualizado_por_id', backref='actualizado_por_usuario', lazy='dynamic')
    ventas = db.relationship('Venta', backref='usuario', lazy='dynamic')
    clientes_creados = db.relationship('Cliente', backref='creado_por', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.nombre} {self.apellidos}>'

# ============================================
# TABLAS NUEVAS: CATEGORÍA Y LABORATORIO
# ============================================

class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    medicamentos = db.relationship('Medicamento', backref='categoria', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Laboratorio(db.Model):
    __tablename__ = 'laboratorios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    contacto = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    medicamentos = db.relationship('Medicamento', backref='laboratorio', lazy='dynamic')
    
    def __repr__(self):
        return f'<Laboratorio {self.nombre}>'

# ============================================
# TABLA MEDICAMENTO (ACTUALIZADA)
# ============================================

class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    nombre_generico = db.Column(db.String(100), nullable=True)
    descripcion = db.Column(db.Text, nullable=True)
    presentacion = db.Column(db.String(50), nullable=True)
    concentracion = db.Column(db.String(50), nullable=True)
    precio_compra = db.Column(db.Float, nullable=False, default=0)
    precio_venta = db.Column(db.Float, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    stock_maximo = db.Column(db.Integer, nullable=True)
    ubicacion = db.Column(db.String(50), nullable=True)
    requiere_receta = db.Column(db.Boolean, default=False)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    
    # NUEVAS CLAVES FORÁNEAS
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    laboratorio_id = db.Column(db.Integer, db.ForeignKey('laboratorios.id'), nullable=True)
    
    # Auditoría
    creado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # NUEVAS RELACIONES
    detalles_venta = db.relationship('DetalleVenta', backref='medicamento', lazy='dynamic')
    
    @property
    def valor_inventario(self):
        return self.stock * self.precio_compra
    
    @property
    def ganancia_potencial(self):
        return self.stock * (self.precio_venta - self.precio_compra)
    
    @property
    def margen_ganancia(self):
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0
    
    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo
    
    def __repr__(self):
        return f'<Medicamento {self.nombre}>'

# ============================================
# TABLAS NUEVAS: CLIENTE, VENTA, DETALLE VENTA
# ============================================

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo_identificacion = db.Column(db.String(20), default='CEDULA')  # CEDULA, RUC, PASAPORTE
    identificacion = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date)
    puntos = db.Column(db.Integer, default=0)
    observaciones = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Claves foráneas
    creado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Relaciones
    ventas = db.relationship('Venta', backref='cliente', lazy='dynamic', order_by='Venta.fecha.desc()')
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellidos}"
    
    @property
    def total_compras(self):
        return self.ventas.count()
    
    @property
    def total_gastado(self):
        return db.session.query(db.func.sum(Venta.total)).filter(Venta.cliente_id == self.id).scalar() or 0
    
    def __repr__(self):
        return f'<Cliente {self.nombre_completo}>'

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_factura = db.Column(db.String(20), unique=True, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    subtotal = db.Column(db.Float, nullable=False, default=0)
    iva = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False, default=0)
    descuento = db.Column(db.Float, default=0)
    forma_pago = db.Column(db.String(50), default='EFECTIVO')  # EFECTIVO, TARJETA, TRANSFERENCIA
    estado = db.Column(db.String(20), default='COMPLETADA')  # COMPLETADA, ANULADA, PENDIENTE
    observaciones = db.Column(db.Text)
    
    # Claves foráneas
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Relaciones
    detalles = db.relationship('DetalleVenta', backref='venta', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def cantidad_items(self):
        return self.detalles.count()
    
    @property
    def total_productos(self):
        return self.detalles.with_entities(db.func.sum(DetalleVenta.cantidad)).scalar() or 0
    
    def calcular_totales(self):
        """Calcula subtotal, IVA y total basado en los detalles"""
        self.subtotal = sum(d.subtotal for d in self.detalles)
        self.iva = self.subtotal * 0.12  # IVA 12%
        self.total = self.subtotal + self.iva - self.descuento
        return self.total
    
    def generar_numero_factura(self):
        """Genera un número de factura único"""
        ultima_venta = Venta.query.order_by(Venta.id.desc()).first()
        if ultima_venta:
            ultimo_numero = int(ultima_venta.numero_factura.split('-')[-1])
            nuevo_numero = ultimo_numero + 1
        else:
            nuevo_numero = 1
        from datetime import datetime
        año = datetime.now().year
        return f"FAC-{año}-{nuevo_numero:06d}"
    
    def __repr__(self):
        return f'<Venta {self.numero_factura}>'

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    descuento = db.Column(db.Float, default=0)
    subtotal = db.Column(db.Float, nullable=False)
    
    # Claves foráneas
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    
    @property
    def total(self):
        return self.subtotal - self.descuento
    
    def calcular_subtotal(self):
        self.subtotal = self.cantidad * self.precio_unitario
        return self.subtotal
    
    def __repr__(self):
        return f'<Detalle Venta {self.venta_id} - {self.medicamento_id}>'