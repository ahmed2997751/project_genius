# EduSense - AI Tutor for All

## Overview

EduSense is an AI-powered educational platform that transforms student study notes into interactive flashcards using machine learning. The application supports UN Sustainable Development Goal 4 (Quality Education) by making AI-assisted learning accessible to all students. The platform features automated flashcard generation from text notes, interactive flip-card animations, progress tracking, and a premium subscription model with advanced analytics.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology Stack**: HTML5 semantic markup with responsive Bootstrap 5 integration using Replit's dark theme
- **Interactive Components**: Vanilla JavaScript implementation for flashcard flip animations and user interactions without framework dependencies
- **Styling**: CSS3 with custom animations, flexbox layouts, and Bootstrap component integration
- **Template Engine**: Jinja2 for server-side rendering with template inheritance using a base layout

### Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for rapid development and database abstraction
- **Database Layer**: MySQL for production with SQLite fallback for development, using declarative base models
- **Authentication**: Session-based authentication with Werkzeug password hashing and user role management
- **API Structure**: Route-based endpoints handling CRUD operations for notes, flashcards, users, and payments
- **AI Integration**: Hugging Face Transformers API for question-answer generation from user notes

### Data Storage Design
- **User Management**: Users table with premium subscription tracking and relationship mappings
- **Content Storage**: Notes table linked to users with subject categorization and timestamps
- **Flashcard System**: FlashcardSet and Flashcard tables with hierarchical relationships to notes and users
- **Analytics Storage**: UserAnalytics table for tracking study sessions, accuracy rates, and progress metrics
- **Payment Records**: Payment table for transaction tracking and subscription management

### AI Service Architecture
- **Question Generation**: Integration with Hugging Face's DistilBERT model for extracting key concepts from notes
- **Content Processing**: Text cleaning and concept extraction algorithms with fallback to basic flashcard generation
- **API Management**: Structured error handling and rate limiting for external AI service calls

## External Dependencies

### AI and Machine Learning
- **Hugging Face Transformers**: DistilBERT-based question-answering model for automated flashcard generation
- **Hugging Face Inference API**: Cloud-based model hosting for scalable AI processing

### Payment Processing
- **IntaSend**: Payment gateway integration for premium subscription handling with sandbox and production environments
- **Transaction Management**: Secure payment verification and subscription lifecycle management

### Development Tools
- **Bootstrap 5**: UI component library with dark theme customization for consistent styling
- **Font Awesome**: Icon library for visual elements and user interface enhancement
- **Chart.js**: Client-side charting library for analytics dashboard visualization

### Infrastructure Services
- **Flask Ecosystem**: Werkzeug for WSGI utilities, Jinja2 for templating, and SQLAlchemy for database operations
- **Database Connectivity**: MySQL adapter with connection pooling and health check configurations
- **Session Management**: Server-side session storage with secure secret key handling