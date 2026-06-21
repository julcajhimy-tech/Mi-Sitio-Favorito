import os
from app import create_app, db
from app.models import User

# Creamos un contexto de la aplicación Flask para poder interactuar con la base de datos
app = create_app()

with app.app_context():
    print("Iniciando proceso de creación de usuarios desde variables de entorno...")

    # --- Usuario 1 ---
    username_1 = os.environ.get('USER1_NAME')
    display_name_1 = os.environ.get('USER1_DISPLAY_NAME')
    password_1 = os.environ.get('USER1_PASS')

    if all([username_1, display_name_1, password_1]):
        # Revisa si el usuario ya existe para no crearlo de nuevo
        if not User.query.filter_by(username=username_1).first():
            user = User(username=username_1, display_name=display_name_1)
            user.set_password(password_1)
            db.session.add(user)
            print(f"-> Usuario '{username_1}' creado con éxito.")
        else:
            print(f"-> Usuario '{username_1}' ya existe. No se realizaron cambios.")
    else:
        print("-> Faltan variables de entorno para el Usuario 1 (USER1_NAME, USER1_DISPLAY_NAME, USER1_PASS).")

    # --- Usuario 2 ---
    username_2 = os.environ.get('USER2_NAME')
    display_name_2 = os.environ.get('USER2_DISPLAY_NAME')
    password_2 = os.environ.get('USER2_PASS')

    if all([username_2, display_name_2, password_2]):
        # Revisa si el usuario ya existe
        if not User.query.filter_by(username=username_2).first():
            user = User(username=username_2, display_name=display_name_2)
            user.set_password(password_2)
            db.session.add(user)
            print(f"-> Usuario '{username_2}' creado con éxito.")
        else:
            print(f"-> Usuario '{username_2}' ya existe. No se realizaron cambios.")
    else:
        print("-> Faltan variables de entorno para el Usuario 2 (USER2_NAME, USER2_DISPLAY_NAME, USER2_PASS).")

    # Guarda todos los cambios en la base de datos
    db.session.commit()
    print("Proceso de creación de usuarios finalizado.")