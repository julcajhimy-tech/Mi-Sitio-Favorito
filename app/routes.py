import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import cloudinary
import cloudinary.uploader
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from . import db, socketio
from .models import Message, User

main_bp = Blueprint("main", __name__)

# --- Configuración de Media ---
MEDIA_CONFIG = {
    "image": {"extensions": {"jpg", "jpeg", "png", "gif"}, "folder": "chat/images", "resource_type": "image"},
    "audio": {"extensions": {"mp3", "wav", "ogg", "m4a", "webm"}, "folder": "chat/audio", "resource_type": "video"},
    "document": {"extensions": {"pdf", "doc", "docx", "txt"}, "folder": "chat/documents", "resource_type": "raw"},
}

def _get_media_config(filename: str) -> tuple[str | None, str | None, str | None]:
    """Determina el tipo de mensaje, la carpeta y el tipo de recurso según la extensión."""
    extension = filename.rsplit(".", 1)[-1].lower()
    for media_type, config in MEDIA_CONFIG.items():
        if extension in config["extensions"]:
            return media_type, config["folder"], config["resource_type"]
    return None, None, None


def is_safe_redirect_url(target: str) -> bool:
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))
    return redirect_url.scheme in {"http", "https"} and host_url.netloc == redirect_url.netloc


@main_bp.route("/")
def index():
    return redirect(url_for("main.chat" if current_user.is_authenticated else "main.login"))


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.chat"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password) or not user.is_active:
            flash("Usuario o contraseña incorrectos.", "error")
            return render_template("login.html"), 401

        login_user(user, remember=False)
        next_url = request.args.get("next")
        return redirect(next_url if next_url and is_safe_redirect_url(next_url) else url_for("main.chat"))

    return render_template("login.html")


@main_bp.route("/chat")
@login_required
def chat():
    # Eliminar mensajes con más de 7 días de antigüedad
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    Message.query.filter(Message.created_at < one_week_ago).delete()
    db.session.commit()

    messages = Message.query.order_by(Message.created_at.asc()).limit(200).all()
    return render_template(
        "chat.html",
        messages=messages,
        max_users=current_app.config["MAX_CHAT_USERS"],
    )


@main_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("main.login"))


@main_bp.route("/delete_message/<int:message_id>", methods=["DELETE"])
@login_required
def delete_message(message_id):
    message = db.session.get(Message, message_id)
    if not message:
        return jsonify({"error": "El mensaje no fue encontrado."}), 404
    if message.author_id != current_user.id:
        return jsonify({"error": "No tienes permiso para borrar este mensaje."}), 403

    db.session.delete(message)
    db.session.commit()

    socketio.emit("message_deleted", {"message_id": message_id})

    return jsonify({"success": True, "message": "Mensaje borrado."})


@main_bp.route("/upload_media", methods=["POST"])
@login_required
def upload_media():
    if "media_file" not in request.files:
        return jsonify({"error": "No se encontró ningún archivo."}), 400

    file = request.files["media_file"]
    if not file or not file.filename:
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    filename = secure_filename(file.filename)
    message_type, upload_folder, resource_type = _get_media_config(filename)

    if not message_type:
        return jsonify({"error": "Tipo de archivo no soportado."}), 415

    try:
        # Subir archivo a Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=upload_folder,
            resource_type=resource_type,
            public_id=uuid.uuid4().hex,  # Nombre de archivo único
        )
    except Exception as e:
        current_app.logger.error(f"Error al subir a Cloudinary: {e}")
        return jsonify({"error": "No se pudo subir el archivo al servidor externo."}), 500

    # --- Creación del mensaje en la BD ---
    media_url = upload_result.get("secure_url")
    if not media_url:
        return jsonify({"error": "No se pudo obtener la URL del archivo subido."}), 500

    body_content = filename if message_type in {"image", "document"} else None

    new_message = Message(
        author_id=current_user.id,
        message_type=message_type,
        media_url=media_url,
        body=body_content,
    )
    db.session.add(new_message)
    db.session.commit()

    socketio.emit("new_message", new_message.to_dict())

    return jsonify({"success": True, "message": "Archivo subido correctamente."})