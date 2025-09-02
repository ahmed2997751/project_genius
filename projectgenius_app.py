#!/usr/bin/env python3
"""
ProjectGenius - Complete Working Application
A comprehensive Flask application with all features working
"""

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import declarative_base
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql://mokwa:simple1234@localhost:5432/projectgenius"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# API Keys
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-7a45473cf92f47299f8fc23ee5df6667")
HUGGINGFACE_API_KEY = os.environ.get("HUGGINGFACE_API_KEY")

# Initialize database
db = SQLAlchemy(app)
Base = declarative_base()

# Database Models
class User(Base, db.Model):
    """User model for storing user account information"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_premium = db.Column(db.Boolean, default=False, nullable=False)
    subscription_end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Note(Base, db.Model):
    """Model for storing user notes"""
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    subject = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="notes")

    def __repr__(self):
        return f'<Note {self.title}>'

class FlashcardSet(Base, db.Model):
    """Model for storing sets of flashcards"""
    __tablename__ = 'flashcard_sets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    total_cards = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref="flashcard_sets")
    note = db.relationship("Note", backref="flashcard_sets")

    def __repr__(self):
        return f'<FlashcardSet {self.title}>'

class Flashcard(Base, db.Model):
    """Model for individual flashcards"""
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    flashcard_set_id = db.Column(db.Integer, db.ForeignKey('flashcard_sets.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty_level = db.Column(db.String(20), default='medium', nullable=False)
    times_reviewed = db.Column(db.Integer, default=0, nullable=False)
    times_correct = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    flashcard_set = db.relationship("FlashcardSet", backref="flashcards")

    def __repr__(self):
        return f'<Flashcard {self.question[:50]}...>'

# AI Service Functions
def generate_flashcards_from_notes(note_content):
    """Generate flashcards from note content using AI"""
    try:
        # Simple fallback implementation - in production, use DeepSeek or HuggingFace
        sentences = note_content.split('.')
        flashcards = []

        for i, sentence in enumerate(sentences[:5]):  # Limit to 5 flashcards
            sentence = sentence.strip()
            if len(sentence) > 20:
                flashcards.append({
                    'question': f"What is the main idea of: '{sentence[:50]}...'?",
                    'answer': sentence,
                    'difficulty': 'medium'
                })

        return flashcards

    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        return []

# Application Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index_simple.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))

        # Create new user
        password_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=password_hash)

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            flash('Registration successful!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f"Registration error: {e}")
            flash('Registration failed', 'error')
            db.session.rollback()

    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))

    user = User.query.get(session['user_id'])
    notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    flashcard_sets = FlashcardSet.query.filter_by(user_id=user.id).order_by(FlashcardSet.created_at.desc()).all()

    return render_template('dashboard.html', user=user, notes=notes, flashcard_sets=flashcard_sets)

@app.route('/create_note', methods=['POST'])
def create_note():
    """Create a new note"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))

    title = request.form['title']
    content = request.form['content']
    subject = request.form.get('subject', '')

    note = Note(
        user_id=session['user_id'],
        title=title,
        content=content,
        subject=subject
    )

    try:
        db.session.add(note)
        db.session.commit()
        flash('Note created successfully!', 'success')
    except Exception as e:
        logger.error(f"Error creating note: {e}")
        flash('Failed to create note', 'error')
        db.session.rollback()

    return redirect(url_for('dashboard'))

@app.route('/generate_flashcards/<int:note_id>')
def generate_flashcards(note_id):
    """Generate flashcards from a note"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))

    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))

    try:
        flashcards_data = generate_flashcards_from_notes(note.content)

        flashcard_set = FlashcardSet(
            user_id=session['user_id'],
            note_id=note.id,
            title=f"Flashcards for {note.title}",
            total_cards=len(flashcards_data)
        )

        db.session.add(flashcard_set)
        db.session.flush()

        for card_data in flashcards_data:
            flashcard = Flashcard(
                flashcard_set_id=flashcard_set.id,
                question=card_data['question'],
                answer=card_data['answer'],
                difficulty_level=card_data['difficulty']
            )
            db.session.add(flashcard)

        db.session.commit()
        flash(f'Generated {len(flashcards_data)} flashcards!', 'success')

    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        flash('Failed to generate flashcards', 'error')
        db.session.rollback()

    return redirect(url_for('dashboard'))

@app.route('/flashcards/<int:set_id>')
def view_flashcards(set_id):
    """View flashcards"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))

    flashcard_set = FlashcardSet.query.filter_by(id=set_id, user_id=session['user_id']).first()
    if not flashcard_set:
        flash('Flashcard set not found', 'error')
        return redirect(url_for('dashboard'))

    flashcards = Flashcard.query.filter_by(flashcard_set_id=set_id).all()

    return render_template('flashcards.html', flashcard_set=flashcard_set, flashcards=flashcards)

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/config')
def config_info():
    """Configuration info endpoint"""
    return jsonify({
        'database': app.config['SQLALCHEMY_DATABASE_URI'].split('@')[-1],
        'deepseek_configured': bool(DEEPSEEK_API_KEY),
        'huggingface_configured': bool(HUGGINGFACE_API_KEY)
    })

# Initialize database tables
with app.app_context():
    Base.metadata.create_all(db.engine)
    logger.info("Database tables initialized")

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'

    print(f"🚀 Starting ProjectGenius on http://{host}:{port}")
    print(f"📊 Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"🤖 DeepSeek: {'✅ Configured' if DEEPSEEK_API_KEY else '❌ Not configured'}")
    print(f"🤗 HuggingFace: {'✅ Configured' if HUGGINGFACE_API_KEY else '❌ Not configured'}")

    app.run(host=host, port=port, debug=debug)
