# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

# Instancias de extensiones
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Importar modelos aquí para evitar circular imports
    with app.app_context():
        from app import models  # noqa

    # Registrar Blueprints
    from app.routes import main, medicamentos, auth, clientes, ventas
    
    app.register_blueprint(main.bp)
    app.register_blueprint(medicamentos.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(clientes.bp)
    app.register_blueprint(ventas.bp)

    return app