# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField, DateField, DecimalField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from app.models import Usuario, Cliente, Venta, Medicamento
from datetime import date

# ============================================
# FORMULARIOS DE AUTENTICACIÓN
# ============================================

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres")
    ])
    apellidos = StringField('Apellidos', validators=[
        DataRequired(message="Los apellidos son obligatorios"),
        Length(min=2, max=100, message="Los apellidos deben tener entre 2 y 100 caracteres")
    ])
    telefono = StringField('Teléfono', validators=[
        DataRequired(message="El teléfono es obligatorio"),
        Length(min=8, max=20, message="Teléfono inválido")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="El email es obligatorio"),
        Email(message="Ingresa un email válido")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria"),
        Length(min=6, message="La contraseña debe tener al menos 6 caracteres")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message="Confirma tu contraseña"),
        EqualTo('password', message="Las contraseñas no coinciden")
    ])
    submit = SubmitField('Registrarse')
    
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email ya está registrado.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="El email es obligatorio"),
        Email(message="Ingresa un email válido")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria")
    ])
    recordar = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

# ============================================
# NUEVOS FORMULARIOS: CATEGORÍA Y LABORATORIO
# ============================================

class CategoriaForm(FlaskForm):
    nombre = StringField('Nombre de Categoría', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=50, message="El nombre debe tener entre 2 y 50 caracteres")
    ])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    submit = SubmitField('Guardar')
    
    def validate_nombre(self, nombre):
        categoria = Categoria.query.filter_by(nombre=nombre.data).first()
        if categoria:
            raise ValidationError('Esta categoría ya existe.')

class LaboratorioForm(FlaskForm):
    nombre = StringField('Nombre del Laboratorio', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
    ])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(message="Email inválido")])
    contacto = StringField('Persona de Contacto', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Guardar')
    
    def validate_nombre(self, nombre):
        laboratorio = Laboratorio.query.filter_by(nombre=nombre.data).first()
        if laboratorio:
            raise ValidationError('Este laboratorio ya existe.')

# ============================================
# FORMULARIO DE MEDICAMENTO (ACTUALIZADO)
# ============================================

# app/forms.py - Clase MedicamentoForm ACTUALIZADA

class MedicamentoForm(FlaskForm):
    codigo_barras = StringField('Código de Barras', validators=[Optional(), Length(max=50)])
    nombre = StringField('Nombre Comercial', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
    ])
    nombre_generico = StringField('Nombre Genérico', validators=[Optional(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Optional()])
    presentacion = StringField('Presentación', validators=[Optional(), Length(max=50)])
    concentracion = StringField('Concentración', validators=[Optional(), Length(max=50)])
    
    # Campos de relación (NUEVOS)
    categoria_id = SelectField('Categoría', coerce=int, validators=[Optional()])
    laboratorio_id = SelectField('Laboratorio', coerce=int, validators=[Optional()])
    
    precio_compra = FloatField('Precio de Compra', validators=[
        DataRequired(message="El precio de compra es obligatorio"),
        NumberRange(min=0, message="El precio debe ser mayor o igual a 0")
    ])
    precio_venta = FloatField('Precio de Venta', validators=[
        DataRequired(message="El precio de venta es obligatorio"),
        NumberRange(min=0, message="El precio debe ser mayor o igual a 0")
    ])
    stock = IntegerField('Stock Actual', validators=[
        DataRequired(message="El stock es obligatorio"),
        NumberRange(min=0, message="El stock debe ser mayor o igual a 0")
    ])
    stock_minimo = IntegerField('Stock Mínimo', validators=[
        DataRequired(message="El stock mínimo es obligatorio"),
        NumberRange(min=0, message="El stock mínimo debe ser mayor o igual a 0")
    ])
    stock_maximo = IntegerField('Stock Máximo', validators=[Optional(), NumberRange(min=0)])
    ubicacion = StringField('Ubicación en Almacén', validators=[Optional(), Length(max=50)])
    requiere_receta = BooleanField('Requiere Receta Médica')
    fecha_vencimiento = DateField('Fecha de Vencimiento', validators=[Optional()])
    submit = SubmitField('Guardar')
    
    def validate_precio_venta(self, field):
        """Valida que el precio de venta sea mayor al de compra"""
        if self.precio_compra.data and field.data and field.data <= self.precio_compra.data:
            raise ValidationError('El precio de venta debe ser mayor al precio de compra')
    
    def validate_fecha_vencimiento(self, field):
        """Valida que la fecha de vencimiento no sea en el pasado"""
        if field.data and field.data < date.today():
            raise ValidationError('La fecha de vencimiento no puede ser en el pasado')

# ============================================
# NUEVOS FORMULARIOS: CLIENTE
# ============================================

class ClienteForm(FlaskForm):
    tipo_identificacion = SelectField('Tipo de Identificación', choices=[
        ('CEDULA', 'Cédula'),
        ('RUC', 'RUC'),
        ('PASAPORTE', 'Pasaporte')
    ], validators=[DataRequired()])
    identificacion = StringField('Número de Identificación', validators=[
        DataRequired(message="La identificación es obligatoria"),
        Length(min=5, max=20, message="Identificación inválida")
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message="El nombre es obligatorio"),
        Length(min=2, max=100, message="El nombre debe tener entre 2 y 100 caracteres")
    ])
    apellidos = StringField('Apellidos', validators=[
        DataRequired(message="Los apellidos son obligatorios"),
        Length(min=2, max=100, message="Los apellidos deben tener entre 2 y 100 caracteres")
    ])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=20)])
    email = StringField('Email', validators=[Optional(), Email(message="Email inválido")])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[Optional()])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    submit = SubmitField('Guardar Cliente')
    
    def validate_identificacion(self, field):
        cliente = Cliente.query.filter_by(identificacion=field.data).first()
        if cliente:
            raise ValidationError('Esta identificación ya está registrada.')

# ============================================
# NUEVOS FORMULARIOS: VENTA
# ============================================

class VentaForm(FlaskForm):
    cliente_id = SelectField('Cliente', coerce=int, validators=[DataRequired()])
    forma_pago = SelectField('Forma de Pago', choices=[
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta de Crédito/Débito'),
        ('TRANSFERENCIA', 'Transferencia Bancaria')
    ], validators=[DataRequired()])
    descuento = FloatField('Descuento', default=0, validators=[NumberRange(min=0)])
    observaciones = TextAreaField('Observaciones', validators=[Optional()])
    submit = SubmitField('Procesar Venta')

class DetalleVentaForm(FlaskForm):
    medicamento_id = SelectField('Medicamento', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[
        DataRequired(),
        NumberRange(min=1, message="La cantidad debe ser al menos 1")
    ])
    submit = SubmitField('Agregar')