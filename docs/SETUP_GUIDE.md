# ProjectGenius Setup and Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Development Setup](#development-setup)
3. [Database Configuration](#database-configuration)
4. [Environment Variables](#environment-variables)
5. [Running the Application](#running-the-application)
6. [Production Deployment](#production-deployment)
7. [Docker Deployment](#docker-deployment)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Database**: PostgreSQL 13+ (production) or SQLite 3.8+ (development)
- **Redis**: 5.0+ (optional, for caching and sessions)
- **Node.js**: 16+ (for frontend build tools, optional)
- **Git**: Latest version

### Development Tools
- **IDE**: VS Code, PyCharm, or similar
- **Terminal**: Bash, Zsh, or PowerShell
- **Docker**: Latest version (for containerized deployment)

### Operating System Support
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: 11.0+
- **Windows**: 10/11 with WSL2 recommended

## Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/projectgenius.git
cd ProjectGenius
```

### 2. Create Virtual Environment
```bash
# Using venv (recommended)
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.11+
```

### 3. Install Dependencies
```bash
# Install production dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e .[dev]

# Verify installation
pip list | grep Flask
```

### 4. Install Development Tools (Optional)
```bash
# Install development dependencies
pip install pytest pytest-cov black flake8 mypy isort pre-commit

# Set up pre-commit hooks
pre-commit install
```

## Database Configuration

### SQLite (Development)
SQLite is the default for development and requires no additional setup.

```bash
# Database will be created automatically at first run
export DATABASE_URL="sqlite:///projectgenius.db"
```

### PostgreSQL (Production)

#### Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib

# macOS (using Homebrew)
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

#### Create Database and User
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE projectgenius;
CREATE USER pguser WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE projectgenius TO pguser;
ALTER USER pguser CREATEDB;
\q
```

#### Test Connection
```bash
psql -h localhost -U pguser -d projectgenius
```

## Environment Variables

### 1. Create Environment File
```bash
cp .env.example .env
```

### 2. Configure Environment Variables

#### Basic Configuration
```env
# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-in-production

# Database Configuration
DATABASE_URL=postgresql://pguser:your_password@localhost:5432/projectgenius

# For development with SQLite:
# DATABASE_URL=sqlite:///projectgenius.db

# Security
JWT_SECRET_KEY=your-jwt-secret-key-here
BCRYPT_LOG_ROUNDS=12

# File Upload Settings
UPLOAD_FOLDER=instance/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### AI Service Configuration
```env
# AI Services (optional)
DEEPSEEK_API_KEY=your-deepseek-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
```

#### Redis Configuration (optional)
```env
# Redis for caching and sessions
REDIS_URL=redis://localhost:6379/0
CACHE_TYPE=redis
SESSION_TYPE=redis
```

### 3. Environment-Specific Configurations

#### Development (.env.development)
```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///projectgenius.db
LOG_LEVEL=DEBUG
```

#### Production (.env.production)
```env
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://user:pass@localhost:5432/projectgenius
LOG_LEVEL=INFO
FORCE_HTTPS=True
```

## Running the Application

### Development Mode

#### Option 1: Standalone Application (Quickstart)
```bash
# Run the complete working application
python projectgenius_app.py

# Application will start on http://localhost:5000
```

#### Option 2: Modular Application
```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create admin user
flask create-admin

# Run development server
python run_dev.py

# Or using Flask CLI
export FLASK_APP=projectgenius
flask run --host=0.0.0.0 --port=5000
```

### Database Management
```bash
# Initialize database (first time only)
flask init-db

# Create migrations
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Seed demo data
flask seed-data --demo

# Create admin user
flask create-admin --username admin --email admin@example.com
```

### Verify Installation
```bash
# Check application health
curl http://localhost:5000/api/health

# Check database connection
flask db-status

# Run basic tests
python -m pytest tests/test_server.py -v
```

## Production Deployment

### 1. Prepare Production Environment

#### System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx redis-server

# Create application user
sudo useradd -m -s /bin/bash projectgenius
sudo usermod -aG www-data projectgenius
```

#### Application Directory
```bash
# Create application directory
sudo mkdir -p /var/www/projectgenius
sudo chown projectgenius:projectgenius /var/www/projectgenius

# Switch to application user
sudo -u projectgenius -i
cd /var/www/projectgenius

# Clone repository
git clone https://github.com/yourusername/projectgenius.git .
```

### 2. Production Setup Script
```bash
# Run production setup
python setup_production.py

# This script will:
# - Create virtual environment
# - Install dependencies
# - Configure database
# - Set up logging
# - Create systemd services
```

### 3. Manual Production Setup

#### Virtual Environment and Dependencies
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

#### Database Setup
```bash
# Set production environment variables
export FLASK_ENV=production
export DATABASE_URL="postgresql://pguser:password@localhost:5432/projectgenius"

# Initialize database
flask db upgrade
flask create-admin
```

#### Create Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
preload_app = True
```

### 4. Systemd Service Configuration

#### Create Service File
```bash
sudo nano /etc/systemd/system/projectgenius.service
```

```ini
[Unit]
Description=ProjectGenius Flask Application
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=forking
User=projectgenius
Group=www-data
WorkingDirectory=/var/www/projectgenius
Environment=PATH=/var/www/projectgenius/venv/bin
Environment=FLASK_ENV=production
EnvironmentFile=/var/www/projectgenius/.env
ExecStart=/var/www/projectgenius/venv/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable projectgenius
sudo systemctl start projectgenius
sudo systemctl status projectgenius
```

### 5. Nginx Configuration

#### Create Nginx Site Configuration
```bash
sudo nano /etc/nginx/sites-available/projectgenius
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    
    # Static files
    location /static/ {
        alias /var/www/projectgenius/projectgenius/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # File uploads
    location /uploads/ {
        alias /var/www/projectgenius/instance/uploads/;
        expires 1y;
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket support (if needed)
    location /socket.io/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Enable Site and Test Configuration
```bash
sudo ln -s /etc/nginx/sites-available/projectgenius /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn psycopg2-binary

# Copy project
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Collect static files and create directories
RUN mkdir -p instance/uploads logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
```

### 2. Create Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://pguser:password@db:5432/projectgenius
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - static_volume:/app/projectgenius/static
      - media_volume:/app/instance/uploads
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=projectgenius
      - POSTGRES_USER=pguser
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d --build

# Run database migrations
docker-compose exec web flask db upgrade

# Create admin user
docker-compose exec web flask create-admin

# View logs
docker-compose logs -f web

# Scale web service
docker-compose up -d --scale web=3
```

## Testing

### Unit Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=projectgenius --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with markers
pytest -m "not slow" -v
```

### Integration Tests
```bash
# Run integration tests
pytest tests/test_api.py tests/test_server.py

# Test with production-like settings
FLASK_ENV=testing pytest tests/
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f tests/load_test.py --host=http://localhost:5000
```

### Database Testing
```bash
# Test database connections
flask test-db

# Run migration tests
pytest tests/test_migrations.py
```

## Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check database status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U pguser -d projectgenius

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R projectgenius:projectgenius /var/www/projectgenius
sudo chmod -R 755 /var/www/projectgenius
sudo chmod -R 775 instance/uploads
```

#### Service Start Issues
```bash
# Check service status
sudo systemctl status projectgenius

# View service logs
sudo journalctl -u projectgenius -f

# Test Gunicorn manually
cd /var/www/projectgenius
source venv/bin/activate
gunicorn --config gunicorn.conf.py wsgi:app
```

#### Nginx Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log

# Reload Nginx configuration
sudo systemctl reload nginx
```

### Debug Mode
```bash
# Enable debug mode
export FLASK_DEBUG=True
export LOG_LEVEL=DEBUG

# Check debug information
flask shell
>>> from projectgenius import db
>>> db.engine.execute('SELECT 1')
```

### Performance Issues
```bash
# Check system resources
htop
df -h
free -m

# Monitor database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Check application logs
tail -f logs/app.log
```

## Monitoring and Maintenance

### Application Monitoring
```bash
# Check application health
curl http://localhost:8000/api/health

# Monitor response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/
```

### Database Maintenance
```bash
# Database backup
pg_dump -U pguser projectgenius > backup_$(date +%Y%m%d).sql

# Vacuum database
sudo -u postgres psql -d projectgenius -c "VACUUM ANALYZE;"

# Check database size
sudo -u postgres psql -d projectgenius -c "SELECT pg_size_pretty(pg_database_size('projectgenius'));"
```

### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/projectgenius
```

```
/var/www/projectgenius/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 projectgenius projectgenius
    postrotate
        systemctl reload projectgenius
    endscript
}
```

### Automated Backups
```bash
# Create backup script
sudo nano /usr/local/bin/backup_projectgenius.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/projectgenius"
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -U pguser projectgenius | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# File backup
tar -czf $BACKUP_DIR/files_$DATE.tar.gz /var/www/projectgenius/instance/uploads

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete
```

### Security Updates
```bash
# System updates
sudo apt update && sudo apt upgrade

# Python dependency updates
pip list --outdated
pip install -U package_name

# Security scanning
pip audit
```

### Performance Optimization
```bash
# Enable database query logging
# In postgresql.conf:
# log_statement = 'all'
# log_duration = on

# Optimize database
sudo -u postgres psql -d projectgenius -c "REINDEX DATABASE projectgenius;"

# Monitor slow queries
sudo -u postgres psql -d projectgenius -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

## Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://sqlalchemy.org/)
- [PostgreSQL Documentation](https://postgresql.org/docs/)

### Community
- [ProjectGenius GitHub Issues](https://github.com/yourusername/projectgenius/issues)
- [Flask Community](https://discord.gg/flask)
- [Python Discord](https://discord.gg/python)

### Support
- **Email**: support@projectgenius.edu
- **Documentation**: https://docs.projectgenius.edu
- **Status Page**: https://status.projectgenius.edu

---

This guide covers comprehensive setup and deployment scenarios for ProjectGenius. For specific deployment questions or issues, please refer to the troubleshooting section or contact support.