/**
 * EduSense Flashcard Study Session
 * Interactive flashcard functionality with flip animations and progress tracking
 */

class FlashcardSession {
    constructor(flashcards, totalCards) {
        this.flashcards = flashcards;
        this.totalCards = totalCards;
        this.currentCardIndex = 0;
        this.cardsStudied = 0;
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        this.sessionStartTime = Date.now();
        this.studyTime = 0;
        this.timerInterval = null;
        this.isFlipped = false;
        this.hasAnswered = false;
        
        this.initializeSession();
    }
    
    /**
     * Initialize the study session
     */
    initializeSession() {
        this.startTimer();
        this.updateProgress();
        this.updateStats();
        this.showCurrentCard();
        
        // Add keyboard event listeners
        document.addEventListener('keydown', this.handleKeypress.bind(this));
        
        console.log('Flashcard session initialized with', this.totalCards, 'cards');
    }
    
    /**
     * Start the study timer
     */
    startTimer() {
        this.timerInterval = setInterval(() => {
            this.studyTime = Math.floor((Date.now() - this.sessionStartTime) / 1000);
            this.updateTimer();
        }, 1000);
    }
    
    /**
     * Stop the study timer
     */
    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }
    
    /**
     * Update timer display
     */
    updateTimer() {
        const minutes = Math.floor(this.studyTime / 60);
        const seconds = this.studyTime % 60;
        const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        const timerElement = document.getElementById('studyTimer');
        if (timerElement) {
            timerElement.textContent = `Study Time: ${timeString}`;
        }
    }
    
    /**
     * Show current flashcard
     */
    showCurrentCard() {
        // Hide all cards
        for (let i = 1; i <= this.totalCards; i++) {
            const card = document.getElementById(`flashcard${i}`);
            if (card) {
                card.style.display = 'none';
                card.classList.remove('flipped');
            }
        }
        
        // Show current card
        const currentCard = document.getElementById(`flashcard${this.currentCardIndex + 1}`);
        if (currentCard) {
            currentCard.style.display = 'block';
            this.isFlipped = false;
            this.hasAnswered = false;
            
            // Add entrance animation
            currentCard.style.opacity = '0';
            currentCard.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                currentCard.style.transition = 'all 0.3s ease';
                currentCard.style.opacity = '1';
                currentCard.style.transform = 'translateY(0)';
            }, 50);
        }
        
        this.updateProgress();
        this.updateNavigationButtons();
    }
    
    /**
     * Flip current flashcard
     * @param {number} cardNumber - Card number to flip
     */
    flipCard(cardNumber) {
        const card = document.getElementById(`flashcard${cardNumber}`);
        if (!card) return;
        
        // Only allow flipping if it's the current card
        if (cardNumber !== this.currentCardIndex + 1) return;
        
        card.classList.toggle('flipped');
        this.isFlipped = !this.isFlipped;
        
        // Play flip sound effect (if available)
        this.playFlipSound();
        
        // Update feedback section visibility
        this.updateFeedbackVisibility();
    }
    
    /**
     * Play flip sound effect
     */
    playFlipSound() {
        // Create a subtle audio feedback
        if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
            try {
                const audioContext = new (AudioContext || webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
                oscillator.frequency.exponentialRampToValueAtTime(200, audioContext.currentTime + 0.1);
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.1);
            } catch (error) {
                // Audio not supported, silently continue
            }
        }
    }
    
    /**
     * Update feedback section visibility
     */
    updateFeedbackVisibility() {
        const feedbackSection = document.getElementById('feedbackSection');
        if (feedbackSection) {
            feedbackSection.style.display = this.isFlipped ? 'block' : 'none';
        }
    }
    
    /**
     * Mark answer as correct or incorrect
     * @param {boolean} isCorrect - Whether answer was correct
     */
    markAnswer(isCorrect) {
        if (this.hasAnswered) return;
        
        this.hasAnswered = true;
        
        if (isCorrect) {
            this.correctAnswers++;
        } else {
            this.incorrectAnswers++;
        }
        
        this.cardsStudied++;
        
        // Update flashcard statistics via API
        this.updateFlashcardStats(isCorrect);
        
        this.updateStats();
        
        // Auto-advance after a short delay
        setTimeout(() => {
            this.nextCard();
        }, 1500);
        
        // Provide visual feedback
        this.showAnswerFeedback(isCorrect);
    }
    
    /**
     * Show visual feedback for answer
     * @param {boolean} isCorrect - Whether answer was correct
     */
    showAnswerFeedback(isCorrect) {
        const currentCard = document.getElementById(`flashcard${this.currentCardIndex + 1}`);
        if (!currentCard) return;
        
        // Add feedback class
        const feedbackClass = isCorrect ? 'answer-correct' : 'answer-incorrect';
        currentCard.classList.add(feedbackClass);
        
        // Remove feedback class after animation
        setTimeout(() => {
            currentCard.classList.remove(feedbackClass);
        }, 1500);
        
        // Show notification
        const message = isCorrect ? 'Correct! Great job!' : 'Incorrect. Review this concept.';
        const type = isCorrect ? 'success' : 'warning';
        
        if (window.EduSense && window.EduSense.showNotification) {
            window.EduSense.showNotification(message, type, 1500);
        }
    }
    
    /**
     * Update flashcard statistics via API
     * @param {boolean} isCorrect - Whether answer was correct
     */
    async updateFlashcardStats(isCorrect) {
        const flashcardId = this.flashcards[this.currentCardIndex].id;
        
        try {
            const response = await fetch('/update_flashcard_stats', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flashcard_id: flashcardId,
                    is_correct: isCorrect
                })
            });
            
            if (!response.ok) {
                console.warn('Failed to update flashcard statistics');
            }
        } catch (error) {
            console.error('Error updating flashcard statistics:', error);
        }
    }
    
    /**
     * Go to next card
     */
    nextCard() {
        if (this.currentCardIndex < this.totalCards - 1) {
            this.currentCardIndex++;
            this.showCurrentCard();
        } else {
            this.completeSession();
        }
    }
    
    /**
     * Go to previous card
     */
    previousCard() {
        if (this.currentCardIndex > 0) {
            this.currentCardIndex--;
            this.showCurrentCard();
        }
    }
    
    /**
     * Update progress display
     */
    updateProgress() {
        const currentCardElement = document.getElementById('currentCard');
        const progressFill = document.getElementById('progressFill');
        
        if (currentCardElement) {
            currentCardElement.textContent = this.currentCardIndex + 1;
        }
        
        if (progressFill) {
            const progress = ((this.currentCardIndex + 1) / this.totalCards) * 100;
            progressFill.style.width = `${progress}%`;
        }
    }
    
    /**
     * Update study statistics display
     */
    updateStats() {
        const elements = {
            cardsStudied: document.getElementById('cardsStudied'),
            correctAnswers: document.getElementById('correctAnswers'),
            incorrectAnswers: document.getElementById('incorrectAnswers'),
            accuracyRate: document.getElementById('accuracyRate')
        };
        
        if (elements.cardsStudied) {
            elements.cardsStudied.textContent = this.cardsStudied;
        }
        
        if (elements.correctAnswers) {
            elements.correctAnswers.textContent = this.correctAnswers;
        }
        
        if (elements.incorrectAnswers) {
            elements.incorrectAnswers.textContent = this.incorrectAnswers;
        }
        
        if (elements.accuracyRate) {
            const accuracy = this.cardsStudied > 0 ? 
                Math.round((this.correctAnswers / this.cardsStudied) * 100) : 0;
            elements.accuracyRate.textContent = `${accuracy}%`;
        }
    }
    
    /**
     * Update navigation buttons
     */
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        
        if (prevBtn) {
            prevBtn.disabled = this.currentCardIndex === 0;
        }
        
        if (nextBtn) {
            if (this.currentCardIndex === this.totalCards - 1) {
                nextBtn.textContent = 'Finish';
                nextBtn.innerHTML = '<i class="fas fa-flag-checkered me-1"></i>Finish';
            } else {
                nextBtn.innerHTML = 'Next <i class="fas fa-chevron-right"></i>';
            }
        }
    }
    
    /**
     * Handle keyboard events
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeypress(event) {
        switch (event.key) {
            case ' ':
            case 'Enter':
                event.preventDefault();
                this.flipCard(this.currentCardIndex + 1);
                break;
            case 'ArrowLeft':
                event.preventDefault();
                this.previousCard();
                break;
            case 'ArrowRight':
                event.preventDefault();
                if (this.hasAnswered || !this.isFlipped) {
                    this.nextCard();
                }
                break;
            case '1':
                event.preventDefault();
                if (this.isFlipped && !this.hasAnswered) {
                    this.markAnswer(false);
                }
                break;
            case '2':
                event.preventDefault();
                if (this.isFlipped && !this.hasAnswered) {
                    this.markAnswer(true);
                }
                break;
        }
    }
    
    /**
     * Complete study session
     */
    completeSession() {
        this.stopTimer();
        
        // Update final statistics
        const finalCorrect = document.getElementById('finalCorrect');
        const finalAccuracy = document.getElementById('finalAccuracy');
        const finalStudyTime = document.getElementById('finalStudyTime');
        
        if (finalCorrect) {
            finalCorrect.textContent = this.correctAnswers;
        }
        
        if (finalAccuracy) {
            const accuracy = this.cardsStudied > 0 ? 
                Math.round((this.correctAnswers / this.cardsStudied) * 100) : 0;
            finalAccuracy.textContent = `${accuracy}%`;
        }
        
        if (finalStudyTime) {
            const minutes = Math.floor(this.studyTime / 60);
            const seconds = this.studyTime % 60;
            finalStudyTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }
        
        // Save session data to local storage
        this.saveSessionData();
        
        // Show completion modal
        const completionModal = new bootstrap.Modal(document.getElementById('completionModal'));
        completionModal.show();
        
        // Track completion
        if (window.EduSense && window.EduSense.Utils) {
            console.log('Study session completed:', {
                totalCards: this.totalCards,
                correctAnswers: this.correctAnswers,
                accuracy: Math.round((this.correctAnswers / this.cardsStudied) * 100),
                studyTime: this.studyTime
            });
        }
    }
    
    /**
     * Save session data to local storage
     */
    saveSessionData() {
        const sessionData = {
            timestamp: Date.now(),
            totalCards: this.totalCards,
            cardsStudied: this.cardsStudied,
            correctAnswers: this.correctAnswers,
            incorrectAnswers: this.incorrectAnswers,
            studyTime: this.studyTime,
            accuracy: Math.round((this.correctAnswers / this.cardsStudied) * 100)
        };
        
        if (window.EduSense && window.EduSense.StorageManager) {
            const sessions = window.EduSense.StorageManager.get('study_sessions', []);
            sessions.push(sessionData);
            
            // Keep only last 10 sessions
            if (sessions.length > 10) {
                sessions.splice(0, sessions.length - 10);
            }
            
            window.EduSense.StorageManager.set('study_sessions', sessions);
        }
    }
    
    /**
     * Restart study session
     */
    restart() {
        this.currentCardIndex = 0;
        this.cardsStudied = 0;
        this.correctAnswers = 0;
        this.incorrectAnswers = 0;
        this.sessionStartTime = Date.now();
        this.studyTime = 0;
        this.isFlipped = false;
        this.hasAnswered = false;
        
        this.startTimer();
        this.updateProgress();
        this.updateStats();
        this.showCurrentCard();
        
        // Hide completion modal if open
        const completionModal = bootstrap.Modal.getInstance(document.getElementById('completionModal'));
        if (completionModal) {
            completionModal.hide();
        }
    }
}

// Global functions for template integration
let currentSession = null;

/**
 * Initialize study session
 * @param {Array} flashcards - Array of flashcard objects
 * @param {number} totalCards - Total number of cards
 */
function initializeStudySession(flashcards, totalCards) {
    currentSession = new FlashcardSession(flashcards, totalCards);
}

/**
 * Flip card wrapper function
 * @param {number} cardNumber - Card number to flip
 */
function flipCard(cardNumber) {
    if (currentSession) {
        currentSession.flipCard(cardNumber);
    }
}

/**
 * Mark answer wrapper function
 * @param {boolean} isCorrect - Whether answer was correct
 */
function markAnswer(isCorrect) {
    if (currentSession) {
        currentSession.markAnswer(isCorrect);
    }
}

/**
 * Next card wrapper function
 */
function nextCard() {
    if (currentSession) {
        currentSession.nextCard();
    }
}

/**
 * Previous card wrapper function
 */
function previousCard() {
    if (currentSession) {
        currentSession.previousCard();
    }
}

/**
 * Restart study wrapper function
 */
function restartStudy() {
    if (currentSession) {
        currentSession.restart();
    }
}

// Add CSS for answer feedback animations
const style = document.createElement('style');
style.textContent = `
    .answer-correct {
        animation: correctPulse 1.5s ease-in-out;
    }
    
    .answer-incorrect {
        animation: incorrectShake 1.5s ease-in-out;
    }
    
    @keyframes correctPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); box-shadow: 0 0 30px rgba(40, 167, 69, 0.5); }
    }
    
    @keyframes incorrectShake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlashcardSession;
}
