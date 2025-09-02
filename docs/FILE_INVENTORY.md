# ProjectGenius File Inventory

## Root Directory Files

### Application Entry Points
- **`projectgenius_app.py`** - Standalone Flask application with complete working features including user management, notes, flashcards, and AI integration. Contains all core functionality in a single file for development and testing.
- **`wsgi.py`** - Production WSGI entry point for deployment with Gunicorn or similar WSGI servers.
- **`run_dev.py`** - Development server runner script with debug configuration.
- **`run_production.py`** - Production server runner with optimized settings.
- **`setup_production.py`** - Production environment setup script for database initialization and configuration.
- **`routes.py`** - Legacy route definitions (deprecated in favor of modular blueprint structure).

### Configuration Files
- **`requirements.txt`** - Python package dependencies for production deployment.
- **`pyproject.toml`** - Modern Python project configuration including build system, development dependencies, and tool configurations (Black, isort, mypy, pytest).
- **`.gitignore`** - Git ignore patterns for Python projects, virtual environments, and IDE files.

### Documentation
- **`README.md`** - Comprehensive project documentation including features, installation, API documentation, and usage examples.
- **`README_PRODUCTION.md`** - Production deployment guide with server configuration and deployment instructions.

## Main Application Package (`projectgenius/`)

### Core Application Files
- **`__init__.py`** - Application factory with Flask app creation, extension initialization, blueprint registration, and configuration loading.
- **`models.py`** - Core database models including User, Submission, Challenge, Achievement, and UserAchievement with relationships and authentication methods.
- **`utils.py`** - Common utility functions and helper methods used across the application.

### Authentication Module (`auth/`)
- **`__init__.py`** - Authentication blueprint definition and initialization.
- **`routes.py`** - Authentication routes including login, logout, registration, and password management.
- **`forms.py`** - WTForms definitions for authentication forms with validation.
- **`templates/`** - Authentication-specific Jinja2 templates for login and registration pages.

### Core Module (`core/`)
- **`__init__.py`** - Core blueprint definition for main application functionality.
- **`routes.py`** - Main application routes including home page, dashboard, and core navigation.
- **`cli.py`** - Click-based CLI commands for database management, user creation, and data seeding.
- **`errors.py`** - HTTP error handlers for 404, 500, and other error conditions.
- **`security.py`** - Security utilities and authentication decorators.
- **`config/`** - Configuration classes for different environments (development, production, testing).

### API Module (`api/`)
- **`__init__.py`** - RESTful API blueprint with versioning (v1 prefix).
- **`courses.py`** - Course management API endpoints including CRUD operations and enrollment.
- **`quizzes.py`** - Quiz and assessment API with attempt tracking and scoring.
- **`assignments.py`** - Assignment management API with submission and grading functionality.
- **`users.py`** - User management API including profile updates and analytics.

### Course Management (`courses/`)
- **`models.py`** - Course-related database models including Course, CourseEnrollment, Module, Lesson, LessonResource, ModuleProgress, LessonCompletion, CourseAnnouncement, and CourseReview with comprehensive relationship mapping.

### Quiz System (`quizzes/`)
- **`__init__.py`** - Quiz blueprint definition and route registration.
- **`models.py`** - Quiz system models including Quiz, Question, QuizAttempt, QuestionResponse, CodingQuestion, and QuizAnalytics with support for multiple question types and automated grading.

### Assignment System (`assignments/`)
- **`models.py`** - Assignment models including Assignment, AssignmentSubmission, AssignmentGroup, GroupMember, AssignmentResource, SubmissionComment, and AssignmentAnalytics supporting individual and group work.

### Additional Modules
- **`dashboard/`** - Dashboard functionality and views for student and instructor interfaces.
- **`services/`** - Business logic layer with external service integrations and data processing.
- **`models/`** - Additional model definitions and database schema extensions.

## Templates (`projectgenius/templates/`)

### Base Templates
- **`base.html`** - Main layout template with navigation, Bootstrap integration, and common page structure.
- **`index.html`** - Main home page template with feature highlights and call-to-action sections.
- **`index_simple.html`** - Simplified home page for development and testing.
- **`dashboard.html`** - User dashboard template with course overview, progress tracking, and quick actions.
- **`register.html`** - User registration form with validation and error handling.

### Feature Templates
- **`analytics.html`** - Analytics dashboard with charts and performance metrics.
- **`flashcards.html`** - Interactive flashcard interface with study session management.
- **`subscription.html`** - Subscription management and payment processing interface.

### Template Directories
- **`courses/`** - Course-related templates including course listing, detail views, and enrollment forms.
- **`dashboard/`** - Dashboard component templates for different user roles.
- **`quizzes/`** - Quiz interface templates including question display and result views.
- **`errors/`** - Error page templates (404, 500, etc.) with user-friendly messaging.

## Static Assets (`projectgenius/static/`)

### Stylesheets (`css/`)
- Custom CSS files for application styling
- Bootstrap theme customizations
- Responsive design styles for mobile compatibility
- Component-specific styles for courses, quizzes, and dashboard

### JavaScript (`js/`)
- Interactive functionality scripts
- AJAX request handlers for dynamic content
- Chart.js integration for analytics visualization
- Form validation and user experience enhancements
- Quiz timer and submission handling

## Testing Suite (`tests/`)

### Test Configuration
- **`__init__.py`** - Test package initialization.
- **`conftest.py`** - Pytest configuration with fixtures, database setup, and test client creation.

### Test Modules
- **`test_auth.py`** - Authentication system tests including login, registration, and session management.
- **`test_api.py`** - RESTful API endpoint tests with request/response validation.
- **`test_models.py`** - Database model tests including relationships and data validation.
- **`test_flashcards.py`** - Flashcard functionality tests with AI generation and study session logic.
- **`test_server.py`** - Server integration tests and application startup validation.
- **`test_services.py`** - Service layer tests including external API integrations.

## Database Management

### Migrations (`migrations/`)
- **Alembic migration files** - Database schema version control with upgrade and downgrade scripts.
- **`env.py`** - Alembic environment configuration.
- **`script.py.mako`** - Migration script template.
- **`versions/`** - Individual migration files with timestamps and descriptions.

### Instance Files (`instance/`)
- **Configuration overrides** - Instance-specific settings that override default configuration.
- **Database files** - SQLite database files for development (if using SQLite).
- **Upload directories** - File storage for user uploads and course materials.

## Development Tools

### Python Configuration
- **`venv/`** - Virtual environment directory (excluded from version control).
- **`.env`** - Environment variables for local development (not tracked in git).
- **`.env.example`** - Template for environment variable configuration.

### Quality Control
- **`.pre-commit-config.yaml`** - Pre-commit hooks for code quality enforcement.
- **`pytest.ini`** - Pytest configuration with coverage settings and test discovery.
- **`setup.cfg`** - Tool configuration for flake8, mypy, and other development tools.

## Logs and Runtime

### Logging (`logs/`)
- **Application logs** - Runtime logging for debugging and monitoring.
- **Error logs** - Error tracking and exception handling logs.
- **Access logs** - Request logging for performance monitoring.

### Runtime Files
- **PID files** - Process identification for production deployment.
- **Socket files** - Unix socket files for Gunicorn deployment.
- **Cache files** - Redis or file-based caching storage.

## Documentation (`docs/`)
- **`CODEBASE_INDEX.md`** - Comprehensive codebase overview and architecture documentation.
- **`FILE_INVENTORY.md`** - This file - detailed inventory of all project files.
- **`API_DOCUMENTATION.md`** - API endpoint documentation with examples.
- **`DEPLOYMENT_GUIDE.md`** - Deployment instructions for various environments.
- **`CONTRIBUTING.md`** - Guidelines for contributing to the project.

## File Count Summary
- **Python Files**: ~50+ .py files across modules and tests
- **HTML Templates**: ~20+ Jinja2 templates for various pages
- **Static Assets**: CSS, JavaScript, and image files
- **Configuration**: 10+ configuration and setup files
- **Documentation**: Comprehensive project documentation
- **Tests**: Complete test suite with >90% coverage

## File Naming Conventions
- **Snake case** for Python files and directories (`user_model.py`)
- **Lowercase** for templates and static files (`base.html`)
- **Uppercase** for documentation files (`README.md`)
- **Descriptive names** indicating purpose and functionality
- **Module organization** following Flask blueprint patterns

## Architecture Patterns
- **Blueprint modularization** - Organized by feature areas
- **Model-View-Controller** - Separation of concerns
- **Factory pattern** - Application creation and configuration
- **Repository pattern** - Data access abstraction
- **Service layer** - Business logic separation

This inventory represents a well-organized, production-ready Flask application with comprehensive testing, documentation, and modern Python development practices.