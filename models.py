from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
import bcrypt

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str, rounds: int = 10) -> None:
        """Hash password using bcrypt with salt rounds matching the original service."""
        salt = bcrypt.gensalt(rounds=rounds)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password: str) -> bool:
        """Verify the input password against the stored bcrypt hash."""
        if not self.password_hash or not password:
            return False
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email
        }


class GameScore(db.Model):
    __tablename__ = 'game_scores'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('scores', lazy=True))

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'userId': self.user_id,
            'gameId': self.game_id,
            'score': self.score,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }
