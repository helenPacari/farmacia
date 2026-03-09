# update_db.py
from app import create_app, db
from app.models import Categoria, Laboratorio, Cliente
from datetime import date

app = create_app()

with app.app_context():
    print("🗄️ Actualizando base de datos...")
    
    # Crear nuevas tablas
    db.create_all()
    print("✅ Nuevas tablas creadas!")
    
    # Crear categorías de ejemplo
    categorias = [
        Categoria(nombre='Analgésicos', descripcion='Medicamentos para el dolor'),
        Categoria(nombre='Antibióticos', descripcion='Medicamentos para infecciones bacterianas'),
        Categoria(nombre='Antiinflamatorios', descripcion='Medicamentos para inflamación'),
        Categoria(nombre='Vitaminas', descripcion='Suplementos vitamínicos'),
        Categoria(nombre='Sistema Nervioso', descripcion='Medicamentos para el sistema nervioso'),
    ]
    
    for cat in categorias:
        db.session.add(cat)
    
    # Crear laboratorios de ejemplo
    laboratorios = [
        Laboratorio(nombre='Genfar', direccion='Calle 10 #23-45', telefono='1234567', email='contacto@genfar.com'),
        Laboratorio(nombre='La Sante', direccion='Av. Principal #45-67', telefono='7654321', email='info@lasante.com'),
        Laboratorio(nombre='MK', direccion='Carrera 8 #12-34', telefono='9876543', email='ventas@mk.com'),
        Laboratorio(nombre='Bayer', direccion='Transversal 5 #67-89', telefono='2345678', email='contacto@bayer.com'),
    ]
    
    for lab in laboratorios:
        db.session.add(lab)
    
    # Crear clientes de ejemplo
    clientes = [
        Cliente(
            tipo_identificacion='CEDULA',
            identificacion='1234567890',
            nombre='Juan',
            apellidos='Pérez Gómez',
            telefono='0999123456',
            email='juan@email.com',
            direccion='Calle Principal 123'
        ),
        Cliente(
            tipo_identificacion='CEDULA',
            identificacion='0987654321',
            nombre='María',
            apellidos='González López',
            telefono='0999234567',
            email='maria@email.com',
            direccion='Av. Secundaria 456'
        ),
        Cliente(
            tipo_identificacion='RUC',
            identificacion='1798765432001',
            nombre='Carlos',
            apellidos='Rodríguez Martínez',
            telefono='0999345678',
            email='carlos@empresa.com',
            direccion='Zona Industrial 789'
        ),
    ]
    
    for cli in clientes:
        db.session.add(cli)
    
    db.session.commit()
    print(f"✅ {len(categorias)} categorías creadas")
    print(f"✅ {len(laboratorios)} laboratorios creados")
    print(f"✅ {len(clientes)} clientes creados")
    
    print("\n📊 Resumen de tablas:")
    print(f"   Categorías: {Categoria.query.count()}")
    print(f"   Laboratorios: {Laboratorio.query.count()}")
    print(f"   Clientes: {Cliente.query.count()}")