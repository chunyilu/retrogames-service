import os

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    _db_url = os.environ.get('DATABASE_URL')
    if _db_url and _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = _db_url or f"sqlite:///{os.path.join(BASE_DIR, 'auth.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }
    SECRET_KEY = os.environ.get('SECRET_KEY', 'retro-secret-key-change-in-production')
    PORT = int(os.environ.get('PORT', 3000))
