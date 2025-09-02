"""CLI commands for ProjectGenius application."""
import click
from flask import current_app
from flask.cli import with_appcontext
from projectgenius import db
from projectgenius.models import User, Achievement
from projectgenius.courses.models import Course
from werkzeug.security import generate_password_hash
import os


def register_cli_commands(app):
    """Register CLI commands with the Flask app."""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_data_command)
    app.cli.add_command(clean_uploads_command)
    app.cli.add_command(backup_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Create database tables and initialize data."""
    db.create_all()

    # Create default achievements
    default_achievements = [
        {
            'name': 'First Steps',
            'description': 'Enrolled in your first course',
            'points': 10
        },
        {
            'name': 'Knowledge Seeker',
            'description': 'Completed 5 courses',
            'points': 50
        },
        {
            'name': 'Assignment Master',
            'description': 'Completed 10 assignments',
            'points': 30
        },
        {
            'name': 'Quiz Champion',
            'description': 'Scored 100% on 5 quizzes',
            'points': 25
        },
        {
            'name': 'Perfect Student',
            'description': 'Completed a course with 100% score',
            'points': 100
        },
        {
            'name': 'Early Bird',
            'description': 'Submitted 10 assignments before deadline',
            'points': 20
        },
        {
            'name': 'Consistent Learner',
            'description': 'Logged in for 30 consecutive days',
            'points': 40
        },
        {
            'name': 'Course Creator',
            'description': 'Created and published your first course',
            'points': 75
        },
        {
            'name': 'Mentor',
            'description': 'Helped 10 students with their questions',
            'points': 60
        },
        {
            'name': 'Scholar',
            'description': 'Earned 1000 points total',
            'points': 150
        }
    ]

    for achievement_data in default_achievements:
        if not Achievement.query.filter_by(name=achievement_data['name']).first():
            achievement = Achievement(**achievement_data)
            db.session.add(achievement)

    db.session.commit()
    click.echo('Database initialized successfully!')


@click.command('create-admin')
@click.option('--username', prompt=True, help='Admin username')
@click.option('--email', prompt=True, help='Admin email')
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True, help='Admin password')
@click.option('--full-name', prompt=True, help='Admin full name')
@with_appcontext
def create_admin_command(username, email, password, full_name):
    """Create an admin user."""
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        click.echo(f'User {username} already exists!')
        return

    if User.query.filter_by(email=email).first():
        click.echo(f'Email {email} already exists!')
        return

    # Create admin user
    admin = User(
        username=username,
        email=email,
        full_name=full_name,
        password=password,
        is_admin=True,
        is_active=True,
        email_verified=True
    )

    db.session.add(admin)
    db.session.commit()

    click.echo(f'Admin user {username} created successfully!')


@click.command('seed-data')
@click.option('--demo', is_flag=True, help='Create demo data')
@with_appcontext
def seed_data_command(demo):
    """Seed the database with sample data."""
    if demo:
        # Create demo instructor
        demo_instructor = User.query.filter_by(username='demo_instructor').first()
        if not demo_instructor:
            demo_instructor = User(
                username='demo_instructor',
                email='instructor@demo.com',
                full_name='Demo Instructor',
                password='demopass123',
                is_active=True,
                email_verified=True,
                bio='Experienced educator passionate about technology and learning.'
            )
            db.session.add(demo_instructor)
            db.session.flush()

        # Create demo courses
        demo_courses = [
            {
                'title': 'Python Programming for Beginners',
                'description': 'Learn Python programming from scratch with hands-on examples and projects.',
                'level': 'Beginner',
                'category': 'Programming',
                'duration_weeks': 8,
                'price': 0.0,
                'is_published': True
            },
            {
                'title': 'Web Development with Flask',
                'description': 'Build modern web applications using the Flask framework.',
                'level': 'Intermediate',
                'category': 'Web Development',
                'duration_weeks': 10,
                'price': 49.99,
                'is_published': True
            },
            {
                'title': 'Data Science Fundamentals',
                'description': 'Introduction to data science concepts and tools.',
                'level': 'Beginner',
                'category': 'Data Science',
                'duration_weeks': 12,
                'price': 79.99,
                'is_published': True
            },
            {
                'title': 'Machine Learning Basics',
                'description': 'Understanding machine learning algorithms and applications.',
                'level': 'Intermediate',
                'category': 'Machine Learning',
                'duration_weeks': 14,
                'price': 99.99,
                'is_published': True
            },
            {
                'title': 'JavaScript Essentials',
                'description': 'Master JavaScript fundamentals for modern web development.',
                'level': 'Beginner',
                'category': 'Programming',
                'duration_weeks': 6,
                'price': 0.0,
                'is_published': True
            }
        ]

        for course_data in demo_courses:
            if not Course.query.filter_by(title=course_data['title']).first():
                course = Course(
                    instructor_id=demo_instructor.id,
                    **course_data
                )
                db.session.add(course)

        # Create demo students
        demo_students = [
            {
                'username': 'student1',
                'email': 'student1@demo.com',
                'full_name': 'Alice Johnson',
                'password': 'student123'
            },
            {
                'username': 'student2',
                'email': 'student2@demo.com',
                'full_name': 'Bob Smith',
                'password': 'student123'
            },
            {
                'username': 'student3',
                'email': 'student3@demo.com',
                'full_name': 'Carol Davis',
                'password': 'student123'
            }
        ]

        for student_data in demo_students:
            if not User.query.filter_by(username=student_data['username']).first():
                student = User(
                    is_active=True,
                    email_verified=True,
                    **student_data
                )
                db.session.add(student)

        db.session.commit()
        click.echo('Demo data seeded successfully!')
    else:
        click.echo('Use --demo flag to create demo data')


@click.command('clean-uploads')
@click.option('--dry-run', is_flag=True, help='Show files that would be deleted without actually deleting them')
@with_appcontext
def clean_uploads_command(dry_run):
    """Clean up orphaned uploaded files."""
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder or not os.path.exists(upload_folder):
        click.echo('Upload folder not found or not configured')
        return

    # Get all file references in database
    from projectgenius.models import AssignmentSubmission, LessonResource

    referenced_files = set()

    # Get files from assignment submissions
    submissions = AssignmentSubmission.query.filter(
        AssignmentSubmission.file_paths.isnot(None)
    ).all()

    for submission in submissions:
        if submission.file_paths:
            for file_path in submission.file_paths:
                referenced_files.add(os.path.basename(file_path))

    # Get files from lesson resources
    resources = LessonResource.query.filter(
        LessonResource.resource_type == 'file'
    ).all()

    for resource in resources:
        if resource.url and resource.url.startswith('/'):
            referenced_files.add(os.path.basename(resource.url))

    # Find orphaned files
    orphaned_files = []
    total_size = 0

    for root, dirs, files in os.walk(upload_folder):
        for file in files:
            file_path = os.path.join(root, file)
            if file not in referenced_files:
                orphaned_files.append(file_path)
                total_size += os.path.getsize(file_path)

    if not orphaned_files:
        click.echo('No orphaned files found')
        return

    click.echo(f'Found {len(orphaned_files)} orphaned files ({total_size / 1024 / 1024:.2f} MB)')

    if dry_run:
        click.echo('\nFiles that would be deleted:')
        for file_path in orphaned_files[:10]:  # Show first 10
            click.echo(f'  {file_path}')
        if len(orphaned_files) > 10:
            click.echo(f'  ... and {len(orphaned_files) - 10} more')
    else:
        if click.confirm('Do you want to delete these files?'):
            deleted_count = 0
            for file_path in orphaned_files:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                except OSError as e:
                    click.echo(f'Error deleting {file_path}: {e}')

            click.echo(f'Deleted {deleted_count} orphaned files')


@click.command('backup-db')
@click.option('--output', '-o', help='Output file path')
@with_appcontext
def backup_db_command(output):
    """Create a database backup."""
    import json
    from datetime import datetime

    if not output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f'backup_{timestamp}.json'

    backup_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'users': [],
        'courses': [],
        'achievements': []
    }

    # Backup users (excluding sensitive data)
    users = User.query.all()
    for user in users:
        backup_data['users'].append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_admin': user.is_admin,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat()
        })

    # Backup courses
    courses = Course.query.all()
    for course in courses:
        backup_data['courses'].append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'instructor_id': course.instructor_id,
            'level': course.level,
            'category': course.category,
            'price': course.price,
            'duration_weeks': course.duration_weeks,
            'is_published': course.is_published,
            'created_at': course.created_at.isoformat()
        })

    # Backup achievements
    achievements = Achievement.query.all()
    for achievement in achievements:
        backup_data['achievements'].append({
            'id': achievement.id,
            'name': achievement.name,
            'description': achievement.description,
            'points': achievement.points,
            'created_at': achievement.created_at.isoformat()
        })

    try:
        with open(output, 'w') as f:
            json.dump(backup_data, f, indent=2)
        click.echo(f'Database backup created: {output}')
    except Exception as e:
        click.echo(f'Error creating backup: {e}')


@click.command('stats')
@with_appcontext
def stats_command():
    """Display database statistics."""
    users_count = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    admins_count = User.query.filter_by(is_admin=True).count()

    courses_count = Course.query.count()
    published_courses = Course.query.filter_by(is_published=True).count()

    from projectgenius.models import CourseEnrollment, AssignmentSubmission, QuizAttempt

    enrollments_count = CourseEnrollment.query.count()
    submissions_count = AssignmentSubmission.query.count()
    quiz_attempts_count = QuizAttempt.query.count()

    achievements_count = Achievement.query.count()

    click.echo('=== ProjectGenius Statistics ===')
    click.echo(f'Users: {users_count} (Active: {active_users}, Admins: {admins_count})')
    click.echo(f'Courses: {courses_count} (Published: {published_courses})')
    click.echo(f'Enrollments: {enrollments_count}')
    click.echo(f'Submissions: {submissions_count}')
    click.echo(f'Quiz Attempts: {quiz_attempts_count}')
    click.echo(f'Achievements: {achievements_count}')
