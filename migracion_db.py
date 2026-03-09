# migrate_db.py
from app import create_app, db
from app.models import Usuario
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🗄️ Verificando estructura de la base de datos...")
    
    # Verificar si la columna 'rol' existe
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('usuarios')]
    
    if 'rol' not in columns:
        print("➕ Agregando columna 'rol' a la tabla usuarios...")
        db.session.execute(text("ALTER TABLE usuarios ADD COLUMN rol VARCHAR(20) DEFAULT 'vendedor'"))
        print("✅ Columna 'rol' agregada correctamente")
    else:
        print("✅ La columna 'rol' ya existe")
    
    # Actualizar usuarios existentes con un rol por defecto
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        if not usuario.rol:
            usuario.rol = 'admin' if usuario.email == 'admin@farmacia.com' else 'vendedor'
    
    db.session.commit()
    print("✅ Roles asignados a usuarios existentes")
    
    print("\n📊 Usuarios actualizados:")
    for usuario in Usuario.query.all():
        print(f"   - {usuario.email}: {usuario.rol}")