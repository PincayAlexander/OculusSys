from flask import session
import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Configuración base común a todos los entornos."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY') or 'secretkey123'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    #SQLALCHEMY_ECHO = True

class TestingConfig(BaseConfig):
    DEBUG = True
    WTF_CSRF_ENABLED = False

class ProductionConfig(BaseConfig):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


def get_config_by_name(name):
    """ Get config by name """
    if name == 'development':
        return DevelopmentConfig()
    elif name == 'production':
        return ProductionConfig()
    elif name == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
