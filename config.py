from pathlib import Path
from decouple import config as env_config
import logging


base_dir = Path(__file__).parent


class Config:
    """Set Base Flask configuration variables."""
    SECRET_KEY = env_config('SECRET_KEY')
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'
    SESSION_ALIVE_SECONDS = 1800
    HOST = '0.0.0.0'
    PORT = 8000


class DevConfig(Config):
    """Set Development Server Flask configuration variables."""
    FLASK_ENV = 'development'
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///organization_employees.sqlite'

    DEBUG = True
    TESTING = True


class ProductionConfig(Config):
    """Set Production Server Flask configuration variables."""
    FLASK_ENV = 'production'

    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///organization_employees.db'

    DEBUG = False
    TESTING = False


class LoggerConfig:
    format = '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
    datefmt='%d-%m-%Y %H:%M:%S'
    level = logging.DEBUG
    filename = Path(base_dir, 'organization_employee_portal.log')
