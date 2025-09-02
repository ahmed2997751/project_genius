"""Quiz API endpoints for ProjectGenius application."""
from flask import jsonify, request, current_app
from sqlalchemy import desc
from projectgenius.api import api_bp
from projectgenius.quizzes.models import Quiz, Question, QuizAttempt, QuestionResponse
from projectgenius.auth.routes import login_required
from projectgenius import db

@api_bp.route('/quizzes', methods=['GET'])
@login_required
def list_quizzes():
    """Get list of available quizzes."""
    lesson_id = request.args.get('lesson_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)

    query = Quiz.query.filter_by(is_published=True)

    if lesson_id:
        query = query.filter_by(lesson_id=lesson_id)

    quizzes = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'quizzes': [{
            'id': quiz.id,
            'title': quiz.title,
            'description': quiz.description,
            'time_limit': quiz.time_limit,
            'passing_score': quiz.passing_score,
            'total_questions': len(quiz.questions),
            'total_points': quiz.total_points
        } for quiz in quizzes.items],
        'pagination': {
            'page': quizzes.page,
            'pages': quizzes.pages,
            'total': quizzes.total,
            'per_page': quizzes.per_page
        }
    })

@api_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@login_required
def get_quiz(quiz_id):
    """Get quiz details without answers."""
    quiz = Quiz.query.get_or_404(quiz_id)

    if not quiz.is_published and not request.user.is_admin:
        return jsonify({'error': 'Quiz not found'}), 404

    # Check if user has ongoing attempt
    ongoing_attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        user_id=request.user.id,
        status='in_progress'
    ).first()

    return jsonify({
        'id': quiz.id,
        'title': quiz.title,
        'description': quiz.description,
        'time_limit': quiz.time_limit,
        'passing_score': quiz.passing_score,
        'max_attempts': quiz.max_attempts,
        'shuffle_questions': quiz.shuffle_questions,
        'show_correct_answers': quiz.show_correct_answers,
        'total_points': quiz.total_points,
        'has_ongoing_attempt': bool(ongoing_attempt),
        'attempts_left': quiz.max_attempts - QuizAttempt.query.filter_by(
            quiz_id=quiz_id,
            user_id=request.user.id,
            status='completed'
        ).count() if quiz.max_attempts else None
    })

@api_bp.route('/quizzes/<int:quiz_id>/start', methods=['POST'])
@login_required
def start_quiz(quiz_id):
    """Start a new quiz attempt."""
    quiz = Quiz.query.get_or_404(quiz_id)

    # Check if user has ongoing attempt
    ongoing_attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz_id,
        user_id=request.user.id,
        status='in_progress'
    ).first()

    if ongoing_attempt:
        return jsonify({
            'error': 'You have an ongoing attempt',
            'attempt_id': ongoing_attempt.id
        }), 400

    # Check attempt limit
    if quiz.max_attempts:
        completed_attempts = QuizAttempt.query.filter_by(
            quiz_id=quiz_id,
            user_id=request.user.id,
            status='completed'
        ).count()
        if completed_attempts >= quiz.max_attempts:
            return jsonify({'error': 'Maximum attempts reached'}), 400

    # Create new attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=request.user.id,
        attempt_number=completed_attempts + 1 if 'completed_attempts' in locals() else 1
    )
    db.session.add(attempt)
    db.session.commit()

    # Get questions (potentially shuffled)
    questions = quiz.questions
    if quiz.shuffle_questions:
        from random import shuffle
        questions = list(questions)
        shuffle(questions)

    return jsonify({
        'attempt_id': attempt.id,
        'questions': [{
            'id': q.id,
            'question_type': q.question_type,
            'content': q.content,
            'options': q.options if q.question_type == 'multiple_choice' else None,
            'points': q.points,
            'order': q.order
        } for q in questions]
    })

@api_bp.route('/quizzes/attempts/<int:attempt_id>/submit', methods=['POST'])
@login_required
def submit_quiz_attempt(attempt_id):
    """Submit answers for a quiz attempt."""
    attempt = QuizAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != request.user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if attempt.status != 'in_progress':
        return jsonify({'error': 'Attempt already completed'}), 400

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'responses' not in data or not isinstance(data['responses'], list):
        return jsonify({'error': 'Invalid response format'}), 400

    # Process responses
    for response_data in data['responses']:
        question = Question.query.get(response_data.get('question_id'))
        if not question or question.quiz_id != attempt.quiz_id:
            continue

        response = QuestionResponse(
            attempt_id=attempt_id,
            question_id=question.id,
            response=response_data.get('answer')
        )

        # Auto-grade if possible
        if question.question_type in ['multiple_choice', 'true_false']:
            response.is_correct = response.response == question.correct_answer
            response.points_earned = question.points if response.is_correct else 0

        db.session.add(response)

    # Update attempt
    attempt.status = 'completed'
    attempt.completed_at = db.func.now()
    attempt.score = attempt.calculate_score()

    db.session.commit()

    return jsonify({
        'message': 'Quiz submitted successfully',
        'score': attempt.score,
        'passing_score': attempt.quiz.passing_score,
        'passed': attempt.is_passing
    })

@api_bp.route('/quizzes/attempts/<int:attempt_id>/results', methods=['GET'])
@login_required
def get_attempt_results(attempt_id):
    """Get detailed results for a quiz attempt."""
    attempt = QuizAttempt.query.get_or_404(attempt_id)

    if attempt.user_id != request.user.id and not request.user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'attempt_id': attempt.id,
        'quiz': {
            'id': attempt.quiz.id,
            'title': attempt.quiz.title
        },
        'score': attempt.score,
        'passing_score': attempt.quiz.passing_score,
        'passed': attempt.is_passing,
        'time_taken': attempt.time_taken,
        'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
        'responses': [{
            'question_id': response.question_id,
            'question': response.question.content,
            'your_answer': response.response,
            'correct_answer': response.question.correct_answer if attempt.quiz.show_correct_answers else None,
            'is_correct': response.is_correct,
            'points_earned': response.points_earned,
            'points_possible': response.question.points,
            'feedback': response.feedback
        } for response in attempt.responses]
    })

@api_bp.route('/quizzes/<int:quiz_id>/analytics', methods=['GET'])
@login_required
def get_quiz_analytics(quiz_id):
    """Get analytics for a quiz."""
    quiz = Quiz.query.get_or_404(quiz_id)

    if not request.user.is_admin and not quiz.is_instructor(request.user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    analytics = quiz.quiz_analytics.first()
    if not analytics:
        return jsonify({'error': 'No analytics available'}), 404

    return jsonify({
        'quiz_id': quiz_id,
        'total_attempts': analytics.total_attempts,
        'average_score': analytics.average_score,
        'completion_rate': analytics.completion_rate,
        'average_time': analytics.average_time_seconds,
        'difficulty_rating': analytics.difficulty_rating,
        'question_stats': [{
            'question_id': q.id,
            'correct_response_rate': sum(1 for r in q.responses if r.is_correct) / len(q.responses) if q.responses else 0,
            'average_points': sum(r.points_earned for r in q.responses) / len(q.responses) if q.responses else 0
        } for q in quiz.questions]
    })
