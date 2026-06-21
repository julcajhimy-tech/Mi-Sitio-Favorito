import getpass

from app import create_app, db
from app.models import User

app = create_app()


def ask_user(number: int) -> User:
    username = input(f"Usuario {number}: ").strip().lower()
    display_name = input(f"Nombre visible {number}: ").strip()
    password = getpass.getpass(f"Contraseña de {username}: ")
    confirm = getpass.getpass("Confirmar contraseña: ")

    if not username or not display_name or not password:
        raise ValueError("Todos los campos son obligatorios.")
    if len(username) < 3 or len(username) > 30:
        raise ValueError("El usuario debe tener entre 3 y 30 caracteres.")
    if len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres.")
    if password != confirm:
        raise ValueError("Las contraseñas no coinciden.")

    user = User(username=username, display_name=display_name)
    user.set_password(password)
    return user


with app.app_context():
    db.drop_all()
    db.create_all()
    print("Crea exactamente dos usuarios autorizados para el chat privado.\n")
    users = [ask_user(1), ask_user(2)]
    db.session.add_all(users)
    db.session.commit()
    print("Usuarios creados correctamente. Ya puedes ejecutar: python run.py")
