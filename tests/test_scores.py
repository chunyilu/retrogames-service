import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User, GameScore


class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret'


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user(client):
    res = client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    return res.get_json()['userId']


def test_record_score_success(client, sample_user):
    response = client.post('/scores', json={
        'userId': sample_user,
        'gameId': 'pacman',
        'score': 1500
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Score recorded successfully!'
    assert data['score']['userId'] == sample_user
    assert data['score']['gameId'] == 'pacman'
    assert data['score']['score'] == 1500
    assert 'createdAt' in data['score']


def test_record_score_snake_case(client, sample_user):
    response = client.post('/scores', json={
        'user_id': sample_user,
        'game_id': 'space-invaders',
        'score': 2000
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['score']['gameId'] == 'space-invaders'
    assert data['score']['score'] == 2000


def test_record_score_missing_fields(client, sample_user):
    response = client.post('/scores', json={
        'userId': sample_user,
        'gameId': 'pacman'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'userId, gameId, and score are required.'}


def test_record_score_invalid_score(client, sample_user):
    response = client.post('/scores', json={
        'userId': sample_user,
        'gameId': 'pacman',
        'score': 'not-a-number'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Score must be an integer.'}


def test_record_score_nonexistent_user(client):
    response = client.post('/scores', json={
        'userId': 9999,
        'gameId': 'pacman',
        'score': 500
    })
    assert response.status_code == 404
    assert response.get_json() == {'error': 'User not found.'}


def test_get_game_scores_and_leaderboard(client, sample_user):
    # Register a second user
    res2 = client.post('/register', json={
        'email': 'player2@retro.net',
        'password': 'password123'
    })
    user2_id = res2.get_json()['userId']

    # Record scores for pacman
    client.post('/scores', json={'userId': sample_user, 'gameId': 'pacman', 'score': 100})
    client.post('/scores', json={'userId': user2_id, 'gameId': 'pacman', 'score': 300})
    client.post('/scores', json={'userId': sample_user, 'gameId': 'pacman', 'score': 200})
    # Record score for another game
    client.post('/scores', json={'userId': sample_user, 'gameId': 'tetris', 'score': 500})

    # Test /scores/pacman
    response = client.get('/scores/pacman')
    assert response.status_code == 200
    data = response.get_json()
    assert data['gameId'] == 'pacman'
    scores = data['scores']
    assert len(scores) == 3
    # Check descending order: 300, 200, 100
    assert [s['score'] for s in scores] == [300, 200, 100]

    # Test leaderboard alias with limit
    response_lb = client.get('/scores/leaderboard/pacman?limit=2')
    assert response_lb.status_code == 200
    lb_data = response_lb.get_json()
    assert len(lb_data['scores']) == 2
    assert [s['score'] for s in lb_data['scores']] == [300, 200]


def test_get_user_scores(client, sample_user):
    client.post('/scores', json={'userId': sample_user, 'gameId': 'pacman', 'score': 150})
    client.post('/scores', json={'userId': sample_user, 'gameId': 'tetris', 'score': 450})

    response = client.get(f'/users/{sample_user}/scores')
    assert response.status_code == 200
    data = response.get_json()
    assert data['userId'] == sample_user
    assert len(data['scores']) == 2
    game_ids = [s['gameId'] for s in data['scores']]
    assert 'pacman' in game_ids
    assert 'tetris' in game_ids


def test_get_user_scores_nonexistent_user(client):
    response = client.get('/users/9999/scores')
    assert response.status_code == 404
    assert response.get_json() == {'error': 'User not found.'}
