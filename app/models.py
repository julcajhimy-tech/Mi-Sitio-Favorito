from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(60), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    messages = db.relationship("Message", back_populates="author", cascade="all, delete-orphan")

    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(1000), nullable=True)
    media_url = db.Column(db.String(255), nullable=True)
    message_type = db.Column(db.String(20), nullable=False, default="text")
    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)

    author = db.relationship("User", back_populates="messages")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "body": self.body,
            "media_url": self.media_url,
            "message_type": self.message_type,
            "author_id": self.author_id,
            "author_name": self.author.display_name,
            "created_at": self.created_at.isoformat(),
        }# Comentario de prueba para forzar la detección de cambios
