# app/models.py
from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    rol = db.Column(db.String(30), nullable=False, default="editor")  # admin | editor
    activo = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    firmas = db.relationship("Firma", backref="usuario", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def crear_admin_inicial() -> "Usuario":
        """
        Admin inicial para no quedar bloqueado.
        IMPORTANTE: cambia esta clave después del primer ingreso.
        """
        u = Usuario(
            nombre="Administrador",
            email="admin@municunco.local",
            rol="admin",
            activo=True,
        )
        u.set_password("Admin2026!")  # Cambiar al primer ingreso
        return u


class Firma(db.Model):
    __tablename__ = "firmas"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    # Datos visibles
    nombre = db.Column(db.String(140), nullable=False)
    cargo = db.Column(db.String(140), nullable=True)
    unidad = db.Column(db.String(140), nullable=True)
    telefono = db.Column(db.String(60), nullable=True)
    correo = db.Column(db.String(180), nullable=True)
    web = db.Column(db.String(180), nullable=True)

    # Estilo
    plantilla = db.Column(db.String(50), nullable=False, default="clasica")
    color_base = db.Column(db.String(20), nullable=False, default="#1f4e79")

    # Archivos (rutas relativas a /static)
    logo_path = db.Column(db.String(255), nullable=True)
    firma_path = db.Column(db.String(255), nullable=True)

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
