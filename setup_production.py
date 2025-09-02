#!/usr/bin/env python3
"""
Production Setup Script for ProjectGenius
Sets up a clean production environment without test data
"""

import os
import sys
import secrets
from pathlib import Path
import shutil
from datetime import datetime

def create_production_env():
    """Create production .env file with secure settings"""
    env_content = f"""# ProjectGenius Production Configuration
# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Environment
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY={secrets.token_hex(32)}
JWT_SECRET_KEY={secrets.token_hex(32)}
BCRYPT_LOG_ROUNDS=12

# Database
DATABASE_URL=sqlite:///projectgenius.db

# File Uploads
UPLOAD_FOLDER=instance/uploads
MAX_CONTENT_LENGTH=16777216

# Email Configuration (Configure for your SMTP server)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password

# API Keys (Optional - for AI features)
DEEPSEEK_API_KEY=your-deepseek-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Application Settings
COMPANY_NAME=ProjectGenius
SUPPORT_EMAIL=support@projectgenius.com
ADMIN_EMAIL=admin@projectgenius.com
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("✓ Created production .env file")
    print("  → Please update email settings and API keys in .env")

def setup_directories():
    """Create necessary directories for production"""
    directories = [
        'instance',
        'instance/uploads',
        'instance/backups',
        'logs',
        'static/uploads'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def initialize_clean_database():
    """Initialize database with clean schema, no test data"""
    try:
        # Set environment for production
        os.environ['DATABASE_URL'] = 'sqlite:///projectgenius.db'
        os.environ['FLASK_ENV'] = 'production'

        from projectgenius import create_app, db

        print("📊 Initializing production database...")

        app = create_app()
        with app.app_context():
            # Drop all existing tables (clean slate)
            db.drop_all()
            print("✓ Dropped existing tables")

            # Create all tables with fresh schema
            db.create_all()
            print("✓ Created database schema")

            # Verify tables were created
            tables = db.engine.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            table_names = [table[0] for table in tables if not table[0].startswith('sqlite_')]
            print(f"✓ Created {len(table_names)} tables: {', '.join(table_names)}")

        print("✅ Database initialized successfully (no test data)")
        return True

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def create_gitignore():
    """Create production .gitignore file"""
    gitignore_content = """# ProjectGenius Production .gitignore

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Instance folder
instance/
!instance/.gitkeep

# Logs
logs/
*.log

# Uploads
static/uploads/
uploads/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Backup files
*.backup
*.bak
backups/

# Temporary files
temp/
tmp/
"""

    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✓ Created production .gitignore")

def create_production_run_script():
    """Create production startup script"""
    run_script = """#!/usr/bin/env python3
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
        print("\\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == '__main__':
    main()
"""

    with open('run_production.py', 'w') as f:
        f.write(run_script)

    # Make it executable
    os.chmod('run_production.py', 0o755)
    print("✓ Created production run script: run_production.py")

def create_wsgi_file():
    """Create WSGI file for production deployment"""
    wsgi_content = """#!/usr/bin/env python3
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
"""

    with open('wsgi.py', 'w') as f:
        f.write(wsgi_content)
    print("✓ Created WSGI file for production deployment")

def create_readme():
    """Create production README file"""
    readme_content = """# ProjectGenius - Production Setup

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Edit .env file with your settings
   nano .env
   ```

3. **Start the Application**
   ```bash
   # Development
   python run_production.py

   # Production with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
   ```

## 📧 Email Configuration

Update these settings in `.env`:
```
MAIL_SERVER=smtp.your-provider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
```

## 🔐 Security

- Change the SECRET_KEY in production
- Use HTTPS in production
- Configure proper firewall rules
- Regular database backups

## 📱 Access

After starting the server, access your application at:
- Local: http://localhost:8000
- Network: http://your-server-ip:8000

## 👤 First User

Register your first user through the web interface at:
http://your-domain.com/auth/register

## 🆘 Support

For issues and documentation, visit:
https://github.com/your-username/ProjectGenius
"""

    with open('README_PRODUCTION.md', 'w') as f:
        f.write(readme_content)
    print("✓ Created production README")

def main():
    """Main setup function"""
    print("🏭 ProjectGenius Production Setup")
    print("=" * 40)

    try:
        # Create directories
        setup_directories()

        # Create configuration files
        create_production_env()
        create_gitignore()

        # Create run scripts
        create_production_run_script()
        create_wsgi_file()

        # Create documentation
        create_readme()

        # Initialize clean database
        if initialize_clean_database():
            print("\n🎉 Production setup completed successfully!")
            print("\n📋 Next Steps:")
            print("1. Edit .env file with your email/API settings")
            print("2. Review and customize configuration")
            print("3. Start server: python run_production.py")
            print("4. Register your first user via web interface")
            print("5. For production: gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app")

            print("\n🔗 Access URLs:")
            print("   • Home: http://localhost:8000")
            print("   • Register: http://localhost:8000/auth/register")
            print("   • Login: http://localhost:8000/auth/login")

        else:
            print("\n❌ Setup failed at database initialization")
            return False

    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return False

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
