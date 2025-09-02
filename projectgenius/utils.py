"""Utility functions for ProjectGenius application."""
import re
import uuid
from typing import Optional, Union
from datetime import datetime, timedelta
import bleach
import markdown
from functools import wraps
from flask import current_app, request, jsonify
import jwt
from werkzeug.utils import secure_filename

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving the original extension."""
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
    return f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if a filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks."""
    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'hr', 'a', 'img'
    ]
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height']
    }
    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attributes)

def markdown_to_html(text: str) -> str:
    """Convert markdown text to sanitized HTML."""
    html = markdown.markdown(text, extensions=['extra', 'codehilite', 'tables'])
    return sanitize_html(html)

def format_datetime(dt: datetime, format_str: Optional[str] = None) -> str:
    """Format datetime object to string."""
    if format_str is None:
        format_str = '%Y-%m-%d %H:%M:%S'
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: Optional[str] = None) -> datetime:
    """Parse datetime string to datetime object."""
    if format_str is None:
        format_str = '%Y-%m-%d %H:%M:%S'
    return datetime.strptime(date_str, format_str)

def calculate_time_elapsed(start_time: datetime) -> str:
    """Calculate human-readable time elapsed from start_time."""
    now = datetime.utcnow()
    diff = now - start_time

    if diff < timedelta(minutes=1):
        return 'just now'
    elif diff < timedelta(hours=1):
        minutes = diff.seconds // 60
        return f'{minutes} minute{"s" if minutes != 1 else ""} ago'
    elif diff < timedelta(days=1):
        hours = diff.seconds // 3600
        return f'{hours} hour{"s" if hours != 1 else ""} ago'
    elif diff < timedelta(days=30):
        days = diff.days
        return f'{days} day{"s" if days != 1 else ""} ago'
    elif diff < timedelta(days=365):
        months = diff.days // 30
        return f'{months} month{"s" if months != 1 else ""} ago'
    else:
        years = diff.days // 365
        return f'{years} year{"s" if years != 1 else ""} ago'

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def generate_jwt_token(user_id: Union[int, str], expiration: Optional[int] = None) -> str:
    """Generate JWT token for user authentication."""
    if expiration is None:
        expiration = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)

    payload = {
        'user_id': str(user_id),
        'exp': datetime.utcnow() + timedelta(seconds=expiration),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload if valid."""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_api_key(f):
    """Decorator to require API key for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key is missing'}), 401

        # Import here to avoid circular imports
        from projectgenius.models import User
        user = User.query.filter_by(api_key=api_key, is_active=True).first()
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401

        return f(*args, **kwargs)
    return decorated_function

def rate_limit(limit: int, per: int):
    """Decorator to implement rate limiting for routes."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This is a simplified version. In production, use Redis or similar
            # to implement proper rate limiting
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"

def is_safe_redirect_url(url: str) -> bool:
    """Check if URL is safe for redirects to prevent open redirects."""
    if not url:
        return False

    # Check if it's a relative URL
    if url.startswith('/'):
        return True

    # Check if it's a URL to the same site
    allowed_hosts = current_app.config.get('ALLOWED_REDIRECT_HOSTS', [])
    from urllib.parse import urlparse
    try:
        parsed = urlparse(url)
        return parsed.netloc in allowed_hosts
    except:
        return False

def mask_sensitive_data(data: dict, fields: list) -> dict:
    """Mask sensitive data in dictionary."""
    masked_data = data.copy()
    for field in fields:
        if field in masked_data:
            masked_data[field] = '****'
    return masked_data

def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password meets all requirements"
