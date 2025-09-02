"""Core routes for ProjectGenius application."""
from flask import render_template, redirect, url_for, session, request, jsonify, current_app
from projectgenius.core import core_bp
from projectgenius.auth.routes import login_required
from projectgenius.models import User, Achievement
from projectgenius.courses.models import Course, CourseEnrollment
from projectgenius.assignments.models import Assignment, AssignmentSubmission
from projectgenius.quizzes.models import Quiz, QuizAttempt
from projectgenius import db
from sqlalchemy import desc, func
from datetime import datetime, timedelta, timezone

@core_bp.route('/')
def index():
    """Home page."""
    if 'user_id' in session:
        return redirect(url_for('core.dashboard'))

    # Get featured courses
    featured_courses = Course.query.filter_by(is_published=True)\
        .order_by(desc(Course.created_at))\
        .limit(6).all()

    # Get statistics
    stats = {
        'total_courses': Course.query.filter_by(is_published=True).count(),
        'total_students': User.query.filter_by(is_active=True).count(),
        'total_instructors': User.query.filter(
            User.taught_courses.any(Course.is_published == True)
        ).count()
    }

    return render_template('index.html',
                         featured_courses=featured_courses,
                         stats=stats)

@core_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    user = User.query.get(session['user_id'])

    # Get user statistics
    enrolled_courses = CourseEnrollment.query.filter_by(student_id=user.id).all()
    completed_courses = [e for e in enrolled_courses if e.progress == 100]

    # Get assignments completed
    assignments_completed = AssignmentSubmission.query.filter_by(
        student_id=user.id,
        status='graded'
    ).count()

    # Get achievements earned
    achievements_earned = len(user.achievements)

    stats = {
        'enrolled_courses': len(enrolled_courses),
        'completed_courses': len(completed_courses),
        'assignments_completed': assignments_completed,
        'achievements_earned': achievements_earned
    }

    # Get recent activity (simplified)
    recent_activities = []

    # Add recent quiz attempts
    recent_quiz_attempts = QuizAttempt.query.filter_by(user_id=user.id)\
        .filter(QuizAttempt.completed_at.isnot(None))\
        .order_by(desc(QuizAttempt.completed_at))\
        .limit(3).all()

    for attempt in recent_quiz_attempts:
        recent_activities.append({
            'type': 'quiz',
            'type_color': 'info',
            'description': f'Completed quiz: {attempt.quiz.title}',
            'created_at': attempt.completed_at,
            'course': attempt.quiz.lesson.module.course if attempt.quiz.lesson else None
        })

    # Add recent assignment submissions
    recent_submissions = AssignmentSubmission.query.filter_by(student_id=user.id)\
        .order_by(desc(AssignmentSubmission.submitted_at))\
        .limit(3).all()

    for submission in recent_submissions:
        recent_activities.append({
            'type': 'assignment',
            'type_color': 'success',
            'description': f'Submitted assignment: {submission.assignment.title}',
            'created_at': submission.submitted_at,
            'course': submission.assignment.lesson.module.course if submission.assignment.lesson else None
        })

    # Sort activities by date
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)

    # Get upcoming deadlines
    upcoming_deadlines = []
    current_date = datetime.now(timezone.utc)

    for enrollment in enrolled_courses:
        # Get assignments with upcoming deadlines
        course_assignments = Assignment.query.join(Course)\
            .filter(Course.id == enrollment.course_id)\
            .filter(Assignment.due_date.isnot(None))\
            .filter(Assignment.due_date > current_date)\
            .order_by(Assignment.due_date)\
            .limit(3).all()

        for assignment in course_assignments:
            days_left = (assignment.due_date - current_date).days
            upcoming_deadlines.append({
                'title': assignment.title,
                'course': enrollment.course,
                'due_date': assignment.due_date,
                'days_left': days_left
            })

    # Sort by due date
    upcoming_deadlines.sort(key=lambda x: x['due_date'])

    # Get recent achievements
    recent_achievements = user.achievements[-3:] if user.achievements else []

    # Check if user is new (registered within last 7 days)
    is_new_user = (datetime.now(timezone.utc) - user.created_at.replace(tzinfo=timezone.utc)).days <= 7 and len(enrolled_courses) == 0

    return render_template('dashboard.html',
                         current_user=user,
                         stats=stats,
                         recent_activities=recent_activities,
                         enrolled_courses=enrolled_courses,
                         upcoming_deadlines=upcoming_deadlines[:5],
                         recent_achievements=recent_achievements,
                         is_new_user=is_new_user)

@core_bp.route('/courses')
def browse_courses():
    """Browse available courses."""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search', '')

    query = Course.query.filter_by(is_published=True)

    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Course.title.ilike(search_term) |
            Course.description.ilike(search_term)
        )

    courses = query.order_by(desc(Course.created_at))\
        .paginate(page=page, per_page=12, error_out=False)

    # Get available categories and levels
    categories = db.session.query(Course.category)\
        .filter_by(is_published=True)\
        .distinct().all()
    categories = [cat[0] for cat in categories]

    levels = ['Beginner', 'Intermediate', 'Advanced']

    return render_template('courses/browse.html',
                         courses=courses,
                         categories=categories,
                         levels=levels,
                         current_category=category,
                         current_level=level,
                         search_query=search)

@core_bp.route('/courses/<int:course_id>')
def course_overview(course_id):
    """Course overview page."""
    course = Course.query.get_or_404(course_id)

    if not course.is_published and not (
        'user_id' in session and (
            session.get('is_admin') or
            course.instructor_id == session.get('user_id')
        )
    ):
        return render_template('errors/404.html'), 404

    user = None
    is_enrolled = False
    is_instructor = False
    enrollment = None
    progress = 0

    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        is_instructor = user.is_admin or course.instructor_id == user.id

        if not is_instructor:
            enrollment = CourseEnrollment.query.filter_by(
                student_id=user.id,
                course_id=course_id
            ).first()
            is_enrolled = bool(enrollment)
            progress = enrollment.progress if enrollment else 0

    # Get course announcements
    announcements = course.announcements[:5] if course.announcements else []

    # Calculate module and lesson counts
    total_modules = len(course.modules)
    completed_modules = 0

    if enrollment:
        completed_modules = len([mp for mp in enrollment.module_progress if mp.progress == 100])

    return render_template('courses/overview.html',
                         course=course,
                         is_enrolled=is_enrolled,
                         is_instructor=is_instructor,
                         progress=progress,
                         announcements=announcements,
                         total_modules=total_modules,
                         completed_modules=completed_modules,
                         active_tab='overview')

@core_bp.route('/courses/<int:course_id>/modules')
@login_required
def course_modules(course_id):
    """Course modules page."""
    course = Course.query.get_or_404(course_id)
    user = User.query.get(session['user_id'])

    is_instructor = user.is_admin or course.instructor_id == user.id

    if not is_instructor:
        enrollment = CourseEnrollment.query.filter_by(
            student_id=user.id,
            course_id=course_id
        ).first()
        if not enrollment:
            return redirect(url_for('core.course_overview', course_id=course_id))

    return render_template('courses/modules.html',
                         course=course,
                         is_instructor=is_instructor,
                         active_tab='modules')

@core_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@core_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')

@core_bp.route('/privacy')
def privacy():
    """Privacy policy page."""
    return render_template('privacy.html')

@core_bp.route('/terms')
def terms():
    """Terms of service page."""
    return render_template('terms.html')

@core_bp.route('/search')
def search():
    """Global search functionality."""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('core.index'))

    # Search courses
    courses = Course.query.filter_by(is_published=True)\
        .filter(
            Course.title.ilike(f"%{query}%") |
            Course.description.ilike(f"%{query}%")
        ).limit(10).all()

    # Search instructors
    instructors = User.query.filter(
        User.taught_courses.any(Course.is_published == True),
        User.full_name.ilike(f"%{query}%") |
        User.username.ilike(f"%{query}%")
    ).limit(5).all()

    results = {
        'courses': courses,
        'instructors': instructors,
        'query': query
    }

    return render_template('search_results.html', **results)

@core_bp.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'version': '1.0.0'
    })

@core_bp.route('/profile/<username>')
def public_profile(username):
    """Public user profile page."""
    user = User.query.filter_by(username=username).first_or_404()

    # Get public information only
    taught_courses = Course.query.filter_by(
        instructor_id=user.id,
        is_published=True
    ).all()

    public_achievements = user.achievements[:6] if user.achievements else []

    profile_data = {
        'username': user.username,
        'full_name': user.full_name,
        'bio': user.bio,
        'avatar_url': user.avatar_url,
        'member_since': user.created_at,
        'taught_courses': taught_courses,
        'achievements': public_achievements
    }

    return render_template('profiles/public.html', profile_user=user, **profile_data)

@core_bp.route('/subscription')
@login_required
def subscription():
    """Subscription management page."""
    user = User.query.get(session['user_id'])
    return render_template('subscription.html', current_user=user)

@core_bp.route('/analytics')
@login_required
def analytics():
    """Analytics page for premium users."""
    user = User.query.get(session['user_id'])
    
    # Mock analytics data for now
    analytics_data = {
        'study_sessions': 0,
        'cards_studied': 0,
        'accuracy_rate': 0,
        'streak_days': 0
    }
    
    stats = {
        'total_sessions': 0,
        'total_cards': 0,
        'average_accuracy': 0,
        'study_streak': 0
    }
    
    return render_template('analytics.html',
                         current_user=user,
                         analytics_data=analytics_data,
                         stats=stats)
