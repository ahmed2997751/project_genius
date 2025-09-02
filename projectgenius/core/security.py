"""
Security utilities and middleware for ProjectGenius application.
"""
import re
import bleach
from flask import request, current_app, g
from functools import wraps
import logging
from datetime import datetime, timedelta, timezone
import ipaddress

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}


class SecurityManager:
    """Security utilities and validation functions."""

    @staticmethod
    def sanitize_html(text):
        """Sanitize HTML input to prevent XSS attacks."""
        if not text:
            return text

        # Allow only safe tags and attributes
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'
        ]

        allowed_attributes = {
            'a': ['href', 'title'],
            'img': ['src', 'alt', 'title']
        }

        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )

    @staticmethod
    def validate_email(email):
        """Validate email format and prevent common attacks."""
        if not email or not isinstance(email, str):
            return False

        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False

        # Check for suspicious patterns
        suspicious_patterns = [
            r'<.*>',  # HTML tags
            r'javascript:',  # JavaScript URLs
            r'data:',  # Data URLs
            r'\.\.',  # Directory traversal
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def validate_username(username):
        """Validate username format."""
        if not username or not isinstance(username, str):
            return False

        # Username requirements
        if len(username) < 3 or len(username) > 80:
            return False

        # Allow only alphanumeric characters, dots, dashes, and underscores
        if not re.match(r'^[\w.-]+$', username):
            return False

        # Prevent common reserved words
        reserved_words = [
            'admin', 'administrator', 'root', 'system', 'api', 'www',
            'mail', 'email', 'user', 'users', 'login', 'logout', 'register'
        ]

        if username.lower() in reserved_words:
            return False

        return True

    @staticmethod
    def validate_password(password):
        """Validate password strength."""
        if not password or not isinstance(password, str):
            return False, "Password is required"

        if len(password) < 8:
            return False, "Password must be at least 8 characters long"

        # Check for required character types
        has_upper = re.search(r'[A-Z]', password)
        has_lower = re.search(r'[a-z]', password)
        has_digit = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*()_+]', password)

        if not has_upper:
            return False, "Password must contain at least one uppercase letter"
        if not has_lower:
            return False, "Password must contain at least one lowercase letter"
        if not has_digit:
            return False, "Password must contain at least one number"
        if not has_special:
            return False, "Password must contain at least one special character"

        return True, "Password is valid"

    @staticmethod
    def is_suspicious_ip(ip_address):
        """Check if IP address is suspicious."""
        try:
            ip = ipaddress.ip_address(ip_address)

            # Check for private IPs (might indicate internal attacks)
            if ip.is_private:
                return True

            # Check for localhost
            if ip.is_loopback:
                return True

            return False
        except ValueError:
            return True  # Invalid IP format

    @staticmethod
    def rate_limit(key, limit=10, window=60):
        """Simple rate limiting (use Redis in production)."""
        now = datetime.now(timezone.utc)

        if key not in rate_limit_store:
            rate_limit_store[key] = []

        # Clean old entries
        rate_limit_store[key] = [
            timestamp for timestamp in rate_limit_store[key]
            if now - timestamp < timedelta(seconds=window)
        ]

        # Check if limit exceeded
        if len(rate_limit_store[key]) >= limit:
            return False

        # Add current request
        rate_limit_store[key].append(now)
        return True


def rate_limit_decorator(limit=10, window=60):
    """Decorator for rate limiting endpoints."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create rate limit key from IP and endpoint
            client_ip = request.remote_addr or 'unknown'
            endpoint = request.endpoint or 'unknown'
            key = f"{client_ip}:{endpoint}"

            if not SecurityManager.rate_limit(key, limit, window):
                logger.warning(f"Rate limit exceeded for {key}")
                return {
                    'error': 'Too many requests. Please try again later.'
                }, 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def security_headers_middleware():
    """Add security headers to responses."""
    def middleware(response):
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS protection
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy (basic)
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.replit.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdnjs.cloudflare.com;"
        )

        return response
    return middleware


def log_security_events():
    """Middleware to log security-related events."""
    client_ip = request.remote_addr or 'unknown'
    endpoint = request.endpoint or 'unknown'

    # Log suspicious activity
    if SecurityManager.is_suspicious_ip(client_ip):
        logger.warning(f"Suspicious IP access: {client_ip} - {endpoint}")

    # Log authentication attempts
    if endpoint and ('login' in endpoint or 'register' in endpoint):
        logger.info(f"Auth attempt from {client_ip}: {endpoint}")

    # Log API access
    if request.path.startswith('/api/'):
        logger.info(f"API access: {client_ip} - {endpoint}")


def _sanitize_dict_values(data_dict):
    """Helper function to sanitize string values in a dictionary."""
    for key, value in data_dict.items():
        if isinstance(value, str):
            data_dict[key] = SecurityManager.sanitize_html(value)
    return data_dict


def sanitize_input_middleware():
    """Middleware to sanitize user inputs."""
    if request.method not in ['POST', 'PUT', 'PATCH']:
        return

    if request.is_json:
        _sanitize_json_data()
    elif request.form:
        _sanitize_form_data()


def _sanitize_json_data():
    """Sanitize JSON request data."""
    data = request.get_json()
    if isinstance(data, dict):
        g.sanitized_data = _sanitize_dict_values(data)


def _sanitize_form_data():
    """Sanitize form request data."""
    sanitized_form = _sanitize_dict_values(dict(request.form))
    g.sanitized_form = sanitized_form