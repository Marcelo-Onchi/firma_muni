# app/routes/auth_routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.models import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("sig.listar_firmas"))
    return render_template("login.html")


@auth_bp.post("/login")
def login_post():
    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = Usuario.query.filter_by(email=email, activo=True).first()
    if not user or not user.check_password(password):
        flash("Credenciales inválidas.", "danger")
        return redirect(url_for("auth.login"))

    login_user(user)
    return redirect(url_for("sig.listar_firmas"))


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("auth.login"))
