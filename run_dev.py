#!/usr/bin/env python3
"""
Development server startup script for ProjectGenius.

This script provides an easy way to start the development server with
proper configuration and helpful debugging information.
"""

import os
import sys
from pathlib import Path
import subprocess
import argparse

def check_requirements():
    """Check if required dependencies are installed."""
    try:
        import flask # type: ignore
        import sqlalchemy # type: ignore
        import bcrypt # type: ignore
        print("✓ Core dependencies found")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables for development."""
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': 'True',
        'FLASK_APP': 'projectgenius:create_app',
    }

    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"Set {key}={value}")

def check_database():
    """Check if database is set up."""
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///projectgenius.db')

    if db_url.startswith('sqlite:///'):
        db_file = db_url.replace('sqlite:///', '')

        # If relative path, assume instance folder
        if not os.path.isabs(db_file):
            db_file = os.path.join("instance", db_file)

        if not os.path.exists(db_file):
            print(f"⚠ Database file not found: {db_file}")
            print("Run: flask init-db && flask db upgrade")
            return False

    print("✓ Database configuration found")
    return True


def check_env_file():
    """Check if .env file exists."""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠ .env file not found")
        print("Copy .env.example to .env and configure your settings")

        # Create basic .env file
        with open('.env', 'w') as f:
            f.write("""# ProjectGenius Development Configuration
FLASK_ENV=development
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=sqlite:///projectgenius.db
""")
        print("✓ Created basic .env file")
    else:
        print("✓ .env file found")

def main():
    """Main function to start the development server."""
    parser = argparse.ArgumentParser(description='Start ProjectGenius development server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--skip-checks', action='store_true', help='Skip pre-flight checks')

    args = parser.parse_args()

    print("🚀 Starting ProjectGenius Development Server")
    print("=" * 50)

    if not args.skip_checks:
        print("\n📋 Running pre-flight checks...")

        # Check requirements
        if not check_requirements():
            sys.exit(1)

        # Set up environment
        print("\n🔧 Setting up environment...")
        setup_environment()
        check_env_file()

        # Check database
        print("\n🗄️ Checking database...")
        if not check_database():
            response = input("Would you like to set up the database? (y/N): ")
            if response.lower() == 'y':
                try:
                    subprocess.run(['flask', 'init-db'], check=True)
                    subprocess.run(['flask', 'db', 'init'], check=True)
                    subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration'], check=True)
                    subprocess.run(['flask', 'db', 'upgrade'], check=True)
                    print("✓ Database initialized")
                except subprocess.CalledProcessError:
                    print("✗ Failed to initialize database")
                    sys.exit(1)

    print(f"\n🌐 Starting server at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    # Set environment variables
    os.environ['HOST'] = args.host
    os.environ['PORT'] = str(args.port)

    if args.debug:
        os.environ['FLASK_DEBUG'] = 'True'

    try:
        # Import and run the app using factory
        from projectgenius import create_app
        app = create_app()
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or os.environ.get('FLASK_DEBUG', '').lower() == 'true',
            threaded=True
        )
    except ImportError as e:
        print(f"✗ Failed to import application: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n✗ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
