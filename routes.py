from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import db, User, GameScore

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


@auth_bp.route('/scores', methods=['POST'])
def record_score():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'userId, gameId, and score are required.'}), 400

    user_id = data.get('userId') if 'userId' in data else data.get('user_id')
    game_id = data.get('gameId') if 'gameId' in data else data.get('game_id')
    score_val = data.get('score')

    if user_id is None or not game_id or not str(game_id).strip() or score_val is None:
        return jsonify({'error': 'userId, gameId, and score are required.'}), 400

    try:
        score = int(score_val)
    except (ValueError, TypeError):
        return jsonify({'error': 'Score must be an integer.'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    try:
        game_score = GameScore(
            user_id=user.id,
            game_id=str(game_id).strip(),
            score=score
        )
        db.session.add(game_score)
        db.session.commit()

        return jsonify({
            'message': 'Score recorded successfully!',
            'score': game_score.to_dict()
        }), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Database error.'}), 500


@auth_bp.route('/scores/<game_id>', methods=['GET'])
@auth_bp.route('/scores/leaderboard/<game_id>', methods=['GET'])
def get_game_scores(game_id):
    limit = request.args.get('limit', type=int)
    query = GameScore.query.filter_by(game_id=str(game_id).strip()).order_by(
        GameScore.score.desc(),
        GameScore.created_at.asc()
    )
    if limit and limit > 0:
        scores = query.limit(limit).all()
    else:
        scores = query.all()

    return jsonify({
        'gameId': str(game_id).strip(),
        'scores': [s.to_dict() for s in scores]
    }), 200


@auth_bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.order_by(User.id.asc()).all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception:
        return jsonify({'error': 'Database error.'}), 500


@auth_bp.route('/users/<int:user_id>/scores', methods=['GET'])
def get_user_scores(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    scores = GameScore.query.filter_by(user_id=user.id).order_by(GameScore.created_at.desc()).all()
    return jsonify({
        'userId': user.id,
        'scores': [s.to_dict() for s in scores]
    }), 200


@auth_bp.route('/', methods=['GET', 'HEAD'])
def index():
    return jsonify({
        'service': 'RetroGames Authentication Service',
        'status': 'healthy',
        'endpoints': {
            'health': '/health',
            'register': 'POST /register',
            'login': 'POST /login',
            'users': 'GET /users',
            'record_score': 'POST /scores',
            'game_scores': 'GET /scores/<game_id>',
            'user_scores': 'GET /users/<user_id>/scores'
        }
    }), 200


@auth_bp.route('/health', methods=['GET', 'HEAD'])
def health():
    return jsonify({'status': 'healthy'}), 200
