# ProjectGenius - Production Setup

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
