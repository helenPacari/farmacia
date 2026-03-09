# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-super-segura'
    
    # Configuración para MySQL (cuando uses Docker)
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://farmacia_user:farmacia123@localhost:3306/farmacia_db'
    
    # Opciones adicionales para MySQL
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False