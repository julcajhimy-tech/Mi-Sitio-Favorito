from urllib.parse import urljoin, urlparse

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .models import Message, User

main_bp = Blueprint("main", __name__)


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
    messages = Message.query.order_by(Message.created_at.asc()).limit(200).all()
    return render_template(
        "chat.html",
        messages=messages,
        max_users=current_app.config["MAX_CHAT_USERS"],
    )


@main_bp.post("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("main.login"))
