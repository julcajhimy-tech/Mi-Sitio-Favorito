from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
socketio = SocketIO(async_mode="gevent", cors_allowed_origins="*")


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Inicia sesión para acceder al chat privado."
    login_manager.login_message_category = "info"
    socketio.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    from .routes import main_bp
    app.register_blueprint(main_bp)

    from . import socket_events  # noqa: F401

    return app