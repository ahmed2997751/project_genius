# ProjectGenius - AI-Powered Education Platform

[![SDG 4: Quality Education](https://img.shields.io/badge/SDG%204-Quality%20Education-blue.svg)](https://sdgs.un.org/goals/goal4)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)

**ProjectGenius** is a comprehensive AI-powered education platform that provides structured learning through courses, interactive quizzes, assignments, and achievement systems. Built to support **UN Sustainable Development Goal 4: Quality Education**, ProjectGenius makes quality education accessible, engaging, and effective for learners worldwide.

## 🌟 Features

### Core Learning Features
- **Comprehensive Course System**: Structured courses with modules, lessons, and progress tracking
- **Interactive Quizzes**: Auto-graded quizzes with multiple question types and instant feedback
- **Assignment Management**: File uploads, group assignments, and instructor grading system
- **Achievement System**: Gamified learning with badges and progress rewards
- **Real-time Progress Tracking**: Detailed analytics and learning insights

### User Management
- **Secure Authentication**: Password-based authentication with bcrypt hashing
- **Role-based Access**: Student and instructor roles with appropriate permissions
- **User Profiles**: Customizable profiles with learning history and achievements
- **Dashboard**: Personalized learning dashboard with activity tracking

### Advanced Features
- **Course Reviews & Ratings**: Student feedback and course recommendation system
- **Group Learning**: Collaborative assignments and study groups
- **Announcements**: Course-specific announcements and notifications
- **Analytics Dashboard**: Comprehensive learning analytics for students and instructors
- **RESTful API**: Complete API for mobile app integration and third-party services

## 🛠 Tech Stack

### Backend
- **Flask** - Modern Python web framework with application factory pattern
- **SQLAlchemy** - Advanced ORM with relationship mapping and migrations
- **Flask-Migrate** - Database version control and schema management
- **PostgreSQL/SQLite** - Robust database support for development and production
- **Bcrypt** - Secure password hashing and authentication
- **Flask-WTF** - Form handling with CSRF protection

### Frontend
- **Jinja2 Templates** - Dynamic HTML generation with template inheritance
- **Bootstrap 5** - Responsive UI framework with modern design
- **JavaScript (Vanilla)** - Interactive functionality and AJAX requests
- **Font Awesome** - Comprehensive icon library
- **Chart.js** - Data visualization for analytics dashboards

### Development & Deployment
- **Click** - Command-line interface for database management
- **Python-dotenv** - Environment variable management
- **Gunicorn** - Production WSGI HTTP server
- **Redis** - Caching and session storage (optional)

## 📁 Project Structure

```
ProjectGenius/
├── projectgenius/                 # Main application package
│   ├── __init__.py               # Application factory
│   ├── models.py                 # Database models
│   ├── utils.py                  # Utility functions
│   │
│   ├── auth/                     # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py            # Auth routes (login, register, logout)
│   │   ├── forms.py             # Authentication forms
│   │   └── templates/           # Auth-specific templates
│   │
│   ├── core/                     # Core application routes
│   │   ├── __init__.py
│   │   ├── routes.py            # Main routes (home, dashboard, courses)
│   │   ├── cli.py               # CLI commands
│   │   ├── errors.py            # Error handlers
│   │   └── config/              # Configuration management
│   │
│   ├── api/                      # RESTful API endpoints
│   │   ├── __init__.py
│   │   ├── courses.py           # Course API
│   │   ├── quizzes.py           # Quiz API
│   │   ├── assignments.py       # Assignment API
│   │   └── users.py             # User API
│   │
│   ├── courses/                  # Course-related models
│   │   ├── models.py            # Course, Module, Lesson models
│   │   └── __init__.py
│   │
│   ├── quizzes/                  # Quiz system models
│   │   ├── models.py            # Quiz, Question, Attempt models
│   │   └── __init__.py
│   │
│   ├── assignments/              # Assignment system models
│   │   ├── models.py            # Assignment, Submission models
│   │   └── __init__.py
│   │
│   └── templates/                # HTML templates
│       ├── base.html            # Base template
│       ├── index.html           # Home page
│       ├── auth/                # Authentication templates
│       ├── dashboard/           # Dashboard templates
│       ├── courses/             # Course templates
│       └── errors/              # Error page templates
│
├── static/                       # Static assets
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Images and media
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Test configuration
│   ├── test_auth.py             # Authentication tests
│   ├── test_courses.py          # Course functionality tests
│   └── test_api.py              # API endpoint tests
│
├── migrations/                   # Database migrations
├── instance/                     # Instance-specific files
├── logs/                         # Application logs
│
├── main.py                       # Application entry point
├── wsgi.py                       # Production WSGI entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
└── README.md                     # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- PostgreSQL 13+ (or SQLite for development)
- Redis (optional, for caching and sessions)
- Modern web browser

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/projectgenius.git
   cd ProjectGenius
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Database Setup**
   ```bash
   # Initialize database
   flask init-db
   
   # Create database migrations
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Create Admin User**
   ```bash
   flask create-admin
   # Follow the prompts to create an admin account
   ```

7. **Seed Demo Data (Optional)**
   ```bash
   flask seed-data --demo
   ```

8. **Run the Application**
   ```bash
   # Development server
   python main.py
   
   # Or using Flask CLI
   flask run --host=0.0.0.0 --port=5000
   ```

9. **Access the Application**
   Open your browser and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# Basic Configuration
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///projectgenius.db

# For PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost/projectgenius

# Security
JWT_SECRET_KEY=your-jwt-secret-key
BCRYPT_LOG_ROUNDS=12

# File Uploads
UPLOAD_FOLDER=instance/uploads
MAX_CONTENT_LENGTH=16777216

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Database Configuration

The application supports both SQLite (for development) and PostgreSQL (for production):

**SQLite (Development)**:
```env
DATABASE_URL=sqlite:///projectgenius.db
```

**PostgreSQL (Production)**:
```env
DATABASE_URL=postgresql://user:password@localhost/projectgenius
```

## 📚 API Documentation

The application provides a comprehensive RESTful API for all major operations:

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /auth/check` - Check authentication status

### Course Endpoints
- `GET /api/v1/courses` - List all courses
- `GET /api/v1/courses/{id}` - Get course details
- `POST /api/v1/courses` - Create new course (instructor only)
- `PUT /api/v1/courses/{id}` - Update course (instructor only)
- `POST /api/v1/courses/{id}/enroll` - Enroll in course

### Quiz Endpoints
- `GET /api/v1/quizzes` - List available quizzes
- `POST /api/v1/quizzes/{id}/start` - Start quiz attempt
- `POST /api/v1/quizzes/attempts/{id}/submit` - Submit quiz answers
- `GET /api/v1/quizzes/attempts/{id}/results` - Get quiz results

### Assignment Endpoints
- `GET /api/v1/assignments` - List assignments
- `POST /api/v1/assignments/{id}/submit` - Submit assignment
- `POST /api/v1/assignments/submissions/{id}/grade` - Grade submission (instructor only)

## 🎯 Usage Examples

### Creating a Course (Instructor)

```python
import requests

# Login first
login_response = requests.post('/auth/login', json={
    'username': 'instructor',
    'password': 'password'
})

# Create course
course_data = {
    'title': 'Introduction to Python',
    'description': 'Learn Python programming from basics',
    'level': 'Beginner',
    'category': 'Programming',
    'duration_weeks': 8,
    'price': 0.0
}

response = requests.post('/api/v1/courses', json=course_data)
```

### Enrolling in a Course (Student)

```python
# Enroll in course
response = requests.post(f'/api/v1/courses/{course_id}/enroll')
```

### Taking a Quiz

```python
# Start quiz attempt
start_response = requests.post(f'/api/v1/quizzes/{quiz_id}/start')
attempt_id = start_response.json()['attempt_id']

# Submit answers
answers = {
    'responses': [
        {'question_id': 1, 'answer': 'A programming language'},
        {'question_id': 2, 'answer': 'True'}
    ]
}

submit_response = requests.post(f'/api/v1/quizzes/attempts/{attempt_id}/submit', json=answers)
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=projectgenius

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Test Categories
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **API Tests**: Test RESTful API endpoints
- **Database Tests**: Test database operations and models

## 🚀 Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# With configuration file
gunicorn -c gunicorn.conf.py wsgi:app
```

### Environment Setup

For production, ensure these environment variables are set:

```env
FLASK_ENV=production
DEBUG=False
SQLALCHEMY_ECHO=False
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://user:pass@host/db
```

### Database Migration in Production

```bash
# Apply migrations
flask db upgrade

# Create admin user
flask create-admin

# Set up monitoring
flask stats
```

## 📈 Monitoring & Analytics

The application includes comprehensive monitoring and analytics:

- **User Analytics**: Track user engagement, course completion rates
- **Course Analytics**: Monitor course performance, student feedback
- **System Health**: Database performance, API response times
- **Learning Analytics**: Progress tracking, achievement statistics

Access analytics through:
- **Admin Dashboard**: `/admin/analytics`
- **API Endpoints**: `/api/v1/analytics/*`
- **CLI Commands**: `flask stats`

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your feature or fix
4. **Add Tests**: Ensure your changes are tested
5. **Run Tests**: `pytest`
6. **Commit Changes**: `git commit -m 'Add amazing feature'`
7. **Push to Branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**

### Development Guidelines

- **Code Style**: Follow PEP 8 standards
- **Testing**: Maintain >90% test coverage
- **Documentation**: Update docs for new features
- **Security**: Follow security best practices
- **Performance**: Consider performance implications

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [https://projectgenius.dev/docs](https://projectgenius.dev/docs)
- **Issues**: [GitHub Issues](https://github.com/yourusername/projectgenius/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/projectgenius/discussions)
- **Email**: support@projectgenius.dev

## 🙏 Acknowledgments

- **UN SDG 4**: Inspired by the goal of Quality Education for all
- **Flask Community**: For the excellent web framework
- **Bootstrap Team**: For the responsive UI framework
- **Font Awesome**: For the comprehensive icon library
- **Contributors**: All developers who have contributed to this project

## 🔮 Roadmap

### Version 2.0
- [ ] Mobile application (React Native)
- [ ] Video lessons and live streaming
- [ ] Advanced AI features for personalized learning
- [ ] Blockchain certificates and credentials
- [ ] Multi-language support

### Version 2.1
- [ ] Social learning features
- [ ] Marketplace for course creators
- [ ] Advanced analytics and reporting
- [ ] Integration with external LMS systems

---

**ProjectGenius** - Empowering education through technology 🎓✨

*Built with ❤️ for learners worldwide*