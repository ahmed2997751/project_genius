"""Quizzes module for ProjectGenius application."""
from flask import Blueprint

quizzes_bp = Blueprint('quizzes', __name__, url_prefix='/quizzes', template_folder='templates')

# Import routes after blueprint creation to avoid circular imports

