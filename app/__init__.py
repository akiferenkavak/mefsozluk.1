# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from config import Config
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfaya erişmek için giriş yapmalısınız.'
    mail.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Blueprints
    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.entry import bp as entry_bp
    from app.routes.user import bp as user_bp
    from app.routes.admin import admin_bp
    from app.routes.api import bp as api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(entry_bp, url_prefix='/entry')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    csrf.exempt('api.toggle_favorite')
    csrf.exempt('api.delete_entry')
    
    return app

# User loader
@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))