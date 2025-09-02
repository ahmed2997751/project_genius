#!/usr/bin/env python3
'''
WSGI file for ProjectGenius production deployment
Use with: gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
'''

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the application
from projectgenius import create_app

# Create the application
app = create_app()

if __name__ == "__main__":
    app.run()
