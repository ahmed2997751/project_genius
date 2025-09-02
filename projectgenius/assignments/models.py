"""Assignment models for ProjectGenius application."""
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON
from projectgenius import db

class Assignment(db.Model):
    """Assignment model for course tasks and projects."""
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
    points = db.Column(db.Float, nullable=False, default=100.0)
    assignment_type = db.Column(db.String(50), nullable=False)  # project, homework, lab, etc.
    is_group_work = db.Column(db.Boolean, default=False)
    max_group_size = db.Column(db.Integer, nullable=True)
    submission_type = db.Column(db.String(50), nullable=False)  # file, text, link, repository
    allowed_file_types = db.Column(JSON, nullable=True)
    max_file_size = db.Column(db.Integer, nullable=True)  # in bytes
    rubric = db.Column(JSON, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    allow_late_submission = db.Column(db.Boolean, default=True)
    late_penalty_percentage = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submissions = db.relationship('AssignmentSubmission', back_populates='assignment', cascade='all, delete-orphan')
    resources = db.relationship('AssignmentResource', back_populates='assignment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Assignment {self.title}>'

class AssignmentSubmission(db.Model):
    """Model for student assignment submissions."""
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('assignment_groups.id'), nullable=True)
    content = db.Column(db.Text, nullable=True)  # For text submissions
    file_paths = db.Column(JSON, nullable=True)  # For file submissions
    submission_url = db.Column(db.String(500), nullable=True)  # For link/repository submissions
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_late = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='submitted')  # submitted, graded, returned
    grade = db.Column(db.Float, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    rubric_scores = db.Column(JSON, nullable=True)
    graded_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    graded_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    assignment = db.relationship('Assignment', back_populates='submissions')
    student = db.relationship('User', foreign_keys=[student_id])
    graded_by = db.relationship('User', foreign_keys=[graded_by_id])
    group = db.relationship('AssignmentGroup', back_populates='submissions')
    comments = db.relationship('SubmissionComment', back_populates='submission', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<AssignmentSubmission {self.student.username} - {self.assignment.title}>'

class AssignmentGroup(db.Model):
    """Model for group assignments."""
    __tablename__ = 'assignment_groups'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members = db.relationship('GroupMember', back_populates='group', cascade='all, delete-orphan')
    submissions = db.relationship('AssignmentSubmission', back_populates='group')

    @property
    def member_count(self):
        """Get the number of group members."""
        return len(self.members)

    def __repr__(self):
        return f'<AssignmentGroup {self.name}>'

class GroupMember(db.Model):
    """Model for assignment group members."""
    __tablename__ = 'group_members'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('assignment_groups.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), default='member')  # leader, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    group = db.relationship('AssignmentGroup', back_populates='members')
    student = db.relationship('User')

    def __repr__(self):
        return f'<GroupMember {self.student.username} in {self.group.name}>'

class AssignmentResource(db.Model):
    """Model for assignment resources and attachments."""
    __tablename__ = 'assignment_resources'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    resource_type = db.Column(db.String(50), nullable=False)  # file, link, template
    url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    assignment = db.relationship('Assignment', back_populates='resources')

    def __repr__(self):
        return f'<AssignmentResource {self.title}>'

class SubmissionComment(db.Model):
    """Model for comments on assignment submissions."""
    __tablename__ = 'submission_comments'

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('assignment_submissions.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submission = db.relationship('AssignmentSubmission', back_populates='comments')
    user = db.relationship('User')

    def __repr__(self):
        return f'<SubmissionComment by {self.user.username}>'

class AssignmentAnalytics(db.Model):
    """Analytics for assignment performance."""
    __tablename__ = 'assignment_analytics'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    total_submissions = db.Column(db.Integer, default=0)
    on_time_submissions = db.Column(db.Integer, default=0)
    late_submissions = db.Column(db.Integer, default=0)
    average_grade = db.Column(db.Float, nullable=True)
    median_grade = db.Column(db.Float, nullable=True)
    highest_grade = db.Column(db.Float, nullable=True)
    lowest_grade = db.Column(db.Float, nullable=True)
    completion_rate = db.Column(db.Float, nullable=True)  # percentage
    average_time_to_submit = db.Column(db.Integer, nullable=True)  # in hours
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    assignment = db.relationship('Assignment')

    def __repr__(self):
        return f'<AssignmentAnalytics for Assignment {self.assignment_id}>'
