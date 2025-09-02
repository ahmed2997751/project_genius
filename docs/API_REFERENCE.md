# ProjectGenius API Reference

## Overview

The ProjectGenius API provides a comprehensive RESTful interface for managing educational content, user interactions, and learning analytics. The API is versioned and returns JSON responses.

**Base URL**: `/api/v1`
**Content Type**: `application/json`
**Authentication**: API Key or Session-based

## Authentication

### API Key Authentication
Include the API key in the request header:
```http
Authorization: Bearer YOUR_API_KEY
```

### Session Authentication
Use session cookies after logging in through the web interface.

## Response Format

All API responses follow a consistent format:

```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Error responses:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## User Management API

### Register User
```http
POST /api/v1/auth/register
```

**Request Body:**
```json
{
  "username": "student123",
  "email": "student@example.com",
  "password": "securepassword",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "student123",
    "email": "student@example.com",
    "api_key": "abc123..."
  }
}
```

### Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "student123",
  "password": "securepassword"
}
```

### Get User Profile
```http
GET /api/v1/users/profile
```

### Update User Profile
```http
PUT /api/v1/users/profile
```

## Course Management API

### List Courses
```http
GET /api/v1/courses
```

**Query Parameters:**
- `category` (optional): Filter by category
- `level` (optional): Filter by difficulty level
- `page` (optional): Page number for pagination
- `limit` (optional): Number of results per page

**Response:**
```json
{
  "success": true,
  "data": {
    "courses": [
      {
        "id": 1,
        "title": "Introduction to Python",
        "description": "Learn Python programming basics",
        "instructor": {
          "id": 5,
          "username": "instructor_jane",
          "full_name": "Jane Smith"
        },
        "level": "Beginner",
        "category": "Programming",
        "price": 0.0,
        "duration_weeks": 8,
        "student_count": 150,
        "average_rating": 4.5,
        "is_published": true
      }
    ],
    "total": 25,
    "page": 1,
    "pages": 3
  }
}
```

### Get Course Details
```http
GET /api/v1/courses/{course_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Introduction to Python",
    "description": "Comprehensive Python course...",
    "modules": [
      {
        "id": 1,
        "title": "Python Basics",
        "order": 1,
        "lessons": [
          {
            "id": 1,
            "title": "Variables and Data Types",
            "content_type": "video",
            "duration_minutes": 45,
            "order": 1
          }
        ]
      }
    ],
    "announcements": [...],
    "reviews": [...]
  }
}
```

### Create Course (Instructor Only)
```http
POST /api/v1/courses
```

**Request Body:**
```json
{
  "title": "Advanced Python",
  "description": "Advanced Python concepts and frameworks",
  "level": "Advanced",
  "category": "Programming",
  "price": 99.99,
  "duration_weeks": 12
}
```

### Enroll in Course
```http
POST /api/v1/courses/{course_id}/enroll
```

### Get Enrollment Status
```http
GET /api/v1/courses/{course_id}/enrollment
```

## Quiz Management API

### List Available Quizzes
```http
GET /api/v1/quizzes
```

**Query Parameters:**
- `course_id` (optional): Filter by course
- `lesson_id` (optional): Filter by lesson

### Get Quiz Details
```http
GET /api/v1/quizzes/{quiz_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Python Basics Quiz",
    "description": "Test your Python knowledge",
    "time_limit": 30,
    "passing_score": 70.0,
    "max_attempts": 3,
    "total_questions": 10,
    "total_points": 100,
    "questions": [
      {
        "id": 1,
        "question_type": "multiple_choice",
        "content": "What is Python?",
        "options": [
          "A programming language",
          "A snake",
          "A web framework",
          "A database"
        ],
        "points": 10
      }
    ]
  }
}
```

### Start Quiz Attempt
```http
POST /api/v1/quizzes/{quiz_id}/start
```

**Response:**
```json
{
  "success": true,
  "data": {
    "attempt_id": 123,
    "started_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-15T11:00:00Z"
  }
}
```

### Submit Quiz Answers
```http
POST /api/v1/quizzes/attempts/{attempt_id}/submit
```

**Request Body:**
```json
{
  "responses": [
    {
      "question_id": 1,
      "answer": "A programming language"
    },
    {
      "question_id": 2,
      "answer": ["option1", "option3"]
    }
  ]
}
```

### Get Quiz Results
```http
GET /api/v1/quizzes/attempts/{attempt_id}/results
```

**Response:**
```json
{
  "success": true,
  "data": {
    "attempt_id": 123,
    "score": 85.0,
    "is_passing": true,
    "time_taken": 1200,
    "completed_at": "2024-01-15T10:50:00Z",
    "responses": [
      {
        "question_id": 1,
        "response": "A programming language",
        "is_correct": true,
        "points_earned": 10,
        "feedback": "Correct! Python is indeed a programming language."
      }
    ]
  }
}
```

## Assignment Management API

### List Assignments
```http
GET /api/v1/assignments
```

### Get Assignment Details
```http
GET /api/v1/assignments/{assignment_id}
```

### Submit Assignment
```http
POST /api/v1/assignments/{assignment_id}/submit
```

**Request Body (File Upload):**
```json
{
  "submission_type": "file",
  "files": ["file1.pdf", "file2.docx"],
  "content": "Additional notes about the submission"
}
```

**Request Body (Text Submission):**
```json
{
  "submission_type": "text",
  "content": "My assignment solution text..."
}
```

### Grade Assignment (Instructor Only)
```http
POST /api/v1/assignments/submissions/{submission_id}/grade
```

**Request Body:**
```json
{
  "grade": 88.5,
  "feedback": "Great work! Consider improving...",
  "rubric_scores": {
    "content": 9,
    "organization": 8,
    "grammar": 9
  }
}
```

## Analytics API

### User Progress Analytics
```http
GET /api/v1/analytics/progress
```

### Course Analytics (Instructor Only)
```http
GET /api/v1/analytics/courses/{course_id}
```

### Quiz Performance Analytics
```http
GET /api/v1/analytics/quizzes/{quiz_id}
```

## Progress Tracking API

### Get Course Progress
```http
GET /api/v1/progress/courses/{course_id}
```

### Mark Lesson Complete
```http
POST /api/v1/progress/lessons/{lesson_id}/complete
```

### Get Module Progress
```http
GET /api/v1/progress/modules/{module_id}
```

## Achievement System API

### List User Achievements
```http
GET /api/v1/achievements
```

### Get Available Badges
```http
GET /api/v1/achievements/badges
```

## File Upload API

### Upload File
```http
POST /api/v1/files/upload
```

**Request:** Multipart form data with file

**Response:**
```json
{
  "success": true,
  "data": {
    "file_id": "abc123",
    "filename": "document.pdf",
    "url": "/files/abc123/document.pdf",
    "size": 1024000,
    "mime_type": "application/pdf"
  }
}
```

## Search API

### Search Courses
```http
GET /api/v1/search/courses
```

**Query Parameters:**
- `q`: Search query
- `filters`: JSON-encoded filter object

### Search Users
```http
GET /api/v1/search/users
```

## Notification API

### Get User Notifications
```http
GET /api/v1/notifications
```

### Mark Notification as Read
```http
POST /api/v1/notifications/{notification_id}/read
```

## Health and Status

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "services": {
      "redis": "connected",
      "ai_service": "available"
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### API Status
```http
GET /api/v1/status
```

## Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Invalid input data |
| `AUTHENTICATION_ERROR` | Invalid credentials |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `NOT_FOUND` | Resource not found |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |
| `SERVICE_UNAVAILABLE` | External service unavailable |

## HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

## Rate Limiting

The API implements rate limiting to prevent abuse:
- **Authentication endpoints**: 5 requests per minute per IP
- **General API endpoints**: 100 requests per minute per user
- **File upload endpoints**: 10 requests per minute per user

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Results per page (default: 20, max: 100)

**Response Format:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 95,
    "has_next": true,
    "has_prev": false
  }
}
```

## Filtering and Sorting

Many endpoints support filtering and sorting:

**Query Parameters:**
- `sort`: Sort field (e.g., `created_at`, `title`)
- `order`: Sort direction (`asc`, `desc`)
- `filter[field]`: Filter by field value

**Example:**
```http
GET /api/v1/courses?sort=created_at&order=desc&filter[level]=Beginner
```

## Webhooks

Configure webhooks to receive notifications about events:

### Available Events
- `course.enrolled`
- `quiz.completed`
- `assignment.submitted`
- `assignment.graded`
- `achievement.earned`

### Webhook Configuration
```http
POST /api/v1/webhooks
```

**Request Body:**
```json
{
  "url": "https://yourapp.com/webhook",
  "events": ["quiz.completed", "assignment.graded"],
  "secret": "webhook_secret"
}
```

## SDKs and Libraries

### Python SDK
```python
from projectgenius_sdk import ProjectGeniusAPI

api = ProjectGeniusAPI(api_key='your_api_key')
courses = api.courses.list()
```

### JavaScript SDK
```javascript
import { ProjectGeniusAPI } from 'projectgenius-js-sdk';

const api = new ProjectGeniusAPI('your_api_key');
const courses = await api.courses.list();
```

## Support

For API support and questions:
- **Documentation**: [https://docs.projectgenius.edu/api](https://docs.projectgenius.edu/api)
- **Issues**: [GitHub Issues](https://github.com/projectgenius/api/issues)
- **Email**: api-support@projectgenius.edu

---

**Version**: 1.0
**Last Updated**: January 15, 2024
**API Status**: [https://status.projectgenius.edu](https://status.projectgenius.edu)