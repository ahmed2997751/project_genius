"""
Pytest configuration and fixtures for ProjectGenius tests.

This module provides shared fixtures and configuration for all tests
in the ProjectGenius test suite.
"""

import pytest
import tempfile
import os
from pathlib import Path
from projectgenius import create_app, db
from projectgenius.models import User, Course, Quiz, Assignment


@pytest.fixture
def app():
    """Create and configure a test Flask application."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()

    # Test configuration
    test_config = {
        'TESTING': True,
        'DATABASE_URL': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'BCRYPT_LOG_ROUNDS': 4,  # Faster for testing
        'UPLOAD_FOLDER': tempfile.mkdtemp(),
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,
    }

    # Create app with test config
    app = create_app()
    app.config.update(test_config)

    with app.app_context():
        # Create all database tables
        db.create_all()
        yield app

        # Clean up
        db.drop_all()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for CLI commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Return common authentication headers."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def test_user(app):
    """Create a test user in the database."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            full_name='Test User',
            password='testpassword123',
            is_active=True,
            email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_admin(app):
    """Create a test admin user in the database."""
    with app.app_context():
        admin = User(
            username='testadmin',
            email='admin@example.com',
            full_name='Test Admin',
            password='adminpassword123',
            is_admin=True,
            is_active=True,
            email_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        return admin


@pytest.fixture
def test_instructor(app):
    """Create a test instructor user in the database."""
    with app.app_context():
        instructor = User(
            username='testinstructor',
            email='instructor@example.com',
            full_name='Test Instructor',
            password='instructorpass123',
            is_active=True,
            email_verified=True
        )
        db.session.add(instructor)
        db.session.commit()
        return instructor


@pytest.fixture
def test_course(app, test_instructor):
    """Create a test course in the database."""
    with app.app_context():
        course = Course(
            title='Test Course',
            description='A test course for unit testing',
            instructor_id=test_instructor.id,
            level='Beginner',
            category='Testing',
            duration_weeks=4,
            price=0.0,
            is_published=True
        )
        db.session.add(course)
        db.session.commit()
        return course


@pytest.fixture
def test_quiz(app, test_course):
    """Create a test quiz in the database."""
    with app.app_context():
        quiz = Quiz(
            title='Test Quiz',
            description='A test quiz for unit testing',
            time_limit=30,
            passing_score=70.0,
            max_attempts=3,
            is_published=True
        )
        db.session.add(quiz)
        db.session.commit()
        return quiz


@pytest.fixture
def test_assignment(app, test_course):
    """Create a test assignment in the database."""
    with app.app_context():
        assignment = Assignment(
            title='Test Assignment',
            description='A test assignment for unit testing',
            instructions='Complete the test assignment',
            points=100.0,
            assignment_type='homework',
            submission_type='text',
            is_published=True
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    # Login the test user
    response = client.post('/auth/login', data={
        'username': test_user.username,
        'password': 'testpassword123'
    })
    assert response.status_code == 302  # Redirect after successful login
    return client


@pytest.fixture
def admin_client(client, test_admin):
    """Create an authenticated admin client."""
    # Login the test admin
    response = client.post('/auth/login', data={
        'username': test_admin.username,
        'password': 'adminpassword123'
    })
    assert response.status_code == 302  # Redirect after successful login
    return client


@pytest.fixture
def instructor_client(client, test_instructor):
    """Create an authenticated instructor client."""
    # Login the test instructor
    response = client.post('/auth/login', data={
        'username': test_instructor.username,
        'password': 'instructorpass123'
    })
    assert response.status_code == 302  # Redirect after successful login
    return client


@pytest.fixture
def sample_course_data():
    """Return sample course data for testing."""
    return {
        'title': 'Sample Course',
        'description': 'This is a sample course for testing purposes',
        'level': 'Intermediate',
        'category': 'Programming',
        'duration_weeks': 8,
        'price': 49.99
    }


@pytest.fixture
def sample_quiz_data():
    """Return sample quiz data for testing."""
    return {
        'title': 'Sample Quiz',
        'description': 'This is a sample quiz for testing',
        'time_limit': 45,
        'passing_score': 75.0,
        'max_attempts': 2,
        'shuffle_questions': True,
        'show_correct_answers': True
    }


@pytest.fixture
def sample_question_data():
    """Return sample question data for testing."""
    return {
        'question_type': 'multiple_choice',
        'content': 'What is the capital of France?',
        'options': ['London', 'Berlin', 'Paris', 'Madrid'],
        'correct_answer': ['Paris'],
        'points': 5.0,
        'order': 1
    }


@pytest.fixture
def sample_assignment_data():
    """Return sample assignment data for testing."""
    return {
        'title': 'Sample Assignment',
        'description': 'This is a sample assignment for testing',
        'instructions': 'Complete the assignment according to the requirements',
        'points': 100.0,
        'assignment_type': 'project',
        'submission_type': 'file',
        'allowed_file_types': ['pdf', 'docx', 'txt'],
        'max_file_size': 5242880  # 5MB
    }


@pytest.fixture
def temp_upload_file():
    """Create a temporary file for upload testing."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
    temp_file.write(b'This is a test file for upload testing.')
    temp_file.close()

    yield temp_file.name

    # Cleanup
    try:
        os.unlink(temp_file.name)
    except OSError:
        pass


@pytest.fixture(scope='session')
def test_data_dir():
    """Return the path to test data directory."""
    return Path(__file__).parent / 'data'


@pytest.fixture(autouse=True)
def cleanup_database(app):
    """Automatically clean up database after each test."""
    yield

    with app.app_context():
        # Clear all data from tables
        db.session.remove()
        db.drop_all()
        db.create_all()


class TestUtils:
    """Utility class for common test operations."""

    @staticmethod
    def login_user(client, username, password):
        """Helper function to login a user."""
        return client.post('/auth/login', data={
            'username': username,
            'password': password
        })

    @staticmethod
    def logout_user(client):
        """Helper function to logout a user."""
        return client.get('/auth/logout')

    @staticmethod
    def create_test_user(username='testuser', email='test@example.com', password='password123'):
        """Helper function to create a test user."""
        user = User(
            username=username,
            email=email,
            full_name=f'Test {username.title()}',
            password=password,
            is_active=True,
            email_verified=True
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils


# Custom markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "database: mark test as database related"
    )


# Test collection modification
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file names
        if "test_auth" in item.nodeid:
            item.add_marker(pytest.mark.auth)
        elif "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_models" in item.nodeid:
            item.add_marker(pytest.mark.database)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit)
