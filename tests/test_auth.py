"""
Authentication tests for ProjectGenius application.

This module contains unit tests for authentication functionality including
user registration, login, logout, and password management.
"""

import pytest
from flask import url_for, session
from projectgenius.models import User
from projectgenius import db


class TestUserModel:
    """Test the User model functionality."""

    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                username='newuser',
                email='newuser@example.com',
                full_name='New User',
                password='password123'
            )
            db.session.add(user)
            db.session.commit()

            # Verify user was created
            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.full_name == 'New User'
            assert user.is_active is True
            assert user.is_admin is False

    def test_password_hashing(self, app):
        """Test password hashing and verification."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            # Password should be hashed
            assert user.password_hash != 'password123'
            assert user.password_hash is not None

            # Should be able to verify correct password
            assert user.check_password('password123') is True
            assert user.check_password('wrongpassword') is False

    def test_api_key_generation(self, app):
        """Test API key generation."""
        with app.app_context():
            user = User(
                username='apiuser',
                email='api@example.com',
                password='password123'
            )

            # API key should be generated automatically
            assert user.api_key is not None
            assert len(user.api_key) == 64  # 32 bytes hex = 64 characters

    def test_user_representation(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                username='repruser',
                email='repr@example.com',
                password='password123'
            )

            assert str(user) == '<User repruser>'


class TestAuthenticationRoutes:
    """Test authentication routes and functionality."""

    def test_register_get(self, client):
        """Test GET request to register page."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data

    def test_register_post_success(self, client, app):
        """Test successful user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })

        # Should redirect after successful registration
        assert response.status_code == 302

        # Verify user was created in database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.full_name == 'New User'

    def test_register_post_duplicate_username(self, client, test_user):
        """Test registration with duplicate username."""
        response = client.post('/auth/register', data={
            'username': test_user.username,  # Duplicate username
            'email': 'different@example.com',
            'full_name': 'Different User',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })

        assert response.status_code == 200
        assert b'Username already exists' in response.data

    def test_register_post_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': test_user.email,  # Duplicate email
            'full_name': 'Different User',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })

        assert response.status_code == 200
        assert b'Email already registered' in response.data

    def test_register_post_password_mismatch(self, client):
        """Test registration with password confirmation mismatch."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'full_name': 'New User',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword!'
        })

        assert response.status_code == 200
        assert b'Passwords must match' in response.data

    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data

    def test_login_post_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'testpassword123'
        })

        # Should redirect after successful login
        assert response.status_code == 302

    def test_login_post_invalid_username(self, client):
        """Test login with invalid username."""
        response = client.post('/auth/login', data={
            'username': 'nonexistentuser',
            'password': 'password123'
        })

        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_login_post_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        response = client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'wrongpassword'
        })

        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

    def test_logout(self, authenticated_client):
        """Test user logout."""
        # Verify user is logged in first
        response = authenticated_client.get('/dashboard')
        assert response.status_code == 200

        # Logout
        response = authenticated_client.get('/auth/logout')
        assert response.status_code == 302  # Redirect after logout

        # Verify user is logged out
        response = authenticated_client.get('/dashboard', follow_redirects=True)
        assert b'Please log in' in response.data

    def test_login_required_decorator(self, client):
        """Test login_required decorator functionality."""
        # Try to access protected route without login
        response = client.get('/dashboard')
        assert response.status_code == 302  # Should redirect to login

        # Follow redirect
        response = client.get('/dashboard', follow_redirects=True)
        assert b'Please log in' in response.data

    def test_check_auth_status_authenticated(self, authenticated_client):
        """Test authentication status check for authenticated user."""
        response = authenticated_client.get('/auth/check')
        assert response.status_code == 200

        data = response.get_json()
        assert data['authenticated'] is True
        assert 'username' in data

    def test_check_auth_status_anonymous(self, client):
        """Test authentication status check for anonymous user."""
        response = client.get('/auth/check')
        assert response.status_code == 200

        data = response.get_json()
        assert data['authenticated'] is False

    def test_profile_route_authenticated(self, authenticated_client, test_user):
        """Test profile route for authenticated user."""
        response = authenticated_client.get('/auth/profile')
        assert response.status_code == 200

        data = response.get_json()
        assert data['username'] == test_user.username
        assert data['email'] == test_user.email

    def test_profile_route_unauthenticated(self, client):
        """Test profile route for unauthenticated user."""
        response = client.get('/auth/profile')
        assert response.status_code == 302  # Should redirect to login

    def test_change_password_success(self, authenticated_client, test_user, app):
        """Test successful password change."""
        response = authenticated_client.post('/auth/change-password', json={
            'current_password': 'testpassword123',
            'new_password': 'NewPassword123!'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert 'Password updated successfully' in data['message']

        # Verify password was actually changed
        with app.app_context():
            user = User.query.get(test_user.id)
            assert user.check_password('NewPassword123!') is True
            assert user.check_password('testpassword123') is False

    def test_change_password_wrong_current(self, authenticated_client):
        """Test password change with wrong current password."""
        response = authenticated_client.post('/auth/change-password', json={
            'current_password': 'wrongpassword',
            'new_password': 'NewPassword123!'
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'Current password is incorrect' in data['error']

    def test_change_password_missing_fields(self, authenticated_client):
        """Test password change with missing fields."""
        response = authenticated_client.post('/auth/change-password', json={
            'current_password': 'testpassword123'
            # Missing new_password
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required fields' in data['error']

    def test_session_persistence(self, client, test_user):
        """Test that user session persists across requests."""
        # Login
        response = client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'testpassword123'
        })
        assert response.status_code == 302

        # Make another request to verify session persistence
        response = client.get('/dashboard')
        assert response.status_code == 200

        # Check session data
        with client.session_transaction() as sess:
            assert sess.get('user_id') == test_user.id
            assert sess.get('username') == test_user.username


class TestFormValidation:
    """Test form validation for authentication forms."""

    def test_registration_form_validation(self, client):
        """Test registration form validation."""
        # Test with empty data
        response = client.post('/auth/register', data={})
        assert response.status_code == 200
        # Should show validation errors

        # Test with invalid email
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'invalid-email',
            'full_name': 'Test User',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        })
        assert response.status_code == 200

        # Test with weak password
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': '123',  # Too weak
            'confirm_password': '123'
        })
        assert response.status_code == 200

    def test_login_form_validation(self, client):
        """Test login form validation."""
        # Test with empty data
        response = client.post('/auth/login', data={})
        assert response.status_code == 200
        # Should show validation errors

        # Test with missing password
        response = client.post('/auth/login', data={
            'username': 'testuser'
            # Missing password
        })
        assert response.status_code == 200


class TestSecurityFeatures:
    """Test security features of the authentication system."""

    def test_password_strength_requirements(self, client):
        """Test password strength validation."""
        weak_passwords = [
            '123',
            'password',
            'PASSWORD',
            '12345678',
            'abcdefgh'
        ]

        for weak_password in weak_passwords:
            response = client.post('/auth/register', data={
                'username': f'user_{weak_password}',
                'email': f'{weak_password}@example.com',
                'full_name': 'Test User',
                'password': weak_password,
                'confirm_password': weak_password
            })
            # Should reject weak passwords
            assert response.status_code == 200

    def test_csrf_protection(self, client):
        """Test CSRF protection on forms."""
        # This test would depend on CSRF being enabled
        # For now, we test that forms without CSRF tokens are handled properly
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
        # Should not crash, even if CSRF protection is enabled
        assert response.status_code in [200, 302, 400]

    def test_rate_limiting_simulation(self, client, test_user):
        """Simulate rate limiting by making multiple failed login attempts."""
        # Make multiple failed login attempts
        for _ in range(5):
            response = client.post('/auth/login', data={
                'username': test_user.username,
                'password': 'wrongpassword'
            })
            assert response.status_code == 200

        # The system should still respond (actual rate limiting would be implemented separately)
        response = client.post('/auth/login', data={
            'username': test_user.username,
            'password': 'testpassword123'
        })
        # Should still allow correct password
        assert response.status_code in [200, 302]
