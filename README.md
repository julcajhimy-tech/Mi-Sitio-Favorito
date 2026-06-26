# Chat Privado Seguro

Una aplicación de chat minimalista y segura para dos personas, construida con Flask y Socket.IO.

## Características

- **Comunicación en tiempo real:** Mensajería instantánea gracias a WebSockets (Socket.IO).
- **Compartir multimedia:** Envía y recibe imágenes, clips de audio y documentos de forma segura.
- **Notificaciones sonoras:** Recibe una alerta sonora sutil con cada nuevo mensaje.
- **Visualización de hora local:** Las marcas de tiempo de los mensajes se ajustan automáticamente a tu zona horaria.
- **Diseño limpio y accesible:** Interfaz de usuario minimalista y compatible con lectores de pantalla.
- **Persistencia de mensajes:** Los mensajes se guardan en una base de datos SQLite.

## Tecnologías utilizadas

- **Backend:**
  - Python 3
  - Flask
  - Flask-SocketIO
  - Flask-SQLAlchemy
  - Flask-Login
- **Frontend:**
  - HTML5
  - CSS (sin frameworks)
  - JavaScript (vanilla)
  - Socket.IO Client
- **Base de datos:**
  - SQLite

## Instalación y ejecución

1.  **Clona el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd private-two-person-chat
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv .venv
    # En Windows
    .venv\Scripts\activate
    # En macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Inicia la aplicación:**
    ```bash
    flask run
    ```

5.  Abre tu navegador y ve a `http://127.0.0.1:5000`.