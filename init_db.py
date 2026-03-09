# init_db.py
from app import create_app, db, bcrypt
from app.models import Usuario, Medicamento
from datetime import date

app = create_app()

with app.app_context():
    # Crear todas las tablas
    print("Creando tablas...")
    db.drop_all()  # Solo si quieres empezar desde cero
    db.create_all()
    
    # Crear usuario admin
    admin = Usuario(
        nombre='Admin',
        apellidos='Principal',
        telefono='123456789',
        email='admin@farmacia.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Crear algunos medicamentos de prueba
    medicamentos = [
        Medicamento(
            nombre='Paracetamol',
            nombre_generico='Paracetamol',
            laboratorio='Genfar',
            precio_compra=1000,
            precio_venta=2500,
            stock=100,
            stock_minimo=20,
            requiere_receta=False,
            creado_por_id=1
        ),
        Medicamento(
            nombre='Amoxicilina',
            nombre_generico='Amoxicilina',
            laboratorio='La Sante',
            precio_compra=5000,
            precio_venta=12000,
            stock=50,
            stock_minimo=15,
            requiere_receta=True,
            creado_por_id=1
        ),
        Medicamento(
            nombre='Losartán',
            nombre_generico='Losartán Potásico',
            laboratorio='MK',
            precio_compra=8000,
            precio_venta=18000,
            stock=30,
            stock_minimo=10,
            requiere_receta=True,
            creado_por_id=1
        )
    ]
    
    for med in medicamentos:
        db.session.add(med)
    
    db.session.commit()
    print("✅ Base de datos inicializada con datos de prueba!")
    print("   Usuario admin: admin@farmacia.com / admin123")