# app/__init__.py
import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app() -> Flask:
    load_dotenv()

    base_dir = os.path.abspath(os.path.dirname(__file__))  # .../firma_muni/app

    templates_dir = os.path.join(base_dir, "templates")
    static_dir = os.path.join(base_dir, "static")

    app = Flask(
        __name__,
        template_folder=templates_dir,
        static_folder=static_dir,
        static_url_path="/static",
    )
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)
    os.makedirs(app.config["EXPORT_DIR"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import Usuario  # noqa: F401

    @login_manager.user_loader
    def load_user(user_id: str):
        return Usuario.query.get(int(user_id))

    from app.routes.auth_routes import auth_bp
    from app.routes.signature_routes import sig_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(sig_bp)

    with app.app_context():
        db.create_all()
        from app.models import Usuario

        if not Usuario.query.filter_by(email="admin@municunco.local").first():
            admin = Usuario.crear_admin_inicial()
            db.session.add(admin)
            db.session.commit()

    return app
