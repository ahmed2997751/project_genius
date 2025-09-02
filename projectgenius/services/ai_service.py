import os
import logging
import requests
from typing import List, Dict
import re

# Hugging Face API configuration
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY", "hf_placeholder_key")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/distilbert-base-cased-distilled-squad"

def generate_flashcards_from_notes(note_content: str) -> List[Dict[str, str]]:
    """
    Generate flashcards from note content using Hugging Face Question Answering API
    
    Args:
        note_content (str): The content of the note to generate flashcards from
        
    Returns:
        List[Dict[str, str]]: List of flashcards with questions and answers
    """
    try:
        # Clean and prepare the note content
        cleaned_content = clean_note_content(note_content)
        
        if len(cleaned_content.strip()) < 50:
            logging.warning("Note content too short for flashcard generation")
            return []
        
        # Extract key concepts and facts from the content
        key_concepts = extract_key_concepts(cleaned_content)
        
        if not key_concepts:
            logging.warning("No key concepts found in note content")
            return []
        
        # Generate questions and answers for each concept
        flashcards = []
        for concept in key_concepts[:10]:  # Limit to 10 flashcards to avoid API limits
            try:
                flashcard = generate_qa_pair(concept, cleaned_content)
                if flashcard:
                    flashcards.append(flashcard)
            except Exception as e:
                logging.error(f"Error generating flashcard for concept '{concept}': {e}")
                continue
        
        # If Hugging Face API fails, generate basic flashcards from content
        if not flashcards:
            flashcards = generate_basic_flashcards(cleaned_content)
        
        return flashcards
        
    except Exception as e:
        logging.error(f"Error in generate_flashcards_from_notes: {e}")
        # Return basic flashcards as fallback
        return generate_basic_flashcards(note_content)

def clean_note_content(content: str) -> str:
    """Clean and normalize note content"""
    # Remove extra whitespace and normalize line breaks
    content = re.sub(r'\s+', ' ', content)
    content = content.strip()
    
    # Remove very short lines (likely formatting artifacts)
    lines = content.split('.')
    meaningful_lines = [line.strip() for line in lines if len(line.strip()) > 10]
    
    return '. '.join(meaningful_lines)

def extract_key_concepts(content: str) -> List[str]:
    """
    Extract key concepts from the note content
    
    This function identifies important terms, definitions, and concepts
    that would make good flashcard material.
    """
    # Split content into sentences
    sentences = re.split(r'[.!?]+', content)
    
    key_concepts = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Skip very short sentences
            continue
            
        # Look for definition patterns
        if any(pattern in sentence.lower() for pattern in ['is defined as', 'refers to', 'means', 'is the', 'are the']):
            key_concepts.append(sentence)
        
        # Look for important factual statements
        elif any(pattern in sentence.lower() for pattern in ['important', 'key', 'main', 'primary', 'essential']):
            key_concepts.append(sentence)
        
        # Look for numbered or bulleted points
        elif re.match(r'^\d+[\.\)]\s*', sentence) or sentence.startswith('- '):
            key_concepts.append(sentence)
    
    # If no specific patterns found, use the first few meaningful sentences
    if not key_concepts:
        key_concepts = [s.strip() for s in sentences[:5] if len(s.strip()) > 20]
    
    return key_concepts[:15]  # Limit to prevent too many API calls

def generate_qa_pair(concept: str, context: str) -> Dict[str, str]:
    """
    Generate a question-answer pair using Hugging Face QA API
    
    Args:
        concept (str): The concept or sentence to create a question about
        context (str): The full note content as context
        
    Returns:
        Dict[str, str]: Dictionary with question, answer, and difficulty
    """
    try:
        # Create a question from the concept
        question = create_question_from_concept(concept)
        
        if not question:
            return None
        
        # Use Hugging Face API to find the answer
        headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
        payload = {
            "inputs": {
                "question": question,
                "context": context
            }
        }
        
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', '').strip()
            confidence = result.get('score', 0)
            
            if answer and confidence > 0.1:  # Only use answers with reasonable confidence
                difficulty = determine_difficulty(question, answer)
                return {
                    'question': question,
                    'answer': answer,
                    'difficulty': difficulty
                }
        else:
            logging.warning(f"Hugging Face API error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error to Hugging Face API: {e}")
    except Exception as e:
        logging.error(f"Error in generate_qa_pair: {e}")
    
    # Fallback: create a simple Q&A from the concept
    return create_basic_qa_from_concept(concept)

def create_question_from_concept(concept: str) -> str:
    """Create a question from a concept or statement"""
    concept = concept.strip()
    
    # Question templates based on common patterns
    if 'is defined as' in concept.lower() or 'refers to' in concept.lower():
        # Extract the term being defined
        parts = re.split(r'\s+(?:is defined as|refers to|means)\s+', concept, flags=re.IGNORECASE)
        if len(parts) >= 2:
            term = parts[0].strip()
            return f"What is {term}?"
    
    elif 'because' in concept.lower():
        return f"Why {concept.split('because')[0].strip().lower()}?"
    
    elif any(word in concept.lower() for word in ['when', 'where', 'how', 'why']):
        return f"Explain: {concept}"
    
    else:
        # Create a general question
        if len(concept) > 100:
            return f"What is important to know about {concept[:50]}...?"
        else:
            return f"What do you know about: {concept}?"
    
    return None

def create_basic_qa_from_concept(concept: str) -> Dict[str, str]:
    """Create a basic question-answer pair when AI API fails"""
    concept = concept.strip()
    
    # Simple patterns for basic Q&A generation
    if 'is' in concept and len(concept.split()) > 3:
        parts = concept.split(' is ', 1)
        if len(parts) == 2:
            return {
                'question': f"What is {parts[0].strip()}?",
                'answer': parts[1].strip(),
                'difficulty': 'medium'
            }
    
    # Default pattern
    words = concept.split()
    if len(words) > 10:
        question = f"What do you know about {' '.join(words[:5])}?"
        answer = concept
    else:
        question = f"Explain: {concept}"
        answer = concept
    
    return {
        'question': question,
        'answer': answer,
        'difficulty': 'medium'
    }

def determine_difficulty(question: str, answer: str) -> str:
    """Determine the difficulty level of a flashcard"""
    # Simple heuristics for difficulty
    question_words = len(question.split())
    answer_words = len(answer.split())
    
    if question_words <= 5 and answer_words <= 10:
        return 'easy'
    elif question_words <= 10 and answer_words <= 25:
        return 'medium'
    else:
        return 'hard'

def generate_basic_flashcards(content: str) -> List[Dict[str, str]]:
    """
    Generate basic flashcards when AI API is unavailable
    This serves as a fallback mechanism
    """
    flashcards = []
    
    # Split content into sentences and create simple Q&A pairs
    sentences = re.split(r'[.!?]+', content)
    meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    
    for i, sentence in enumerate(meaningful_sentences[:8]):  # Limit to 8 cards
        if not sentence:
            continue
            
        # Create different types of questions
        if i % 3 == 0:
            question = f"What is the main point of: '{sentence[:30]}...'?"
        elif i % 3 == 1:
            question = f"Explain the concept mentioned in: '{sentence[:30]}...'?"
        else:
            question = f"What do you remember about: '{sentence[:30]}...'?"
        
        flashcards.append({
            'question': question,
            'answer': sentence,
            'difficulty': 'medium'
        })
    
    # Add some general questions about the content
    if len(content) > 100:
        flashcards.append({
            'question': "What are the main topics covered in this note?",
            'answer': "Review the key concepts and important points from your notes.",
            'difficulty': 'easy'
        })
    
    return flashcards
