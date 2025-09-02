"""User API endpoints for ProjectGenius application."""
from flask import jsonify, request, current_app
from projectgenius.api import api_bp
from projectgenius.auth.routes import login_required
from projectgenius.models import User, db
from projectgenius.utils import require_api_key


@api_bp.route('/users/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get current user profile."""
    return jsonify({
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'full_name': request.user.full_name,
        'avatar_url': request.user.avatar_url,
        'is_premium': request.user.is_premium,
        'bio': request.user.bio,
        'created_at': request.user.created_at.isoformat()
    })


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """Get user by ID (admin only)."""
    if not request.user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_active': user.is_active,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat()
    })


@api_bp.route('/users', methods=['GET'])
@require_api_key
def list_users():
    """List users (admin only)."""
    if not request.user or not request.user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)

    users = User.query.paginate(page=page, per_page=per_page)

    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'created_at': user.created_at.isoformat()
        } for user in users.items],
        'pagination': {
            'page': users.page,
            'pages': users.pages,
            'total': users.total,
            'per_page': users.per_page
        }
    })


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """Update user profile."""
    user = User.query.get_or_404(user_id)

    # Users can only update their own profile unless they're admin
    if user.id != request.user.id and not request.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    # Update allowed fields
    allowed_fields = ['full_name', 'bio', 'avatar_url']
    if request.user.is_admin:
        allowed_fields.extend(['is_active', 'is_admin'])

    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'User updated successfully',
        'user_id': user.id
    })


@api_bp.route('/users/stats', methods=['GET'])
@require_api_key
def user_stats():
    """Get user statistics."""
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    premium_users = User.query.filter_by(is_premium=True).count()
    admin_users = User.query.filter_by(is_admin=True).count()

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'premium_users': premium_users,
        'admin_users': admin_users,
        'regular_users': total_users - admin_users
    })