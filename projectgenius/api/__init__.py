"""API module for ProjectGenius application."""
from flask import Blueprint

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register routes

