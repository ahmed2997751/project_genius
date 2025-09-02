"""Core module for ProjectGenius application."""
from flask import Blueprint

core_bp = Blueprint('core', __name__)

# Import routes after blueprint creation to avoid circular imports
from projectgenius.core import routes  # noqa: F401
