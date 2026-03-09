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
    from app.routes import main, medicamentos, auth
    
    app.register_blueprint(main.bp)
    app.register_blueprint(medicamentos.bp, url_prefix='/medicamentos')
    app.register_blueprint(auth.bp, url_prefix='/auth')
# app/__init__.py - Dentro de create_app(), antes de return app

    # Registrar filtros y funciones globales para plantillas
    @app.template_global()
    def now():
        from datetime import datetime
        return datetime.now()
    @app.template_global()
    def today():
        from datetime import date
        return date.today()

    return app