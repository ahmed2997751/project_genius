#!/usr/bin/env python3
'''
ProjectGenius Production Server
'''

import os
import sys
from pathlib import Path

# Ensure we're in the right directory
project_root = Path(__file__).parent
os.chdir(project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the application
from projectgenius import create_app

def main():
    print("🚀 Starting ProjectGenius Production Server")
    print("=" * 50)

    # Create the app
    app = create_app()

    # Production settings
    app.config.update(
        DEBUG=False,
        TESTING=False,
        ENV='production'
    )

    # Get host and port from environment or use defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 8000))

    print(f"🌐 Server: http://{host}:{port}")
    print(f"🗄️  Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print(f"📧 Email: {app.config.get('MAIL_USERNAME', 'Not configured')}")
    print("=" * 50)

    try:
        # For production, you should use a proper WSGI server like Gunicorn
        # gunicorn -w 4 -b 0.0.0.0:8000 run_production:app
        app.run(
            host=host,
            port=port,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
