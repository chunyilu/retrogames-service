from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Email and password are required.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password or not str(email).strip():
        return jsonify({'error': 'Email and password are required.'}), 400

    email = str(email).strip()
    password = str(password)

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400

    try:
        user = User(email=email)
        user.set_password(password, rounds=10)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully!',
            'userId': user.id
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already exists.'}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Database error.'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Email and password are required.'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password or not str(email).strip():
        return jsonify({'error': 'Email and password are required.'}), 400

    email = str(email).strip()
    password = str(password)

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    return jsonify({
        'message': 'Login successful!',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200
