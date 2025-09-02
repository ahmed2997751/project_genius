from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import os
from pathlib import Path

class Base(DeclarativeBase):
    pass

# Initialize Flask extensions
db = SQLAlchemy(model_class=Base)
migrate = Migrate()

def create_app(config_name=None):
    """Application factory pattern to create Flask app instance."""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), "templates"),
        static_folder=os.path.join(os.path.dirname(__file__), "static"),
    )


    # Load configuration based on environment
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    config_module = f"projectgenius.core.config.{config_name.capitalize()}Config"
    app.config.from_object(config_module)

    # Ensure instance folder exists
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Enable proxy fix for proper URL generation behind proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Register blueprints
    from projectgenius.auth import auth_bp
    from projectgenius.core import core_bp
    from projectgenius.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    from projectgenius.quizzes import quizzes_bp
    app.register_blueprint(quizzes_bp)

    # Register error handlers
    from projectgenius.core.errors import register_error_handlers
    register_error_handlers(app)

    # Register CLI commands
    from projectgenius.core.cli import register_cli_commands
    register_cli_commands(app)

    return app
