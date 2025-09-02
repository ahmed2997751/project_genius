"""Course-related models for ProjectGenius application."""
from datetime import datetime
from projectgenius import db

class Course(db.Model):
    """Course model for educational content."""
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cover_image = db.Column(db.String(255), nullable=True)
    level = db.Column(db.String(20), nullable=False)  # Beginner, Intermediate, Advanced
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    duration_weeks = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor = db.relationship('User', back_populates='taught_courses')
    enrollments = db.relationship('CourseEnrollment', back_populates='course', cascade='all, delete-orphan')
    modules = db.relationship('Module', back_populates='course', cascade='all, delete-orphan')
    announcements = db.relationship('CourseAnnouncement', back_populates='course', cascade='all, delete-orphan')
    reviews = db.relationship('CourseReview', back_populates='course', cascade='all, delete-orphan')

    @property
    def average_rating(self):
        """Calculate the average rating for the course."""
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    @property
    def student_count(self):
        """Get the number of enrolled students."""
        return len(self.enrollments)

    def __repr__(self):
        return f'<Course {self.title}>'

class CourseEnrollment(db.Model):
    """Model for student course enrollments."""
    __tablename__ = 'course_enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    progress = db.Column(db.Float, default=0.0)  # 0-100%
    last_accessed = db.Column(db.DateTime, nullable=True)
    payment_status = db.Column(db.String(20), default='pending')
    certificate_issued = db.Column(db.Boolean, default=False)

    # Relationships
    student = db.relationship('User', back_populates='enrolled_courses')
    course = db.relationship('Course', back_populates='enrollments')
    module_progress = db.relationship('ModuleProgress', back_populates='enrollment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CourseEnrollment {self.student.username} in {self.course.title}>'

class Module(db.Model):
    """Course module model."""
    __tablename__ = 'modules'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='modules')
    lessons = db.relationship('Lesson', back_populates='module', cascade='all, delete-orphan')
    progress_records = db.relationship('ModuleProgress', back_populates='module')

    def __repr__(self):
        return f'<Module {self.title}>'

class Lesson(db.Model):
    """Course lesson model."""
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(20), nullable=False)  # video, text, quiz, assignment
    duration_minutes = db.Column(db.Integer, nullable=True)
    order = db.Column(db.Integer, nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    module = db.relationship('Module', back_populates='lessons')
    resources = db.relationship('LessonResource', back_populates='lesson', cascade='all, delete-orphan')
    completion_records = db.relationship('LessonCompletion', back_populates='lesson')

    def __repr__(self):
        return f'<Lesson {self.title}>'

class LessonResource(db.Model):
    """Model for lesson resources (files, links, etc.)."""
    __tablename__ = 'lesson_resources'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(20), nullable=False)  # file, link, pdf, etc.
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    lesson = db.relationship('Lesson', back_populates='resources')

    def __repr__(self):
        return f'<LessonResource {self.title}>'

class ModuleProgress(db.Model):
    """Track student progress in modules."""
    __tablename__ = 'module_progress'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('course_enrollments.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)  # 0-100%
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    last_accessed = db.Column(db.DateTime, nullable=True)

    # Relationships
    enrollment = db.relationship('CourseEnrollment', back_populates='module_progress')
    module = db.relationship('Module', back_populates='progress_records')

    def __repr__(self):
        return f'<ModuleProgress {self.enrollment.student.username} - {self.module.title}>'

class LessonCompletion(db.Model):
    """Track completed lessons."""
    __tablename__ = 'lesson_completions'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    student = db.relationship('User')
    lesson = db.relationship('Lesson', back_populates='completion_records')

    def __repr__(self):
        return f'<LessonCompletion {self.student.username} - {self.lesson.title}>'

class CourseAnnouncement(db.Model):
    """Course announcements model."""
    __tablename__ = 'course_announcements'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    course = db.relationship('Course', back_populates='announcements')

    def __repr__(self):
        return f'<CourseAnnouncement {self.title}>'

class CourseReview(db.Model):
    """Course reviews and ratings model."""
    __tablename__ = 'course_reviews'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='reviews')
    student = db.relationship('User')

    def __repr__(self):
        return f'<CourseReview {self.course.title} - {self.rating} stars>'
