"""
Test package for ProjectGenius application.

This package contains all unit tests, integration tests, and fixtures
for testing the ProjectGenius education platform.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path for testing
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Test configuration constants
TEST_DATABASE_URL = 'sqlite:///:memory:'
TEST_SECRET_KEY = 'test-secret-key-for-testing-only'

# Common test utilities
def get_test_data_path():
    """Get the path to test data directory."""
    return Path(__file__).parent / 'data'

def get_test_uploads_path():
    """Get the path to test uploads directory."""
    return Path(__file__).parent / 'uploads'
