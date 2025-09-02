# ProjectGenius Codebase Index

## Overview

ProjectGenius is a comprehensive AI-powered education platform built with Flask that provides structured learning through courses, interactive quizzes, assignments, and achievement systems. The project supports UN Sustainable Development Goal 4: Quality Education.

## Project Structure

### Root Directory
```
ProjectGenius/
├── projectgenius/           # Main application package
├── static/                  # Static assets (CSS, JS, images)
├── tests/                   # Test suite
├── migrations/              # Database migrations
├── instance/                # Instance-specific files
├── logs/                    # Application logs
├── docs/                    # Documentation
├── venv/                    # Virtual environment
├── projectgenius_app.py     # Standalone working application
├── routes.py                # Legacy routes file
├── wsgi.py                  # Production WSGI entry point
├── run_dev.py              # Development server runner
├── run_production.py       # Production server runner
├── setup_production.py     # Production setup script
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
└── README_PRODUCTION.md    # Production deployment guide
```

## Core Application (`projectgenius/`)

### Main Application Files

#### `__init__.py` - Application Factory
- **Purpose**: Creates Flask application instance using factory pattern
- **Key Functions**: `create_app(config_name)`
- **Dependencies**: Flask, SQLAlchemy, Flask-Migrate
- **Registers**: Blueprints, error handlers, CLI commands
- **Features**: Proxy fix for deployment, instance folder creation

#### `models.py` - Core Database Models
- **Purpose**: Core application models
- **Models**:
  - `User`: User account management with bcrypt password hashing
  - `Submission`: Code submission tracking
  - `Challenge`: Programming challenges
  - `Achievement`: User achievement system
  - `UserAchievement`: Association table for user achievements
- **Features**: API key generation, password hashing, relationships

#### `utils.py` - Utility Functions
- **Purpose**: Common utility functions across the application
- **Location**: `projectgenius/utils.py`

### Modular Structure

#### Authentication Module (`auth/`)
- **Blueprint**: `auth_bp`
- **Files**:
  - `__init__.py`: Blueprint definition
  - `routes.py`: Authentication routes (login, register, logout)
  - `forms.py`: WTForms for authentication
  - `templates/`: Auth-specific templates
- **Features**: Secure login/logout, user registration, session management

#### Core Module (`core/`)
- **Blueprint**: `core_bp`
- **Files**:
  - `__init__.py`: Blueprint definition
  - `routes.py`: Main application routes (home, dashboard, courses)
  - `cli.py`: CLI commands for database management
  - `errors.py`: Error handlers for HTTP errors
  - `security.py`: Security utilities
  - `config/`: Configuration management
- **Features**: Main navigation, error handling, CLI tools

#### API Module (`api/`)
- **Blueprint**: `api_bp` (prefix: `/api/v1`)
- **Files**:
  - `__init__.py`: API blueprint definition
  - `courses.py`: Course management API endpoints
  - `quizzes.py`: Quiz and assessment API
  - `assignments.py`: Assignment management API
  - `users.py`: User management API
- **Features**: RESTful API, JSON responses, API versioning

#### Courses Module (`courses/`)
- **Files**:
  - `models.py`: Course-related database models
- **Models**:
  - `Course`: Course information and metadata
  - `CourseEnrollment`: Student enrollment tracking
  - `Module`: Course modules/sections
  - `Lesson`: Individual lessons within modules
  - `LessonResource`: Lesson attachments and resources
  - `ModuleProgress`: Student progress tracking
  - `LessonCompletion`: Lesson completion records
  - `CourseAnnouncement`: Course announcements
  - `CourseReview`: Course ratings and reviews
- **Features**: Progress tracking, enrollment management, course reviews

#### Quizzes Module (`quizzes/`)
- **Blueprint**: `quizzes_bp`
- **Files**:
  - `__init__.py`: Blueprint definition
  - `models.py`: Quiz and assessment models
- **Models**:
  - `Quiz`: Quiz configuration and metadata
  - `Question`: Quiz questions with multiple types
  - `QuizAttempt`: Student quiz attempts
  - `QuestionResponse`: Individual question responses
  - `CodingQuestion`: Specialized coding challenge questions
  - `QuizAnalytics`: Quiz performance analytics
- **Features**: Multiple question types, timed quizzes, auto-grading, analytics

#### Assignments Module (`assignments/`)
- **Files**:
  - `models.py`: Assignment and submission models
- **Models**:
  - `Assignment`: Assignment configuration and requirements
  - `AssignmentSubmission`: Student submissions
  - `AssignmentGroup`: Group assignment management
  - `GroupMember`: Group membership tracking
  - `AssignmentResource`: Assignment attachments
  - `SubmissionComment`: Feedback and comments
  - `AssignmentAnalytics`: Assignment performance analytics
- **Features**: Group assignments, file uploads, rubric grading, analytics

#### Services Module (`services/`)
- **Purpose**: Business logic and external service integrations
- **Location**: `projectgenius/services/`

#### Dashboard Module (`dashboard/`)
- **Purpose**: User dashboard functionality
- **Location**: `projectgenius/dashboard/`

#### Models Module (`models/`)
- **Purpose**: Additional model definitions
- **Location**: `projectgenius/models/`

### Templates Structure (`templates/`)

#### Base Templates
- `base.html`: Main template with navigation and layout
- `index.html`: Home page template
- `index_simple.html`: Simplified home page
- `dashboard.html`: User dashboard
- `register.html`: User registration form

#### Feature-Specific Templates
- `auth/`: Authentication templates (login, register)
- `courses/`: Course-related templates
- `dashboard/`: Dashboard components
- `quizzes/`: Quiz and assessment templates
- `errors/`: Error page templates

#### Specialized Templates
- `analytics.html`: Analytics dashboard
- `flashcards.html`: Flashcard interface
- `subscription.html`: Subscription management

### Static Assets (`static/`)

#### CSS Stylesheets (`css/`)
- Custom styles for the application
- Bootstrap customizations
- Responsive design styles

#### JavaScript (`js/`)
- Interactive functionality
- AJAX requests
- Chart.js for analytics visualization
- Form validation and UX enhancements

## Entry Points

### Development
- **`projectgenius_app.py`**: Standalone Flask application with core features
  - Complete working app with users, notes, flashcards
  - AI integration for flashcard generation
  - Simple database models
  - Integrated authentication
  - API endpoints for health checks

### Production
- **`wsgi.py`**: WSGI entry point for production deployment
- **`run_production.py`**: Production server runner with Gunicorn
- **`setup_production.py`**: Production environment setup

### Legacy
- **`routes.py`**: Legacy route definitions
- **`run_dev.py`**: Development server runner

## Database Architecture

### Core Models
- **User Management**: Users, authentication, profiles
- **Course System**: Courses, modules, lessons, enrollments
- **Assessment System**: Quizzes, questions, attempts, responses
- **Assignment System**: Assignments, submissions, groups, grading
- **Progress Tracking**: Enrollment progress, module completion, analytics
- **Achievement System**: Badges, achievements, user progress

### Database Features
- **PostgreSQL/SQLite Support**: Flexible database backend
- **SQLAlchemy ORM**: Advanced relationship mapping
- **Flask-Migrate**: Database version control
- **Relationship Management**: Proper foreign keys and cascading
- **Analytics Tables**: Performance tracking and reporting

## Testing Suite (`tests/`)

### Test Files
- `conftest.py`: Test configuration and fixtures
- `test_auth.py`: Authentication system tests
- `test_api.py`: API endpoint tests
- `test_models.py`: Database model tests
- `test_flashcards.py`: Flashcard functionality tests
- `test_server.py`: Server integration tests
- `test_services.py`: Service layer tests

### Testing Features
- **Pytest Framework**: Modern testing with fixtures
- **Coverage Reporting**: Code coverage analysis
- **Integration Tests**: Full application testing
- **API Testing**: RESTful endpoint validation
- **Database Testing**: Model and relationship testing

## Configuration Management

### Environment Configuration
- **Development**: `development.py`
- **Production**: `production.py`
- **Testing**: `testing.py`

### Environment Variables
- `FLASK_ENV`: Environment setting
- `SECRET_KEY`: Application secret key
- `DATABASE_URL`: Database connection string
- `DEEPSEEK_API_KEY`: AI service integration
- `HUGGINGFACE_API_KEY`: AI model access

## API Architecture

### Versioning
- **Current Version**: `v1`
- **URL Prefix**: `/api/v1`
- **Format**: JSON responses

### Endpoint Categories
- **Authentication**: Login, register, logout
- **Courses**: CRUD operations, enrollment
- **Quizzes**: Quiz management, attempts, results
- **Assignments**: Assignment CRUD, submissions, grading
- **Users**: Profile management, analytics

## Security Features

### Authentication
- **bcrypt Password Hashing**: Secure password storage
- **Session Management**: Flask session handling
- **API Key Authentication**: API access control
- **CSRF Protection**: Form security with Flask-WTF

### Authorization
- **Role-based Access**: Student/Instructor permissions
- **Resource Ownership**: User-specific data access
- **Admin Controls**: Administrative functionality

## AI Integration

### Supported Services
- **DeepSeek API**: Advanced AI capabilities
- **Hugging Face**: Machine learning models
- **Flashcard Generation**: AI-powered content creation

### Features
- **Content Analysis**: Automatic flashcard generation
- **Personalized Learning**: AI-driven recommendations
- **Assessment Generation**: Automated quiz creation

## Development Tools

### Code Quality
- **Black**: Code formatting
- **Flake8**: Linting and style checking
- **isort**: Import sorting
- **mypy**: Type checking
- **pre-commit**: Git hooks for quality control

### Dependencies Management
- **requirements.txt**: Production dependencies
- **pyproject.toml**: Modern Python project configuration
- **pip-tools**: Dependency management

## Deployment

### Development
```bash
python run_dev.py
# or
python projectgenius_app.py
```

### Production
```bash
python setup_production.py
python run_production.py
# or
gunicorn -c gunicorn.conf.py wsgi:app
```

### Docker Support
- Containerization ready
- Environment variable configuration
- Multi-stage builds supported

## Key Features Summary

### Educational Features
- **Comprehensive Course System**: Multi-level course structure
- **Interactive Assessments**: Quizzes with multiple question types
- **Assignment Management**: Individual and group assignments
- **Progress Tracking**: Detailed learning analytics
- **Achievement System**: Gamified learning experience

### Technical Features
- **Modular Architecture**: Blueprint-based organization
- **RESTful API**: Complete API for frontend/mobile integration
- **Database Migrations**: Version-controlled schema changes
- **Comprehensive Testing**: Unit and integration test coverage
- **AI Integration**: Multiple AI service support
- **Security**: Enterprise-level security practices

### User Experience
- **Responsive Design**: Bootstrap-based UI
- **Dashboard**: Centralized user interface
- **Real-time Updates**: AJAX-powered interactions
- **Analytics**: Performance tracking and insights
- **Multi-role Support**: Students and instructors

## Future Roadmap

### Version 2.0
- Mobile application (React Native)
- Video lessons and live streaming
- Advanced AI personalization
- Blockchain certificates
- Multi-language support

### Version 2.1
- Social learning features
- Course marketplace
- Advanced analytics
- External LMS integration

## Contributing

### Development Setup
1. Clone repository
2. Create virtual environment
3. Install dependencies
4. Configure environment variables
5. Initialize database
6. Run tests
7. Start development server

### Code Standards
- Follow PEP 8 guidelines
- Maintain >90% test coverage
- Update documentation for new features
- Security-first development approach
- Performance optimization considerations

This codebase represents a production-ready educational platform with enterprise-level architecture, comprehensive testing, and modern development practices.