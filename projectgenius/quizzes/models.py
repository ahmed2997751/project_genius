"""Quiz and assessment models for ProjectGenius application."""
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from projectgenius import db

class Quiz(db.Model):
    """Quiz model for assessments."""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    time_limit = db.Column(db.Integer, nullable=True)  # in minutes
    passing_score = db.Column(db.Float, nullable=False, default=70.0)
    max_attempts = db.Column(db.Integer, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    shuffle_questions = db.Column(db.Boolean, default=True)
    show_correct_answers = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', back_populates='quiz', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', back_populates='quiz', cascade='all, delete-orphan')

    @property
    def total_points(self):
        """Calculate total points possible for the quiz."""
        return sum(question.points for question in self.questions)

    def __repr__(self):
        return f'<Quiz {self.title}>'

class Question(db.Model):
    """Question model for quizzes."""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # multiple_choice, true_false, essay, coding
    content = db.Column(db.Text, nullable=False)
    options = db.Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = db.Column(JSON, nullable=True)  # Can store multiple correct answers
    explanation = db.Column(db.Text, nullable=True)
    points = db.Column(db.Float, nullable=False, default=1.0)
    order = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.String(20), nullable=True)  # easy, medium, hard
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quiz = db.relationship('Quiz', back_populates='questions')
    responses = db.relationship('QuestionResponse', back_populates='question', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question {self.id} for Quiz {self.quiz_id}>'

class QuizAttempt(db.Model):
    """Model for tracking student quiz attempts."""
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Float, nullable=True)
    attempt_number = db.Column(db.Integer, nullable=False)
    time_taken = db.Column(db.Integer, nullable=True)  # in seconds
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned

    # Relationships
    quiz = db.relationship('Quiz', back_populates='attempts')
    user = db.relationship('User', back_populates='quiz_attempts')
    responses = db.relationship('QuestionResponse', back_populates='attempt', cascade='all, delete-orphan')

    @property
    def is_passing(self):
        """Check if the attempt meets the passing score."""
        if self.score is None or self.quiz.passing_score is None:
            return False
        return self.score >= self.quiz.passing_score

    def calculate_score(self):
        """Calculate the score for this attempt."""
        if not self.responses:
            return 0.0

        total_points = self.quiz.total_points
        earned_points = sum(response.points_earned for response in self.responses)

        return (earned_points / total_points) * 100 if total_points > 0 else 0.0

    def __repr__(self):
        return f'<QuizAttempt {self.user.username} - {self.quiz.title}>'

class QuestionResponse(db.Model):
    """Model for storing student responses to questions."""
    __tablename__ = 'question_responses'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    response = db.Column(JSON, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=True)
    points_earned = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attempt = db.relationship('QuizAttempt', back_populates='responses')
    question = db.relationship('Question', back_populates='responses')

    def __repr__(self):
        return f'<QuestionResponse {self.id} for Question {self.question_id}>'

class CodingQuestion(Question):
    """Specialized question type for coding challenges."""
    __tablename__ = 'coding_questions'

    id = db.Column(db.Integer, db.ForeignKey('questions.id'), primary_key=True)
    starter_code = db.Column(db.Text, nullable=True)
    test_cases = db.Column(JSON, nullable=False)  # List of input/output pairs
    language = db.Column(db.String(50), nullable=False)
    time_limit_seconds = db.Column(db.Integer, default=5)
    memory_limit_mb = db.Column(db.Integer, default=128)

    __mapper_args__ = {
        'polymorphic_identity': 'coding'
    }

class QuizAnalytics(db.Model):
    """Analytics for quiz performance."""
    __tablename__ = 'quiz_analytics'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    total_attempts = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, nullable=True)
    completion_rate = db.Column(db.Float, nullable=True)  # percentage
    average_time_seconds = db.Column(db.Float, nullable=True)
    difficulty_rating = db.Column(db.Float, nullable=True)  # calculated from student performance
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    quiz = db.relationship('Quiz')

    def __repr__(self):
        return f'<QuizAnalytics for Quiz {self.quiz_id}>'
