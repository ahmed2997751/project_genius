"""
Model tests for ProjectGenius application.

This module contains unit tests for database models including
User, Course, Quiz, Assignment, and their relationships.
"""

import pytest
from projectgenius.models import User, Course, Quiz, Assignment, Achievement
from projectgenius import db


class TestUserModel:
    """Test User model functionality."""

    def test_user_creation(self, app):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                full_name='Test User',
                password='password123'
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.full_name == 'Test User'
            assert user.is_active is True
            assert user.is_admin is False
            assert user.api_key is not None
            assert len(user.api_key) == 64

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

    def test_user_representation(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password123'
            )

            assert str(user) == '<User testuser>'

    def test_user_api_key_uniqueness(self, app):
        """Test that API keys are unique."""
        with app.app_context():
            user1 = User(username='user1', email='user1@example.com', password='pass1')
            user2 = User(username='user2', email='user2@example.com', password='pass2')

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            assert user1.api_key != user2.api_key


class TestCourseModel:
    """Test Course model functionality."""

    def test_course_creation(self, app, test_instructor):
        """Test creating a new course."""
        with app.app_context():
            course = Course(
                title='Test Course',
                description='A test course description',
                instructor_id=test_instructor.id,
                level='Beginner',
                category='Programming',
                duration_weeks=8,
                price=49.99
            )
            db.session.add(course)
            db.session.commit()

            assert course.id is not None
            assert course.title == 'Test Course'
            assert course.is_published is False
            assert course.student_count == 0
            assert course.average_rating == pytest.approx(0.0)

    def test_course_instructor_relationship(self, app, test_instructor):
        """Test course-instructor relationship."""
        with app.app_context():
            course = Course(
                title='Test Course',
                description='A test course',
                instructor_id=test_instructor.id,
                level='Beginner',
                category='Programming',
                duration_weeks=4
            )
            db.session.add(course)
            db.session.commit()

            assert course.instructor.id == test_instructor.id
            assert course in test_instructor.taught_courses

    def test_course_representation(self, app, test_instructor):
        """Test course string representation."""
        with app.app_context():
            course = Course(
                title='Test Course',
                description='A test course',
                instructor_id=test_instructor.id,
                level='Beginner',
                category='Programming',
                duration_weeks=4
            )

            assert str(course) == '<Course Test Course>'


class TestQuizModel:
    """Test Quiz model functionality."""

    def test_quiz_creation(self, app):
        """Test creating a new quiz."""
        with app.app_context():
            quiz = Quiz(
                title='Test Quiz',
                description='A test quiz',
                time_limit=30,
                passing_score=70.0,
                max_attempts=3,
                shuffle_questions=True
            )
            db.session.add(quiz)
            db.session.commit()

            assert quiz.id is not None
            assert quiz.title == 'Test Quiz'
            assert quiz.passing_score == pytest.approx(70.0)
            assert quiz.shuffle_questions is True
            assert quiz.is_published is False
            assert quiz.total_points == 0  # No questions yet

    def test_quiz_representation(self, app):
        """Test quiz string representation."""
        with app.app_context():
            quiz = Quiz(
                title='Test Quiz',
                description='A test quiz',
                passing_score=75.0
            )

            assert str(quiz) == '<Quiz Test Quiz>'


class TestAssignmentModel:
    """Test Assignment model functionality."""

    def test_assignment_creation(self, app):
        """Test creating a new assignment."""
        with app.app_context():
            assignment = Assignment(
                title='Test Assignment',
                description='A test assignment',
                instructions='Complete the test assignment',
                points=100.0,
                assignment_type='homework',
                submission_type='file',
                is_group_work=False
            )
            db.session.add(assignment)
            db.session.commit()

            assert assignment.id is not None
            assert assignment.title == 'Test Assignment'
            assert assignment.points == pytest.approx(100.0)
            assert assignment.is_group_work is False
            assert assignment.is_published is False

    def test_assignment_representation(self, app):
        """Test assignment string representation."""
        with app.app_context():
            assignment = Assignment(
                title='Test Assignment',
                description='A test assignment',
                points=50.0
            )

            assert str(assignment) == '<Assignment Test Assignment>'


class TestAchievementModel:
    """Test Achievement model functionality."""

    def test_achievement_creation(self, app):
        """Test creating a new achievement."""
        with app.app_context():
            achievement = Achievement(
                name='First Login',
                description='Logged in for the first time',
                points=10
            )
            db.session.add(achievement)
            db.session.commit()

            assert achievement.id is not None
            assert achievement.name == 'First Login'
            assert achievement.points == 10

    def test_achievement_representation(self, app):
        """Test achievement string representation."""
        with app.app_context():
            achievement = Achievement(
                name='Test Achievement',
                description='A test achievement',
                points=25
            )

            assert str(achievement) == '<Achievement Test Achievement>'


class TestModelRelationships:
    """Test relationships between models."""

    def test_user_course_relationships(self, app, test_user, test_instructor):
        """Test user-course relationships."""
        with app.app_context():
            # Create a course
            course = Course(
                title='Test Course',
                description='A test course',
                instructor_id=test_instructor.id,
                level='Beginner',
                category='Programming',
                duration_weeks=4
            )
            db.session.add(course)
            db.session.commit()

            # Check relationships
            assert course in test_instructor.taught_courses
            assert course.instructor == test_instructor

    def test_user_quiz_attempts(self, app, test_user):
        """Test user quiz attempt relationships."""
        with app.app_context():
            # Create a quiz
            quiz = Quiz(
                title='Test Quiz',
                description='A test quiz',
                passing_score=70.0
            )
            db.session.add(quiz)
            db.session.commit()

            # Check that user has no attempts initially
            assert len(test_user.quiz_attempts) == 0
            assert len(quiz.attempts) == 0