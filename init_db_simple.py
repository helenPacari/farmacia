# init_db_simple.py
from app import create_app, db
from app.models import Usuario, Medicamento
from datetime import date

app = create_app()

with app.app_context():
    print("🗄️ Creando tablas en MySQL...")
    
    # Eliminar tablas existentes (solo para prueba)
    db.drop_all()
    print("✅ Tablas eliminadas")
    
    # Crear todas las tablas
    db.create_all()
    print("✅ Tablas creadas!")
    
    # Crear usuario admin
    admin = Usuario(
        nombre='Admin',
        apellidos='Principal',
        telefono='123456789',
        email='admin@farmacia.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Crear medicamento de prueba
    med = Medicamento(
        nombre='Paracetamol',
        laboratorio='Genfar',
        precio_compra=1000,
        precio_venta=2500,
        stock=100,
        stock_minimo=20,
        creado_por_id=1
    )
    db.session.add(med)
    
    db.session.commit()
    print("✅ Datos de prueba insertados!")
    
    # Verificar
    usuarios = Usuario.query.all()
    medicamentos = Medicamento.query.all()
    print(f"👤 Usuarios: {len(usuarios)}")
    print(f"💊 Medicamentos: {len(medicamentos)}")