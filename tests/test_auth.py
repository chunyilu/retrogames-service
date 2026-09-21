import os
import sys
import pytest

# Add parent directory to path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db, User


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


def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json() == {'status': 'healthy'}


def test_register_success(client):
    response = client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'User registered successfully!'
    assert 'userId' in data
    assert isinstance(data['userId'], int)


def test_register_missing_email(client):
    response = client.post('/register', json={
        'password': 'password123'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Email and password are required.'}


def test_register_missing_password(client):
    response = client.post('/register', json={
        'email': 'player1@retro.net'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Email and password are required.'}


def test_register_empty_fields(client):
    response = client.post('/register', json={
        'email': '   ',
        'password': ''
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Email and password are required.'}


def test_register_duplicate_email(client):
    client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    response = client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'different_password'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Email already exists.'}


def test_login_success(client):
    client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Login successful!'
    assert data['user']['email'] == 'player1@retro.net'
    assert 'id' in data['user']


def test_login_wrong_password(client):
    client.post('/register', json={
        'email': 'player1@retro.net',
        'password': 'password123'
    })
    response = client.post('/login', json={
        'email': 'player1@retro.net',
        'password': 'wrong_password'
    })
    assert response.status_code == 401
    assert response.get_json() == {'error': 'Invalid email or password.'}


def test_login_nonexistent_user(client):
    response = client.post('/login', json={
        'email': 'unknown@retro.net',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert response.get_json() == {'error': 'Invalid email or password.'}


def test_login_missing_fields(client):
    response = client.post('/login', json={
        'email': 'player1@retro.net'
    })
    assert response.status_code == 400
    assert response.get_json() == {'error': 'Email and password are required.'}
