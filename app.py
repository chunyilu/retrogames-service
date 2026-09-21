from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import auth_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    port = app.config.get('PORT', 3000)
    print(f"Flask server running on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
