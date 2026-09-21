import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{os.path.join(BASE_DIR, 'auth.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_recycle': 300,    # Recycle connections after 5 minutes
        'connect_timeout': 20,  # Connection timeout of 20 seconds
    }
    SECRET_KEY = os.environ.get('SECRET_KEY', 'retro-secret-key-change-in-production')
    PORT = int(os.environ.get('PORT', 3000))
