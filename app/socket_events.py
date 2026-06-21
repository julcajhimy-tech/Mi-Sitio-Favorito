from flask import request
from flask_login import current_user
from flask_socketio import disconnect, emit, join_room

from . import db, socketio
from .models import Message

CHAT_ROOM = "private-two-person-room"


@socketio.on("connect")
def handle_connect(auth=None):
    if not current_user.is_authenticated:
        return False
    join_room(CHAT_ROOM)
    emit("presence", {"username": current_user.display_name, "status": "online"}, room=CHAT_ROOM)


@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        emit("presence", {"username": current_user.display_name, "status": "offline"}, room=CHAT_ROOM)


@socketio.on("send_message")
def handle_send_message(payload):
    if not current_user.is_authenticated:
        disconnect()
        return

    body = str((payload or {}).get("body", "")).strip()
    if not body:
        return
    if len(body) > 1000:
        emit("message_error", {"message": "El mensaje no puede superar los 1000 caracteres."})
        return

    message = Message(body=body, author_id=current_user.id)
    db.session.add(message)
    db.session.commit()
    emit("new_message", message.to_dict(), room=CHAT_ROOM)
