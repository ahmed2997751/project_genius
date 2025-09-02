-- EduSense Database Schema
-- This file contains the database schema and sample data for the EduSense AI Tutor application

-- Create the database (if using MySQL)
-- CREATE DATABASE IF NOT EXISTS edusense;
-- USE edusense;

-- Users table for storing user account information
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    is_premium BOOLEAN DEFAULT FALSE NOT NULL,
    subscription_end_date DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Notes table for storing user notes that will be converted to flashcards
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    subject VARCHAR(100) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Flashcard sets table for organizing flashcards
CREATE TABLE IF NOT EXISTS flashcard_sets (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    note_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    total_cards INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
);

-- Individual flashcards with questions and answers
CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    flashcard_set_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    difficulty_level VARCHAR(20) DEFAULT 'medium' NOT NULL,
    times_reviewed INTEGER DEFAULT 0 NOT NULL,
    times_correct INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (flashcard_set_id) REFERENCES flashcard_sets(id) ON DELETE CASCADE
);

-- User analytics for tracking study progress
CREATE TABLE IF NOT EXISTS user_analytics (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    study_session_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    cards_studied INTEGER DEFAULT 0 NOT NULL,
    correct_answers INTEGER DEFAULT 0 NOT NULL,
    total_study_time INTEGER DEFAULT 0 NOT NULL, -- in minutes
    subject VARCHAR(100) NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Payment transactions table
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD' NOT NULL,
    status VARCHAR(20) NOT NULL, -- pending, completed, failed, refunded
    payment_method VARCHAR(50) NOT NULL,
    subscription_months INTEGER DEFAULT 1 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_created_at ON notes(created_at);
CREATE INDEX idx_flashcard_sets_user_id ON flashcard_sets(user_id);
CREATE INDEX idx_flashcard_sets_note_id ON flashcard_sets(note_id);
CREATE INDEX idx_flashcards_set_id ON flashcards(flashcard_set_id);
CREATE INDEX idx_analytics_user_id ON user_analytics(user_id);
CREATE INDEX idx_analytics_date ON user_analytics(study_session_date);
CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);

-- Sample data for demonstration (optional - remove in production)
-- Insert sample users
INSERT INTO users (username, email, password_hash, is_premium, created_at) VALUES
('demo_student', 'demo@edusense.com', 'pbkdf2:sha256:260000$mock$hash', FALSE, NOW()),
('premium_user', 'premium@edusense.com', 'pbkdf2:sha256:260000$mock$hash', TRUE, NOW());

-- Insert sample notes
INSERT INTO notes (user_id, title, content, subject, created_at) VALUES
(1, 'Introduction to Machine Learning', 
'Machine learning is a subset of artificial intelligence that focuses on creating systems that can learn and improve from experience without being explicitly programmed. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning. Supervised learning uses labeled data to train models. Unsupervised learning finds patterns in data without labels. Reinforcement learning learns through trial and error with rewards and penalties.',
'Computer Science', NOW()),
(1, 'Cell Biology Basics',
'Cells are the basic unit of life. All living organisms are composed of one or more cells. There are two main types of cells: prokaryotic cells and eukaryotic cells. Prokaryotic cells do not have a nucleus and their genetic material is freely floating in the cytoplasm. Eukaryotic cells have a nucleus that contains their genetic material. The cell membrane controls what enters and exits the cell.',
'Biology', NOW());

-- Insert sample flashcard sets
INSERT INTO flashcard_sets (user_id, note_id, title, description, total_cards, created_at) VALUES
(1, 1, 'Machine Learning Fundamentals', 'Basic concepts in machine learning', 3, NOW()),
(1, 2, 'Cell Biology Quiz', 'Questions about cell structure and types', 3, NOW());

-- Insert sample flashcards
INSERT INTO flashcards (flashcard_set_id, question, answer, difficulty_level, created_at) VALUES
(1, 'What is machine learning?', 'Machine learning is a subset of artificial intelligence that focuses on creating systems that can learn and improve from experience without being explicitly programmed.', 'easy', NOW()),
(1, 'What are the three main types of machine learning?', 'The three main types are supervised learning, unsupervised learning, and reinforcement learning.', 'medium', NOW()),
(1, 'How does reinforcement learning work?', 'Reinforcement learning learns through trial and error with rewards and penalties.', 'hard', NOW()),
(2, 'What are cells?', 'Cells are the basic unit of life. All living organisms are composed of one or more cells.', 'easy', NOW()),
(2, 'What are the two main types of cells?', 'The two main types are prokaryotic cells and eukaryotic cells.', 'medium', NOW()),
(2, 'What is the difference between prokaryotic and eukaryotic cells?', 'Prokaryotic cells do not have a nucleus and their genetic material is freely floating in the cytoplasm. Eukaryotic cells have a nucleus that contains their genetic material.', 'hard', NOW());

-- Insert sample analytics data
INSERT INTO user_analytics (user_id, study_session_date, cards_studied, correct_answers, total_study_time, subject) VALUES
(1, DATE_SUB(NOW(), INTERVAL 1 DAY), 6, 4, 15, 'Computer Science'),
(1, DATE_SUB(NOW(), INTERVAL 2 DAY), 3, 3, 10, 'Biology'),
(1, DATE_SUB(NOW(), INTERVAL 3 DAY), 4, 2, 12, 'Computer Science');

-- Insert sample payment record
INSERT INTO payments (user_id, transaction_id, amount, currency, status, payment_method, subscription_months, created_at) VALUES
(2, 'edu_2_sample123', 9.99, 'USD', 'completed', 'card', 1, NOW());
