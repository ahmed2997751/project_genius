"""Error handlers for the ProjectGenius application."""
from flask import render_template, jsonify, request


def register_error_handlers(app):
    """Register error handlers for the application."""

    def is_api_request():
        """Check if the request is for the API."""
        return request.path.startswith('/api/')

    def render_error(error, code, description):
        """Render error response based on request type."""
        if is_api_request():
            return jsonify({
                'error': error,
                'description': description,
                'code': code
            }), code
        return render_template('errors/{}.html'.format(code),
                            error=error,
                            description=description), code

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_error('Bad Request', 400,
                          'The request could not be processed.')

    @app.errorhandler(401)
    def unauthorized_error(error):
        return render_error('Unauthorized', 401,
                          'Authentication is required to access this resource.')

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_error('Forbidden', 403,
                          'You do not have permission to access this resource.')

    @app.errorhandler(404)
    def not_found_error(error):
        return render_error('Not Found', 404,
                          'The requested resource could not be found.')

    @app.errorhandler(405)
    def method_not_allowed_error(error):
        return render_error('Method Not Allowed', 405,
                          'The method is not allowed for this resource.')

    @app.errorhandler(429)
    def too_many_requests_error(error):
        return render_error('Too Many Requests', 429,
                          'You have exceeded the rate limit.')

    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f'Server Error: {error}')
        return render_error('Internal Server Error', 500,
                          'An unexpected error has occurred.')

    @app.errorhandler(503)
    def service_unavailable_error(error):
        return render_error('Service Unavailable', 503,
                          'The service is temporarily unavailable.')
