# app/config.py
import os


class Config:
    """
    Configuración:
    - Desarrollo (Windows): SQLite automático por defecto.
    - Producción (Ubuntu): PostgreSQL cuando DB_NAME viene definido en .env.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # Si DB_NAME existe, usamos PostgreSQL. Si no, usamos SQLite local.
    DB_NAME = (os.getenv("DB_NAME") or "").strip()

    if DB_NAME:
        DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
        DB_PORT = os.getenv("DB_PORT", "5432")
        DB_USER = os.getenv("DB_USER", "firmas_user")
        DB_PASS = os.getenv("DB_PASS", "")

        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        # DEV local: base SQLite en el mismo repo
        SQLALCHEMY_DATABASE_URI = "sqlite:///firma_muni_dev.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join("app", "static", "uploads"))
    EXPORT_DIR = os.getenv("EXPORT_DIR", os.path.join("app", "static", "exports"))

    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3MB
    ALLOWED_IMAGE_EXTS = {"png", "jpg", "jpeg", "webp"}

    DEFAULT_BRAND_COLOR = "#1f4e79"
    DEFAULT_TEMPLATE = "clasica"
