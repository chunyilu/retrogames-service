from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import auth_bp
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Create database tables if they do not exist - with retry logic
    with app.app_context():
        max_retries = 5
        for i in range(max_retries):
            try:
                # Log database URL (without credentials for security)
                db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
                if db_url:
                    # Mask credentials in URL for logging
                    if '://' in db_url and '@' in db_url:
                        protocol_rest = db_url.split('://', 1)
                        if '@' in protocol_rest[1]:
                            credentials_host = protocol_rest[1].split('@', 1)
                            masked_url = f"{protocol_rest[0]}://****:****@{credentials_host[1]}"
                        else:
                            masked_url = db_url
                    else:
                        masked_url = db_url
                    logger.info(f"Database URL: {masked_url}")

                db.create_all()
                logger.info("Database tables created successfully")
                break
            except Exception as e:
                logger.warning(f"Database connection attempt {i+1} failed: {str(e)}")
                if i < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(2 ** i)  # Exponential backoff
                else:
                    logger.error("Failed to connect to database after all retries")
                    # Don't fail the app startup - allow it to run and handle DB errors gracefully
                    pass

    return app


app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 3000)
    print(f"Flask server running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
