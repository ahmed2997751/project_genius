"""Database models for ProjectGenius application."""
from datetime import datetime
import secrets
import bcrypt
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from projectgenius import db

class User(db.Model):
    """User model for storing user account information."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(64), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    last_login = db.Column(db.DateTime, nullable=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrolled_courses = db.relationship('CourseEnrollment', back_populates='student')
    taught_courses = db.relationship('Course', back_populates='instructor')
    submissions = db.relationship('Submission', back_populates='user', lazy='dynamic')
    achievements = db.relationship('Achievement', secondary='user_achievements')
    
    quiz_attempts = db.relationship('QuizAttempt', back_populates='user', lazy='dynamic')

    def __init__(self, **kwargs):
        """Initialize a new user."""
        if 'password' in kwargs:
            password = kwargs.pop('password')
            self.set_password(password)
        super(User, self).__init__(**kwargs)
        if not self.api_key:
            self.api_key = self.generate_api_key()

    def set_password(self, password):
        """Hash and set the user password."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    @staticmethod
    def generate_api_key():
        """Generate a unique API key."""
        return secrets.token_hex(32)

    def get_id(self):
        """Return the user ID as a string."""
        return str(self.id)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """Return False as anonymous users are not supported."""
        return False

    def __repr__(self):
        """Return string representation of the user."""
        return f'<User {self.username}>'

class Submission(db.Model):
    """Model for storing user code submissions."""
    __tablename__ = 'submissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    score = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    executed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', back_populates='submissions')
    challenge = db.relationship('Challenge')

    def __repr__(self):
        """Return string representation of the submission."""
        return f'<Submission {self.id} by {self.user.username}>'

class Challenge(db.Model):
    """Model for programming challenges."""
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    test_cases = db.Column(db.JSON, nullable=False)
    solution = db.Column(db.Text, nullable=False)
    hints = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        """Return string representation of the challenge."""
        return f'<Challenge {self.title}>'

class Achievement(db.Model):
    """Model for user achievements."""
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge_url = db.Column(db.String(255), nullable=True)
    points = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        """Return string representation of the achievement."""
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    """Association table for user achievements."""
    __tablename__ = 'user_achievements'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), primary_key=True)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
