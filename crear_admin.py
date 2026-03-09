# crear_admin_ahora.py
from app import create_app, db
from app.models import Usuario

app = create_app()

with app.app_context():
    # Crear usuario admin
    admin = Usuario(
        nombre='Admin',
        apellidos='Principal',
        telefono='0999999999',
        email='admin@farmacia.com',
        rol='admin',
        activo=True
    )
    admin.set_password('admin123')
    
    db.session.add(admin)
    db.session.commit()
    
    print("✅ Usuario admin creado exitosamente!")
    print(f"   Email: admin@farmacia.com")
    print(f"   Password: admin123")
    print(f"   Rol: {admin.rol}")
    
    # Verificar
    usuarios = Usuario.query.all()
    print(f"\n📊 Total usuarios: {len(usuarios)}")
    for u in usuarios:
        print(f"   - {u.email}: {u.rol}")