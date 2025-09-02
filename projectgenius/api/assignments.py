"""Assignment API endpoints for ProjectGenius application."""
from flask import jsonify, request, current_app
from sqlalchemy import desc
from projectgenius.api import api_bp
from projectgenius.assignments.models import (
    Assignment, AssignmentSubmission, AssignmentGroup,
    GroupMember, SubmissionComment, AssignmentResource
)
from projectgenius.auth.routes import login_required
from projectgenius.utils import allowed_file, generate_unique_filename
from projectgenius import db
import os

@api_bp.route('/assignments', methods=['GET'])
@login_required
def list_assignments():
    """Get list of assignments."""
    lesson_id = request.args.get('lesson_id', type=int)
    type_filter = request.args.get('type')
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)

    query = Assignment.query

    if lesson_id:
        query = query.filter_by(lesson_id=lesson_id)
    if type_filter:
        query = query.filter_by(assignment_type=type_filter)

    # Show all assignments for instructors, only published ones for students
    if not request.user.is_admin:
        query = query.filter_by(is_published=True)

    assignments = query.order_by(desc(Assignment.created_at))\
        .paginate(page=page, per_page=per_page)

    return jsonify({
        'assignments': [{
            'id': assignment.id,
            'title': assignment.title,
            'description': assignment.description,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'points': assignment.points,
            'type': assignment.assignment_type,
            'is_group_work': assignment.is_group_work,
            'submission_type': assignment.submission_type,
            'created_at': assignment.created_at.isoformat()
        } for assignment in assignments.items],
        'pagination': {
            'page': assignments.page,
            'pages': assignments.pages,
            'total': assignments.total,
            'per_page': assignments.per_page
        }
    })

@api_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@login_required
def get_assignment(assignment_id):
    """Get detailed assignment information."""
    assignment = Assignment.query.get_or_404(assignment_id)

    if not assignment.is_published and not request.user.is_admin:
        return jsonify({'error': 'Assignment not found'}), 404

    # Get user's submission if exists
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=request.user.id
    ).first()

    # Get user's group if it's group work
    group = None
    if assignment.is_group_work:
        group_member = GroupMember.query.join(AssignmentGroup)\
            .filter(
                AssignmentGroup.assignment_id == assignment_id,
                GroupMember.student_id == request.user.id
            ).first()
        if group_member:
            group = group_member.group

    return jsonify({
        'id': assignment.id,
        'title': assignment.title,
        'description': assignment.description,
        'instructions': assignment.instructions,
        'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
        'points': assignment.points,
        'type': assignment.assignment_type,
        'is_group_work': assignment.is_group_work,
        'max_group_size': assignment.max_group_size,
        'submission_type': assignment.submission_type,
        'allowed_file_types': assignment.allowed_file_types,
        'max_file_size': assignment.max_file_size,
        'rubric': assignment.rubric,
        'allow_late_submission': assignment.allow_late_submission,
        'late_penalty_percentage': assignment.late_penalty_percentage,
        'resources': [{
            'id': resource.id,
            'title': resource.title,
            'description': resource.description,
            'type': resource.resource_type,
            'url': resource.url
        } for resource in assignment.resources],
        'submission': {
            'id': submission.id,
            'status': submission.status,
            'submitted_at': submission.submitted_at.isoformat(),
            'grade': submission.grade,
            'feedback': submission.feedback,
            'is_late': submission.is_late
        } if submission else None,
        'group': {
            'id': group.id,
            'name': group.name,
            'members': [{
                'id': member.student_id,
                'username': member.student.username,
                'role': member.role
            } for member in group.members]
        } if group else None
    })

@api_bp.route('/assignments/<int:assignment_id>/submit', methods=['POST'])
@login_required
def submit_assignment(assignment_id):
    """Submit an assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)

    # Check if submission is allowed
    if not assignment.is_published:
        return jsonify({'error': 'Assignment not available'}), 400

    # Check if past due date and late submissions not allowed
    if assignment.due_date and not assignment.allow_late_submission:
        from datetime import datetime
        if datetime.utcnow() > assignment.due_date:
            return jsonify({'error': 'Assignment past due date'}), 400

    # Handle group submission
    group_id = None
    if assignment.is_group_work:
        group_member = GroupMember.query.join(AssignmentGroup)\
            .filter(
                AssignmentGroup.assignment_id == assignment_id,
                GroupMember.student_id == request.user.id
            ).first()
        if not group_member:
            return jsonify({'error': 'Must be in a group to submit'}), 400
        group_id = group_member.group_id

    # Handle different submission types
    submission_data = {}

    if assignment.submission_type == 'file':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if not allowed_file(file.filename, assignment.allowed_file_types):
            return jsonify({'error': 'File type not allowed'}), 400

        if file.content_length > assignment.max_file_size:
            return jsonify({'error': 'File too large'}), 400

        filename = generate_unique_filename(file.filename)
        file_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            str(assignment_id),
            filename
        )

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        submission_data['file_paths'] = [file_path]

    elif assignment.submission_type == 'text':
        if not request.form.get('content'):
            return jsonify({'error': 'No content provided'}), 400
        submission_data['content'] = request.form['content']

    elif assignment.submission_type == 'link':
        if not request.form.get('url'):
            return jsonify({'error': 'No URL provided'}), 400
        submission_data['submission_url'] = request.form['url']

    # Create or update submission
    submission = AssignmentSubmission.query.filter_by(
        assignment_id=assignment_id,
        student_id=request.user.id
    ).first()

    if submission:
        for key, value in submission_data.items():
            setattr(submission, key, value)
        submission.submitted_at = db.func.now()
    else:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            student_id=request.user.id,
            group_id=group_id,
            **submission_data
        )
        db.session.add(submission)

    db.session.commit()

    return jsonify({
        'message': 'Assignment submitted successfully',
        'submission_id': submission.id
    })

@api_bp.route('/assignments/<int:assignment_id>/groups', methods=['POST'])
@login_required
def create_group(assignment_id):
    """Create a new group for group assignment."""
    assignment = Assignment.query.get_or_404(assignment_id)

    if not assignment.is_group_work:
        return jsonify({'error': 'Not a group assignment'}), 400

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'name' not in data:
        return jsonify({'error': 'Group name required'}), 400

    # Check if user is already in a group
    existing_member = GroupMember.query.join(AssignmentGroup)\
        .filter(
            AssignmentGroup.assignment_id == assignment_id,
            GroupMember.student_id == request.user.id
        ).first()

    if existing_member:
        return jsonify({'error': 'Already in a group'}), 400

    # Create group and add creator as leader
    group = AssignmentGroup(
        assignment_id=assignment_id,
        name=data['name']
    )
    db.session.add(group)
    db.session.flush()

    member = GroupMember(
        group_id=group.id,
        student_id=request.user.id,
        role='leader'
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({
        'message': 'Group created successfully',
        'group_id': group.id
    }), 201

@api_bp.route('/assignments/groups/<int:group_id>/members', methods=['POST'])
@login_required
def add_group_member(group_id):
    """Add a member to a group."""
    group = AssignmentGroup.query.get_or_404(group_id)

    # Verify user is group leader
    leader = GroupMember.query.filter_by(
        group_id=group_id,
        student_id=request.user.id,
        role='leader'
    ).first()
    if not leader:
        return jsonify({'error': 'Must be group leader to add members'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'student_id' not in data:
        return jsonify({'error': 'Student ID required'}), 400

    # Check group size limit
    if group.member_count >= group.assignment.max_group_size:
        return jsonify({'error': 'Group is full'}), 400

    # Check if student is already in a group
    existing_member = GroupMember.query.join(AssignmentGroup)\
        .filter(
            AssignmentGroup.assignment_id == group.assignment_id,
            GroupMember.student_id == data['student_id']
        ).first()

    if existing_member:
        return jsonify({'error': 'Student already in a group'}), 400

    member = GroupMember(
        group_id=group_id,
        student_id=data['student_id'],
        role='member'
    )
    db.session.add(member)
    db.session.commit()

    return jsonify({
        'message': 'Member added successfully',
        'member_id': member.id
    })

@api_bp.route('/assignments/submissions/<int:submission_id>/comment', methods=['POST'])
@login_required
def add_submission_comment(submission_id):
    """Add a comment to a submission."""
    submission = AssignmentSubmission.query.get_or_404(submission_id)

    # Verify user has access to submission
    if not (request.user.is_admin or
            request.user.id == submission.student_id or
            submission.assignment.is_instructor(request.user.id)):
        return jsonify({'error': 'Unauthorized'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'content' not in data:
        return jsonify({'error': 'Comment content required'}), 400

    comment = SubmissionComment(
        submission_id=submission_id,
        user_id=request.user.id,
        content=data['content']
    )
    db.session.add(comment)
    db.session.commit()

    return jsonify({
        'message': 'Comment added successfully',
        'comment_id': comment.id
    })

@api_bp.route('/assignments/submissions/<int:submission_id>/grade', methods=['POST'])
@login_required
def grade_submission(submission_id):
    """Grade an assignment submission."""
    submission = AssignmentSubmission.query.get_or_404(submission_id)

    # Verify user can grade
    if not (request.user.is_admin or
            submission.assignment.is_instructor(request.user.id)):
        return jsonify({'error': 'Unauthorized'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'grade' not in data or not isinstance(data['grade'], (int, float)):
        return jsonify({'error': 'Valid grade required'}), 400

    if data['grade'] < 0 or data['grade'] > submission.assignment.points:
        return jsonify({'error': 'Grade out of range'}), 400

    submission.grade = data['grade']
    submission.feedback = data.get('feedback')
    submission.rubric_scores = data.get('rubric_scores')
    submission.graded_by_id = request.user.id
    submission.graded_at = db.func.now()
    submission.status = 'graded'

    db.session.commit()

    return jsonify({
        'message': 'Submission graded successfully',
        'grade': submission.grade
    })
