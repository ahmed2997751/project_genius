"""Configuration module for ProjectGenius application."""
import os
from pathlib import Path

class Config:
    """Base configuration."""

    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://mokwa:simple1234@localhost:5432/projectgenius')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

    # Authentication
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'change-this-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days

    # AI Services
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-7a45473cf92f47299f8fc23ee5df6667')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'deepseek')
    AI_MODEL_NAME = os.environ.get('AI_MODEL_NAME', 'deepseek-chat')
    AI_MAX_TOKENS = int(os.environ.get('AI_MAX_TOKENS', 1000))

    # File Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = Path(__file__).parent.parent.parent / 'instance' / 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Security in production
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 12

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DEVELOPMENT = True

    # Development settings
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    BCRYPT_LOG_ROUNDS = 4  # Lower rounds for faster tests

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True

    # Use SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Security settings for testing
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = False
