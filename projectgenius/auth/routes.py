"""Authentication routes for ProjectGenius application."""
from flask import (
    redirect, request, url_for, flash, session,
    render_template, jsonify
)
from functools import wraps
from projectgenius.auth import auth_bp
from projectgenius.models import User, db
from projectgenius.auth.forms import LoginForm, RegisterForm

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def init_session(user):
    """Initialize user session."""
    session['user_id'] = user.id
    session['username'] = user.username
    session['is_admin'] = user.is_admin

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if 'user_id' in session:
        return redirect(url_for('core.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            init_session(user)
            flash('Successfully logged in!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('core.dashboard'))

        flash('Invalid username or password', 'error')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if 'user_id' in session:
        return redirect(url_for('core.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html', form=form)

        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html', form=form)

        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            password=form.password.data
        )

        db.session.add(user)
        db.session.commit()

        init_session(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('core.dashboard'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    """Log out user and clear session."""
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('core.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Return user profile information."""
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        flash('User not found. Please log in again.', 'error')
        return redirect(url_for('auth.login'))

    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'avatar_url': user.avatar_url,
            'created_at': user.created_at.isoformat()
        })

    return render_template('auth/profile.html', user=user)

@auth_bp.route('/check')
def check_auth():
    """Check authentication status."""
    return jsonify({
        'authenticated': 'user_id' in session,
        'username': session.get('username'),
        'is_admin': session.get('is_admin', False)
    })

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Handle password change."""
    if not request.is_json:
        return jsonify({'error': 'Invalid request format'}), 400

    data = request.get_json()
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({'error': 'Missing required fields'}), 400

    user = User.query.get(session['user_id'])
    if not user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401

    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password updated successfully'})
