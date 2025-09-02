# ProjectGenius Database Schema Documentation

## Overview

ProjectGenius uses a relational database design with PostgreSQL as the primary database and SQLite for development. The schema is managed using Flask-Migrate (Alembic) for version control and migrations.

## Database Configuration

### Supported Databases
- **Production**: PostgreSQL 13+
- **Development**: SQLite 3.8+
- **Testing**: In-memory SQLite

### Connection Examples
```python
# PostgreSQL
DATABASE_URL = "postgresql://username:password@localhost:5432/projectgenius"

# SQLite
DATABASE_URL = "sqlite:///projectgenius.db"
```

## Core Tables

### Users Table (`users`)
Primary table for user account management and authentication.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    full_name VARCHAR(120),
    avatar_url VARCHAR(255),
    api_key VARCHAR(64) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE NOT NULL,
    bio TEXT,
    last_login TIMESTAMP,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_api_key ON users(api_key);
CREATE INDEX idx_users_active ON users(is_active);
```

**Key Features:**
- Bcrypt password hashing
- Unique API key generation
- Soft deletion support via `is_active`
- Email verification tracking
- Admin role management

## Course Management Tables

### Courses Table (`courses`)
Central table for course information and metadata.

```sql
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    instructor_id INTEGER REFERENCES users(id) NOT NULL,
    cover_image VARCHAR(255),
    level VARCHAR(20) NOT NULL, -- 'Beginner', 'Intermediate', 'Advanced'
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2) DEFAULT 0.0 NOT NULL,
    duration_weeks INTEGER NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_published ON courses(is_published);
CREATE INDEX idx_courses_category ON courses(category);
CREATE INDEX idx_courses_level ON courses(level);
```

### Course Enrollments Table (`course_enrollments`)
Tracks student enrollment in courses with progress tracking.

```sql
CREATE TABLE course_enrollments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id) NOT NULL,
    course_id INTEGER REFERENCES courses(id) NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    progress DECIMAL(5,2) DEFAULT 0.0, -- 0-100%
    last_accessed TIMESTAMP,
    payment_status VARCHAR(20) DEFAULT 'pending',
    certificate_issued BOOLEAN DEFAULT FALSE,
    UNIQUE(student_id, course_id)
);

-- Indexes
CREATE INDEX idx_enrollments_student ON course_enrollments(student_id);
CREATE INDEX idx_enrollments_course ON course_enrollments(course_id);
CREATE INDEX idx_enrollments_status ON course_enrollments(payment_status);
```

### Modules Table (`modules`)
Course modules/sections within courses.

```sql
CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    order_index INTEGER NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_modules_course ON modules(course_id);
CREATE INDEX idx_modules_order ON modules(course_id, order_index);
```

### Lessons Table (`lessons`)
Individual lessons within course modules.

```sql
CREATE TABLE lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER REFERENCES modules(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    content_type VARCHAR(20) NOT NULL, -- 'video', 'text', 'quiz', 'assignment'
    duration_minutes INTEGER,
    order_index INTEGER NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_lessons_module ON lessons(module_id);
CREATE INDEX idx_lessons_order ON lessons(module_id, order_index);
CREATE INDEX idx_lessons_type ON lessons(content_type);
```

### Lesson Resources Table (`lesson_resources`)
Attachments and resources for lessons.

```sql
CREATE TABLE lesson_resources (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    resource_type VARCHAR(20) NOT NULL, -- 'file', 'link', 'pdf', 'video'
    url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_resources_lesson ON lesson_resources(lesson_id);
```

## Progress Tracking Tables

### Module Progress Table (`module_progress`)
Tracks student progress through course modules.

```sql
CREATE TABLE module_progress (
    id SERIAL PRIMARY KEY,
    enrollment_id INTEGER REFERENCES course_enrollments(id) NOT NULL,
    module_id INTEGER REFERENCES modules(id) NOT NULL,
    progress DECIMAL(5,2) DEFAULT 0.0, -- 0-100%
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    last_accessed TIMESTAMP,
    UNIQUE(enrollment_id, module_id)
);

-- Indexes
CREATE INDEX idx_module_progress_enrollment ON module_progress(enrollment_id);
CREATE INDEX idx_module_progress_module ON module_progress(module_id);
```

### Lesson Completions Table (`lesson_completions`)
Tracks completed lessons by students.

```sql
CREATE TABLE lesson_completions (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES users(id) NOT NULL,
    lesson_id INTEGER REFERENCES lessons(id) NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, lesson_id)
);

-- Indexes
CREATE INDEX idx_completions_student ON lesson_completions(student_id);
CREATE INDEX idx_completions_lesson ON lesson_completions(lesson_id);
```

## Quiz System Tables

### Quizzes Table (`quizzes`)
Quiz configuration and metadata.

```sql
CREATE TABLE quizzes (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    time_limit INTEGER, -- minutes
    passing_score DECIMAL(5,2) DEFAULT 70.0 NOT NULL,
    max_attempts INTEGER,
    is_published BOOLEAN DEFAULT FALSE,
    shuffle_questions BOOLEAN DEFAULT TRUE,
    show_correct_answers BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_quizzes_lesson ON quizzes(lesson_id);
CREATE INDEX idx_quizzes_published ON quizzes(is_published);
```

### Questions Table (`questions`)
Individual quiz questions with support for multiple types.

```sql
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) NOT NULL,
    question_type VARCHAR(20) NOT NULL, -- 'multiple_choice', 'true_false', 'essay', 'coding'
    content TEXT NOT NULL,
    options JSONB, -- For multiple choice questions
    correct_answer JSONB, -- Can store multiple correct answers
    explanation TEXT,
    points DECIMAL(5,2) DEFAULT 1.0 NOT NULL,
    order_index INTEGER NOT NULL,
    difficulty VARCHAR(20), -- 'easy', 'medium', 'hard'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_questions_quiz ON questions(quiz_id);
CREATE INDEX idx_questions_type ON questions(question_type);
CREATE INDEX idx_questions_order ON questions(quiz_id, order_index);
```

### Quiz Attempts Table (`quiz_attempts`)
Tracks student quiz attempts and results.

```sql
CREATE TABLE quiz_attempts (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    score DECIMAL(5,2),
    attempt_number INTEGER NOT NULL,
    time_taken INTEGER, -- seconds
    status VARCHAR(20) DEFAULT 'in_progress' -- 'in_progress', 'completed', 'abandoned'
);

-- Indexes
CREATE INDEX idx_attempts_quiz ON quiz_attempts(quiz_id);
CREATE INDEX idx_attempts_user ON quiz_attempts(user_id);
CREATE INDEX idx_attempts_status ON quiz_attempts(status);
```

### Question Responses Table (`question_responses`)
Stores student responses to individual questions.

```sql
CREATE TABLE question_responses (
    id SERIAL PRIMARY KEY,
    attempt_id INTEGER REFERENCES quiz_attempts(id) NOT NULL,
    question_id INTEGER REFERENCES questions(id) NOT NULL,
    response JSONB,
    is_correct BOOLEAN,
    points_earned DECIMAL(5,2),
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_responses_attempt ON question_responses(attempt_id);
CREATE INDEX idx_responses_question ON question_responses(question_id);
```

### Coding Questions Table (`coding_questions`)
Specialized table for coding challenge questions.

```sql
CREATE TABLE coding_questions (
    id INTEGER PRIMARY KEY REFERENCES questions(id),
    starter_code TEXT,
    test_cases JSONB NOT NULL, -- Array of input/output pairs
    language VARCHAR(50) NOT NULL,
    time_limit_seconds INTEGER DEFAULT 5,
    memory_limit_mb INTEGER DEFAULT 128
);

-- Indexes
CREATE INDEX idx_coding_questions_language ON coding_questions(language);
```

## Assignment System Tables

### Assignments Table (`assignments`)
Assignment configuration and requirements.

```sql
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER REFERENCES lessons(id),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    instructions TEXT NOT NULL,
    due_date TIMESTAMP,
    points DECIMAL(5,2) DEFAULT 100.0 NOT NULL,
    assignment_type VARCHAR(50) NOT NULL, -- 'project', 'homework', 'lab'
    is_group_work BOOLEAN DEFAULT FALSE,
    max_group_size INTEGER,
    submission_type VARCHAR(50) NOT NULL, -- 'file', 'text', 'link', 'repository'
    allowed_file_types JSONB,
    max_file_size INTEGER, -- bytes
    rubric JSONB,
    is_published BOOLEAN DEFAULT FALSE,
    allow_late_submission BOOLEAN DEFAULT TRUE,
    late_penalty_percentage DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_assignments_lesson ON assignments(lesson_id);
CREATE INDEX idx_assignments_due_date ON assignments(due_date);
CREATE INDEX idx_assignments_type ON assignments(assignment_type);
```

### Assignment Submissions Table (`assignment_submissions`)
Student submissions for assignments.

```sql
CREATE TABLE assignment_submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id) NOT NULL,
    student_id INTEGER REFERENCES users(id) NOT NULL,
    group_id INTEGER REFERENCES assignment_groups(id),
    content TEXT, -- For text submissions
    file_paths JSONB, -- For file submissions
    submission_url VARCHAR(500), -- For link/repository submissions
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_late BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'submitted', -- 'submitted', 'graded', 'returned'
    grade DECIMAL(5,2),
    feedback TEXT,
    rubric_scores JSONB,
    graded_by_id INTEGER REFERENCES users(id),
    graded_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_submissions_assignment ON assignment_submissions(assignment_id);
CREATE INDEX idx_submissions_student ON assignment_submissions(student_id);
CREATE INDEX idx_submissions_status ON assignment_submissions(status);
CREATE INDEX idx_submissions_graded_by ON assignment_submissions(graded_by_id);
```

### Assignment Groups Table (`assignment_groups`)
Groups for collaborative assignments.

```sql
CREATE TABLE assignment_groups (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id) NOT NULL,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_groups_assignment ON assignment_groups(assignment_id);
```

### Group Members Table (`group_members`)
Members of assignment groups.

```sql
CREATE TABLE group_members (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES assignment_groups(id) NOT NULL,
    student_id INTEGER REFERENCES users(id) NOT NULL,
    role VARCHAR(50) DEFAULT 'member', -- 'leader', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, student_id)
);

-- Indexes
CREATE INDEX idx_members_group ON group_members(group_id);
CREATE INDEX idx_members_student ON group_members(student_id);
```

## Communication Tables

### Course Announcements Table (`course_announcements`)
Announcements for courses.

```sql
CREATE TABLE course_announcements (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_announcements_course ON course_announcements(course_id);
CREATE INDEX idx_announcements_created ON course_announcements(created_at);
```

### Submission Comments Table (`submission_comments`)
Comments on assignment submissions.

```sql
CREATE TABLE submission_comments (
    id SERIAL PRIMARY KEY,
    submission_id INTEGER REFERENCES assignment_submissions(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_comments_submission ON submission_comments(submission_id);
CREATE INDEX idx_comments_user ON submission_comments(user_id);
```

## Review and Rating Tables

### Course Reviews Table (`course_reviews`)
Student reviews and ratings for courses.

```sql
CREATE TABLE course_reviews (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses(id) NOT NULL,
    student_id INTEGER REFERENCES users(id) NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, student_id)
);

-- Indexes
CREATE INDEX idx_reviews_course ON course_reviews(course_id);
CREATE INDEX idx_reviews_student ON course_reviews(student_id);
CREATE INDEX idx_reviews_rating ON course_reviews(rating);
```

## Achievement System Tables

### Achievements Table (`achievements`)
Available achievements and badges.

```sql
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    badge_url VARCHAR(255),
    points INTEGER DEFAULT 0 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_achievements_name ON achievements(name);
```

### User Achievements Table (`user_achievements`)
Association table for user achievements.

```sql
CREATE TABLE user_achievements (
    user_id INTEGER REFERENCES users(id),
    achievement_id INTEGER REFERENCES achievements(id),
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id)
);

-- Indexes
CREATE INDEX idx_user_achievements_user ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_achievement ON user_achievements(achievement_id);
```

## Legacy Tables

### Challenges Table (`challenges`)
Programming challenges (legacy support).

```sql
CREATE TABLE challenges (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    points INTEGER NOT NULL,
    test_cases JSONB NOT NULL,
    solution TEXT NOT NULL,
    hints JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_challenges_difficulty ON challenges(difficulty);
CREATE INDEX idx_challenges_active ON challenges(is_active);
```

### Submissions Table (`submissions`)
Code submissions (legacy support).

```sql
CREATE TABLE submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    challenge_id INTEGER REFERENCES challenges(id) NOT NULL,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    score DECIMAL(5,2),
    feedback TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_submissions_user ON submissions(user_id);
CREATE INDEX idx_submissions_challenge ON submissions(challenge_id);
CREATE INDEX idx_submissions_status ON submissions(status);
```

## Analytics Tables

### Quiz Analytics Table (`quiz_analytics`)
Performance analytics for quizzes.

```sql
CREATE TABLE quiz_analytics (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER REFERENCES quizzes(id) NOT NULL,
    total_attempts INTEGER DEFAULT 0,
    average_score DECIMAL(5,2),
    completion_rate DECIMAL(5,2), -- percentage
    average_time_seconds DECIMAL(10,2),
    difficulty_rating DECIMAL(3,2), -- calculated from performance
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_quiz_analytics_quiz ON quiz_analytics(quiz_id);
```

### Assignment Analytics Table (`assignment_analytics`)
Performance analytics for assignments.

```sql
CREATE TABLE assignment_analytics (
    id SERIAL PRIMARY KEY,
    assignment_id INTEGER REFERENCES assignments(id) NOT NULL,
    total_submissions INTEGER DEFAULT 0,
    on_time_submissions INTEGER DEFAULT 0,
    late_submissions INTEGER DEFAULT 0,
    average_grade DECIMAL(5,2),
    median_grade DECIMAL(5,2),
    highest_grade DECIMAL(5,2),
    lowest_grade DECIMAL(5,2),
    completion_rate DECIMAL(5,2), -- percentage
    average_time_to_submit INTEGER, -- hours
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_assignment_analytics_assignment ON assignment_analytics(assignment_id);
```

## Simplified Application Tables

### Notes Table (`notes`)
User notes (from standalone application).

```sql
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    subject VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notes_user ON notes(user_id);
CREATE INDEX idx_notes_subject ON notes(subject);
```

### Flashcard Sets Table (`flashcard_sets`)
Sets of flashcards for studying.

```sql
CREATE TABLE flashcard_sets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    note_id INTEGER REFERENCES notes(id) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    total_cards INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_flashcard_sets_user ON flashcard_sets(user_id);
CREATE INDEX idx_flashcard_sets_note ON flashcard_sets(note_id);
```

### Flashcards Table (`flashcards`)
Individual flashcards within sets.

```sql
CREATE TABLE flashcards (
    id SERIAL PRIMARY KEY,
    flashcard_set_id INTEGER REFERENCES flashcard_sets(id) NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty_level VARCHAR(20) DEFAULT 'medium',
    times_reviewed INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_flashcards_set ON flashcards(flashcard_set_id);
CREATE INDEX idx_flashcards_difficulty ON flashcards(difficulty_level);
```

## Database Relationships

### One-to-Many Relationships
- `users` → `courses` (instructor)
- `users` → `course_enrollments` (student)
- `courses` → `modules`
- `modules` → `lessons`
- `lessons` → `lesson_resources`
- `quizzes` → `questions`
- `quiz_attempts` → `question_responses`
- `assignments` → `assignment_submissions`

### Many-to-Many Relationships
- `users` ↔ `courses` (via `course_enrollments`)
- `users` ↔ `achievements` (via `user_achievements`)
- `students` ↔ `assignment_groups` (via `group_members`)

### Foreign Key Constraints
All foreign key relationships include proper referential integrity constraints with appropriate cascading rules:

- `CASCADE` for dependent data (e.g., deleting a course deletes its modules)
- `SET NULL` for optional references
- `RESTRICT` for critical references that should not be deleted

## Database Migrations

### Migration Files Structure
```
migrations/
├── versions/
│   ├── 001_initial_migration.py
│   ├── 002_add_courses.py
│   ├── 003_add_quizzes.py
│   ├── 004_add_assignments.py
│   ├── 005_add_analytics.py
│   └── ...
├── alembic.ini
├── env.py
└── script.py.mako
```

### Common Migration Commands
```bash
# Create new migration
flask db migrate -m "Add new feature"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade

# Show current revision
flask db current

# Show migration history
flask db history
```

## Performance Considerations

### Indexes
- Primary keys automatically indexed
- Foreign keys indexed for join performance
- Frequently queried columns indexed
- Composite indexes for multi-column queries

### Query Optimization
- Use of `EXPLAIN ANALYZE` for query planning
- Proper use of `SELECT` with specific columns
- Efficient `JOIN` operations
- Pagination for large result sets

### Database Maintenance
- Regular `VACUUM` operations for PostgreSQL
- Index maintenance and rebuilding
- Connection pool management
- Query performance monitoring

## Security Considerations

### Data Protection
- Password hashing with bcrypt
- API key encryption
- Sensitive data handling
- SQL injection prevention

### Access Control
- Row-level security where applicable
- Role-based access control
- Audit logging for sensitive operations
- Data anonymization for analytics

## Backup and Recovery

### Backup Strategy
- Daily full database backups
- Transaction log backups (PostgreSQL)
- Point-in-time recovery capability
- Cross-region backup replication

### Disaster Recovery
- Recovery time objective (RTO): < 1 hour
- Recovery point objective (RPO): < 15 minutes
- Automated failover procedures
- Regular disaster recovery testing

This schema supports a comprehensive educational platform with proper data modeling, performance optimization, and scalability considerations.