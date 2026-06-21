from app import create_app, db
from app.models import User


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CHAT_USERS = 2


def make_app():
    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(username="persona1", display_name="Persona Uno")
        user.set_password("ContraseñaSegura123")
        db.session.add(user)
        db.session.commit()
    return app


def test_login_and_chat_access():
    app = make_app()
    client = app.test_client()

    protected = client.get("/chat")
    assert protected.status_code == 302

    response = client.post(
        "/login",
        data={"username": "persona1", "password": "ContraseñaSegura123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Chat seguro" in response.data


def test_invalid_login_rejected():
    app = make_app()
    client = app.test_client()
    response = client.post("/login", data={"username": "persona1", "password": "incorrecta"})
    assert response.status_code == 401
