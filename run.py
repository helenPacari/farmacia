# run.py
from app import create_app, db

app = create_app()

# Crea las tablas de la base de datos si no existen
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)