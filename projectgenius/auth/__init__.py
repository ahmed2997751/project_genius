"""Authentication module for ProjectGenius application."""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')

from projectgenius.auth import routes  # noqa: F401
