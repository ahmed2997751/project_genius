"""
AI Services module for ProjectGenius application.

This module provides AI-powered features using Hugging Face and DeepSeek APIs
for educational content generation, quiz creation, and intelligent feedback.
"""

from .ai_service import AIService
from .content_generator import ContentGenerator
from .quiz_generator import QuizGenerator
from .feedback_analyzer import FeedbackAnalyzer

__all__ = [
    'AIService',
    'ContentGenerator',
    'QuizGenerator',
    'FeedbackAnalyzer'
]
