"""Course API endpoints for ProjectGenius application."""
from flask import jsonify, request, current_app
from sqlalchemy import desc
from projectgenius.api import api_bp
from projectgenius.courses.models import Course, CourseEnrollment, CourseAnnouncement, CourseReview
from projectgenius.auth.routes import login_required
from projectgenius.utils import require_api_key
from projectgenius import db

@api_bp.route('/courses', methods=['GET'])
def list_courses():
    """Get list of courses with optional filters."""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 50)
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')

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

    # Apply sorting
    if order == 'desc':
        query = query.order_by(desc(getattr(Course, sort_by)))
    else:
        query = query.order_by(getattr(Course, sort_by))

    # Paginate results
    courses = query.paginate(page=page, per_page=per_page)

    return jsonify({
        'courses': [{
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'instructor': {
                'id': course.instructor.id,
                'name': course.instructor.full_name or course.instructor.username
            },
            'level': course.level,
            'category': course.category,
            'price': course.price,
            'duration_weeks': course.duration_weeks,
            'average_rating': course.average_rating,
            'student_count': course.student_count,
            'created_at': course.created_at.isoformat()
        } for course in courses.items],
        'pagination': {
            'page': courses.page,
            'pages': courses.pages,
            'total': courses.total,
            'per_page': courses.per_page,
            'has_next': courses.has_next,
            'has_prev': courses.has_prev
        }
    })

@api_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get detailed course information."""
    course = Course.query.get_or_404(course_id)

    if not course.is_published and not (
        request.user and (
            request.user.is_admin or
            request.user.id == course.instructor_id
        )
    ):
        return jsonify({'error': 'Course not found'}), 404

    return jsonify({
        'id': course.id,
        'title': course.title,
        'description': course.description,
        'instructor': {
            'id': course.instructor.id,
            'name': course.instructor.full_name or course.instructor.username,
            'bio': course.instructor.bio
        },
        'level': course.level,
        'category': course.category,
        'price': course.price,
        'duration_weeks': course.duration_weeks,
        'is_published': course.is_published,
        'average_rating': course.average_rating,
        'student_count': course.student_count,
        'modules': [{
            'id': module.id,
            'title': module.title,
            'description': module.description,
            'order': module.order,
            'lessons': [{
                'id': lesson.id,
                'title': lesson.title,
                'content_type': lesson.content_type,
                'duration_minutes': lesson.duration_minutes,
                'order': lesson.order
            } for lesson in module.lessons if lesson.is_published or (
                request.user and (
                    request.user.is_admin or
                    request.user.id == course.instructor_id
                )
            )]
        } for module in course.modules if module.is_published or (
            request.user and (
                request.user.is_admin or
                request.user.id == course.instructor_id
            )
        )],
        'reviews': [{
            'id': review.id,
            'rating': review.rating,
            'review': review.review,
            'student': {
                'id': review.student.id,
                'name': review.student.full_name or review.student.username
            },
            'created_at': review.created_at.isoformat()
        } for review in course.reviews[:5]],  # Show only latest 5 reviews
        'created_at': course.created_at.isoformat(),
        'updated_at': course.updated_at.isoformat()
    })

@api_bp.route('/courses', methods=['POST'])
@login_required
def create_course():
    """Create a new course."""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    required_fields = ['title', 'description', 'level', 'category', 'duration_weeks']

    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    course = Course(
        title=data['title'],
        description=data['description'],
        instructor_id=request.user.id,
        level=data['level'],
        category=data['category'],
        price=data.get('price', 0.0),
        duration_weeks=data['duration_weeks'],
        is_published=False
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        'message': 'Course created successfully',
        'course_id': course.id
    }), 201

@api_bp.route('/courses/<int:course_id>', methods=['PUT'])
@login_required
def update_course(course_id):
    """Update course information."""
    course = Course.query.get_or_404(course_id)

    if not (request.user.is_admin or request.user.id == course.instructor_id):
        return jsonify({'error': 'Unauthorized'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()

    # Update fields if provided
    for field in ['title', 'description', 'level', 'category', 'price',
                 'duration_weeks', 'is_published']:
        if field in data:
            setattr(course, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Course updated successfully',
        'course_id': course.id
    })

@api_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll in a course."""
    course = Course.query.get_or_404(course_id)

    # Check if already enrolled
    existing_enrollment = CourseEnrollment.query.filter_by(
        student_id=request.user.id,
        course_id=course_id
    ).first()

    if existing_enrollment:
        return jsonify({'error': 'Already enrolled in this course'}), 400

    # Handle paid courses (implement payment processing here)
    if course.price > 0:
        # Add payment processing logic
        pass

    enrollment = CourseEnrollment(
        student_id=request.user.id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        'message': 'Successfully enrolled in course',
        'enrollment_id': enrollment.id
    }), 201

@api_bp.route('/courses/<int:course_id>/announcements', methods=['GET'])
@login_required
def list_announcements(course_id):
    """Get course announcements."""
    course = Course.query.get_or_404(course_id)

    # Check if user is enrolled or is instructor
    if not (request.user.is_admin or
            request.user.id == course.instructor_id or
            CourseEnrollment.query.filter_by(
                student_id=request.user.id,
                course_id=course_id
            ).first()):
        return jsonify({'error': 'Unauthorized'}), 403

    announcements = CourseAnnouncement.query.filter_by(course_id=course_id)\
        .order_by(desc(CourseAnnouncement.created_at)).all()

    return jsonify({
        'announcements': [{
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'created_at': announcement.created_at.isoformat(),
            'updated_at': announcement.updated_at.isoformat()
        } for announcement in announcements]
    })

@api_bp.route('/courses/<int:course_id>/reviews', methods=['POST'])
@login_required
def create_review(course_id):
    """Create a course review."""
    course = Course.query.get_or_404(course_id)

    # Check if user is enrolled and completed the course
    enrollment = CourseEnrollment.query.filter_by(
        student_id=request.user.id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({'error': 'Must be enrolled to review'}), 403

    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'rating' not in data or not isinstance(data['rating'], int) or \
            not 1 <= data['rating'] <= 5:
        return jsonify({'error': 'Invalid rating'}), 400

    # Check if user already reviewed
    existing_review = CourseReview.query.filter_by(
        course_id=course_id,
        student_id=request.user.id
    ).first()

    if existing_review:
        return jsonify({'error': 'Already reviewed this course'}), 400

    review = CourseReview(
        course_id=course_id,
        student_id=request.user.id,
        rating=data['rating'],
        review=data.get('review')
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({
        'message': 'Review submitted successfully',
        'review_id': review.id
    }), 201

@api_bp.route('/courses/categories', methods=['GET'])
def list_categories():
    """Get list of course categories."""
    categories = db.session.query(Course.category)\
        .distinct()\
        .filter(Course.is_published == True)\
        .all()  # noqa: E712

    return jsonify({
        'categories': [category[0] for category in categories]
    })

@api_bp.route('/courses/stats', methods=['GET'])
@require_api_key
def course_stats():
    """Get course statistics."""
    total_courses = Course.query.filter_by(is_published=True).count()
    total_students = CourseEnrollment.query.count()
    avg_rating = db.session.query(db.func.avg(CourseReview.rating))\
        .scalar() or 0.0

    return jsonify({
        'total_courses': total_courses,
        'total_students': total_students,
        'average_rating': float(avg_rating)
    })
