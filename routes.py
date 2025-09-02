from flask import render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import User, Note, FlashcardSet, Flashcard, UserAnalytics, Payment
from ai_service import generate_flashcards_from_notes
from projectgenius.services.payment_service import create_payment, verify_payment
from datetime import datetime, timedelta
import logging

@app.route('/')
def index():
    """Homepage with note input and flashcard generation"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
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
            logging.error(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
            db.session.rollback()
    
    return render_template('index.html')

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
        flash('Invalid username or password', 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """User logout"""
    session.pop('user_id', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard showing notes and flashcard sets"""
    if 'user_id' not in session:
        flash('Please log in to access dashboard', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    # Get user's notes and flashcard sets
    notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    flashcard_sets = FlashcardSet.query.filter_by(user_id=user.id).order_by(FlashcardSet.created_at.desc()).all()
    
    return render_template('dashboard.html', user=user, notes=notes, flashcard_sets=flashcard_sets)

@app.route('/create_note', methods=['POST'])
def create_note():
    """Create a new note"""
    if 'user_id' not in session:
        flash('Please log in to create notes', 'error')
        return redirect(url_for('index'))
    
    title = request.form['title']
    content = request.form['content']
    subject = request.form.get('subject', '')
    
    if not title or not content:
        flash('Title and content are required', 'error')
        return redirect(url_for('dashboard'))
    
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
        logging.error(f"Error creating note: {e}")
        flash('Failed to create note. Please try again.', 'error')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))

@app.route('/generate_flashcards/<int:note_id>')
def generate_flashcards(note_id):
    """Generate flashcards from a note using AI"""
    if 'user_id' not in session:
        flash('Please log in to generate flashcards', 'error')
        return redirect(url_for('index'))
    
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        # Generate flashcards using AI service
        flashcards_data = generate_flashcards_from_notes(note.content)
        
        if not flashcards_data:
            flash('Failed to generate flashcards. Please try again.', 'error')
            return redirect(url_for('dashboard'))
        
        # Create flashcard set
        flashcard_set = FlashcardSet(
            user_id=session['user_id'],
            note_id=note.id,
            title=f"Flashcards for {note.title}",
            description=f"Generated from note: {note.title}",
            total_cards=len(flashcards_data)
        )
        
        db.session.add(flashcard_set)
        db.session.flush()  # Get the ID
        
        # Create individual flashcards
        for card_data in flashcards_data:
            flashcard = Flashcard(
                flashcard_set_id=flashcard_set.id,
                question=card_data['question'],
                answer=card_data['answer'],
                difficulty_level=card_data.get('difficulty', 'medium')
            )
            db.session.add(flashcard)
        
        db.session.commit()
        flash(f'Successfully generated {len(flashcards_data)} flashcards!', 'success')
        return redirect(url_for('view_flashcards', set_id=flashcard_set.id))
        
    except Exception as e:
        logging.error(f"Error generating flashcards: {e}")
        flash('Failed to generate flashcards. Please check your note content and try again.', 'error')
        db.session.rollback()
        return redirect(url_for('dashboard'))

@app.route('/flashcards/<int:set_id>')
def view_flashcards(set_id):
    """View and study flashcards"""
    if 'user_id' not in session:
        flash('Please log in to view flashcards', 'error')
        return redirect(url_for('index'))
    
    flashcard_set = FlashcardSet.query.filter_by(id=set_id, user_id=session['user_id']).first()
    if not flashcard_set:
        flash('Flashcard set not found', 'error')
        return redirect(url_for('dashboard'))
    
    flashcards = Flashcard.query.filter_by(flashcard_set_id=set_id).all()
    
    return render_template('flashcards.html', flashcard_set=flashcard_set, flashcards=flashcards)

@app.route('/update_flashcard_stats', methods=['POST'])
def update_flashcard_stats():
    """Update flashcard statistics when user answers"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.get_json()
    flashcard_id = data.get('flashcard_id')
    is_correct = data.get('is_correct', False)
    
    flashcard = Flashcard.query.get(flashcard_id)
    if not flashcard:
        return jsonify({'error': 'Flashcard not found'}), 404
    
    # Update flashcard statistics
    flashcard.times_reviewed += 1
    if is_correct:
        flashcard.times_correct += 1
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        logging.error(f"Error updating flashcard stats: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update statistics'}), 500

@app.route('/analytics')
def analytics():
    """Analytics dashboard for premium users"""
    if 'user_id' not in session:
        flash('Please log in to view analytics', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    if not user.is_premium:
        flash('Analytics is available for premium users only', 'info')
        return redirect(url_for('subscription'))
    
    # Get analytics data
    analytics_data = UserAnalytics.query.filter_by(user_id=user.id).order_by(UserAnalytics.study_session_date.desc()).all()
    
    # Calculate summary statistics
    total_cards_studied = sum(a.cards_studied for a in analytics_data)
    total_correct = sum(a.correct_answers for a in analytics_data)
    total_study_time = sum(a.total_study_time for a in analytics_data)
    accuracy = (total_correct / total_cards_studied * 100) if total_cards_studied > 0 else 0
    
    stats = {
        'total_cards_studied': total_cards_studied,
        'total_correct': total_correct,
        'total_study_time': total_study_time,
        'accuracy': round(accuracy, 1)
    }
    
    return render_template('analytics.html', user=user, analytics_data=analytics_data, stats=stats)

@app.route('/subscription')
def subscription():
    """Subscription management page"""
    if 'user_id' not in session:
        flash('Please log in to manage subscription', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('subscription.html', user=user)

@app.route('/create_payment', methods=['POST'])
def create_payment_route():
    """Create a payment for premium subscription"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    plan = request.form.get('plan', 'monthly')
    amount = 9.99 if plan == 'monthly' else 99.99  # Monthly or yearly
    months = 1 if plan == 'monthly' else 12
    
    try:
        payment_data = create_payment(session['user_id'], amount, months)
        return jsonify(payment_data)
    except Exception as e:
        logging.error(f"Payment creation error: {e}")
        return jsonify({'error': 'Failed to create payment'}), 500

@app.route('/verify_payment/<transaction_id>')
def verify_payment_route(transaction_id):
    """Verify payment and activate premium subscription"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))
    
    try:
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
        if not payment:
            flash('Payment not found', 'error')
            return redirect(url_for('subscription'))
        
        if verify_payment(transaction_id):
            # Activate premium subscription
            user = User.query.get(session['user_id'])
            user.is_premium = True
            user.subscription_end_date = datetime.utcnow() + timedelta(days=30 * payment.subscription_months)
            
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            
            db.session.commit()
            flash('Premium subscription activated!', 'success')
            return redirect(url_for('analytics'))
        else:
            flash('Payment verification failed', 'error')
            return redirect(url_for('subscription'))
            
    except Exception as e:
        logging.error(f"Payment verification error: {e}")
        flash('Payment verification failed', 'error')
        db.session.rollback()
        return redirect(url_for('subscription'))

@app.route('/delete_note/<int:note_id>')
def delete_note(note_id):
    """Delete a note and its associated flashcards"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))
    
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first()
    if not note:
        flash('Note not found', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully', 'success')
    except Exception as e:
        logging.error(f"Error deleting note: {e}")
        flash('Failed to delete note', 'error')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))

@app.route('/delete_flashcard_set/<int:set_id>')
def delete_flashcard_set(set_id):
    """Delete a flashcard set"""
    if 'user_id' not in session:
        flash('Please log in', 'error')
        return redirect(url_for('index'))
    
    flashcard_set = FlashcardSet.query.filter_by(id=set_id, user_id=session['user_id']).first()
    if not flashcard_set:
        flash('Flashcard set not found', 'error')
        return redirect(url_for('dashboard'))
    
    try:
        db.session.delete(flashcard_set)
        db.session.commit()
        flash('Flashcard set deleted successfully', 'success')
    except Exception as e:
        logging.error(f"Error deleting flashcard set: {e}")
        flash('Failed to delete flashcard set', 'error')
        db.session.rollback()
    
    return redirect(url_for('dashboard'))


@app.route('/courses')
def browse_courses():
    """Browse available courses"""
    # Later you can fetch courses from DB, API, or static list
    courses = [
        {"id": 1, "title": "Intro to Python", "description": "Learn Python basics."},
        {"id": 2, "title": "Flask Web Development", "description": "Build apps with Flask."},
        {"id": 3, "title": "Machine Learning", "description": "An introduction to ML concepts."}
    ]
    return render_template('browse.html', courses=courses)
