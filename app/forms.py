# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional, NumberRange
from app.models import Usuario
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
        """Verifica que el email no esté registrado"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email ya está registrado. Por favor, usa otro.')

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
# FORMULARIO DE MEDICAMENTOS
# ============================================

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
    laboratorio = StringField('Laboratorio', validators=[Optional(), Length(max=100)])
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