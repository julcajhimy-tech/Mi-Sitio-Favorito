# Chat privado para dos personas

Aplicación web responsiva para una conversación privada entre dos cuentas autorizadas. Incluye inicio de sesión, contraseñas cifradas, mensajes persistentes en SQLite y actualización en tiempo real con Flask-SocketIO.

## Funciones incluidas

- Dos usuarios autorizados creados desde la terminal (sin registro público).
- Inicio y cierre de sesión.
- Contraseñas con hash seguro, nunca almacenadas en texto plano.
- Chat en tiempo real mediante WebSockets.
- Historial de mensajes guardado en SQLite.
- Interfaz adaptable a computadora, tablet y celular.
- Estructura modular: rutas, modelos, eventos Socket.IO y configuración separados.
- Pruebas básicas con `pytest`.

## Requisitos

- Python 3.10 o superior.
- Visual Studio Code con la extensión **Python**.

## Ejecución en Visual Studio Code (Windows)

También puedes ejecutar las tareas preconfiguradas desde **Terminal > Run Task**: `Instalar proyecto`, `Crear dos usuarios`, `Ejecutar chat` y `Probar proyecto`.

1. Descomprime el proyecto y abre la carpeta `private_two_person_chat` con Visual Studio Code.
2. Abre la terminal integrada: **Terminal > New Terminal**.
3. Crea el entorno virtual:

```powershell
py -m venv .venv
```

4. Actívalo:

```powershell
.\.venv\Scripts\Activate.ps1
```

> Si PowerShell bloquea la activación, ejecuta una sola vez:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```

5. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

6. Copia `.env.example` como `.env` y cambia `SECRET_KEY` por una clave larga y única.

> Los archivos `scripts/setup_windows.ps1`, `scripts/run_windows.ps1` y `scripts/test_windows.ps1` automatizan estos pasos en PowerShell.

7. Crea las dos cuentas del chat (este comando borra la base de datos anterior):

```powershell
python scripts/create_users.py
```

8. Ejecuta la aplicación:

```powershell
python run.py
```

9. Abre en el navegador: `http://127.0.0.1:5000`

## Ejecución en macOS o Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/create_users.py
python run.py
```

## Ejecutar las pruebas

```powershell
pytest
```

## Datos y persistencia

Los mensajes y usuarios se guardan en `instance/private_chat.db`. Mientras conserves este archivo, los datos no se perderán al cerrar el programa. Haz copias de seguridad periódicas de la carpeta `instance`.

## Para usarlo en internet de forma segura

Antes de publicar el proyecto, cambia `SECRET_KEY`, habilita HTTPS, configura una base de datos gestionada como PostgreSQL, restringe las variables de entorno y usa un servidor de producción compatible con WebSockets. No uses el modo `debug=True` en producción.

## Posibles mejoras escalables

- Conversaciones separadas y grupos privados.
- Mensajes con imágenes o archivos, almacenados en nube.
- Confirmación de lectura y “está escribiendo”.
- Recuperación de contraseña por correo.
- PostgreSQL + migraciones con Alembic/Flask-Migrate.
- Rate limiting, CSRF y auditoría de accesos.
