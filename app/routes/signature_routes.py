# app/routes/signature_routes.py
import os
import uuid

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
    send_from_directory,
)
from flask_login import login_required, current_user

from app import db
from app.models import Firma


sig_bp = Blueprint("sig", __name__)


def _allowed_ext(filename: str) -> bool:
    ext = (filename.rsplit(".", 1)[-1] or "").lower()
    return ext in current_app.config["ALLOWED_IMAGE_EXTS"]


def _save_upload(file_storage, subfolder: str) -> str | None:
    """
    Guarda un archivo en /static/uploads/<subfolder> con nombre UUID.
    Retorna la ruta relativa a /static (ej: 'uploads/logos/xxx.png')
    """
    if not file_storage or not file_storage.filename:
        return None

    if not _allowed_ext(file_storage.filename):
        return None

    ext = file_storage.filename.rsplit(".", 1)[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_root = current_app.config["UPLOAD_DIR"]
    folder = os.path.join(upload_root, subfolder)
    os.makedirs(folder, exist_ok=True)

    abs_path = os.path.join(folder, filename)
    file_storage.save(abs_path)

    return f"uploads/{subfolder}/{filename}"


@sig_bp.get("/")
@login_required
def home():
    return redirect(url_for("sig.listar_firmas"))


@sig_bp.get("/firmas")
@login_required
def listar_firmas():
    firmas = (
        Firma.query.filter_by(user_id=current_user.id)
        .order_by(Firma.updated_at.desc())
        .all()
    )
    return render_template("signature_list.html", firmas=firmas)


@sig_bp.get("/firmas/nueva")
@login_required
def nueva_firma():
    return render_template(
        "signature_editor.html",
        firma=None,
        default_color=current_app.config["DEFAULT_BRAND_COLOR"],
        default_template=current_app.config["DEFAULT_TEMPLATE"],
    )


@sig_bp.post("/firmas/nueva")
@login_required
def nueva_firma_post():
    nombre = (request.form.get("nombre") or "").strip()
    if not nombre:
        flash("El nombre es obligatorio.", "danger")
        return redirect(url_for("sig.nueva_firma"))

    logo_rel = _save_upload(request.files.get("logo"), "logos")
    firma_rel = _save_upload(request.files.get("firma_img"), "firmas")

    f = Firma(
        user_id=current_user.id,
        nombre=nombre,
        cargo=(request.form.get("cargo") or "").strip() or None,
        unidad=(request.form.get("unidad") or "").strip() or None,
        telefono=(request.form.get("telefono") or "").strip() or None,
        correo=(request.form.get("correo") or "").strip() or None,
        web=(request.form.get("web") or "").strip() or None,
        plantilla=(request.form.get("plantilla") or "clasica").strip(),
        color_base=(request.form.get("color_base") or "#1f4e79").strip(),
        logo_path=logo_rel,
        firma_path=firma_rel,
        is_active=True,
    )
    db.session.add(f)
    db.session.commit()

    flash("Firma creada.", "success")
    return redirect(url_for("sig.editar_firma", firma_id=f.id))


@sig_bp.get("/firmas/<int:firma_id>/editar")
@login_required
def editar_firma(firma_id: int):
    firma = Firma.query.filter_by(id=firma_id, user_id=current_user.id).first_or_404()
    return render_template(
        "signature_editor.html",
        firma=firma,
        default_color=current_app.config["DEFAULT_BRAND_COLOR"],
        default_template=current_app.config["DEFAULT_TEMPLATE"],
    )


@sig_bp.post("/firmas/<int:firma_id>/editar")
@login_required
def editar_firma_post(firma_id: int):
    firma = Firma.query.filter_by(id=firma_id, user_id=current_user.id).first_or_404()

    nombre = (request.form.get("nombre") or "").strip()
    if not nombre:
        flash("El nombre es obligatorio.", "danger")
        return redirect(url_for("sig.editar_firma", firma_id=firma.id))

    # Archivos opcionales (si sube, reemplaza)
    new_logo = _save_upload(request.files.get("logo"), "logos")
    new_firma = _save_upload(request.files.get("firma_img"), "firmas")

    firma.nombre = nombre
    firma.cargo = (request.form.get("cargo") or "").strip() or None
    firma.unidad = (request.form.get("unidad") or "").strip() or None
    firma.telefono = (request.form.get("telefono") or "").strip() or None
    firma.correo = (request.form.get("correo") or "").strip() or None
    firma.web = (request.form.get("web") or "").strip() or None
    firma.plantilla = (request.form.get("plantilla") or "clasica").strip()
    firma.color_base = (request.form.get("color_base") or "#1f4e79").strip()

    if new_logo:
        firma.logo_path = new_logo
    if new_firma:
        firma.firma_path = new_firma

    db.session.commit()
    flash("Firma actualizada.", "success")
    return redirect(url_for("sig.editar_firma", firma_id=firma.id))


@sig_bp.post("/firmas/<int:firma_id>/toggle")
@login_required
def toggle_firma(firma_id: int):
    firma = Firma.query.filter_by(id=firma_id, user_id=current_user.id).first_or_404()
    firma.is_active = not firma.is_active
    db.session.commit()
    flash("Estado actualizado.", "success")
    return redirect(url_for("sig.listar_firmas"))
