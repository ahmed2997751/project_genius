#!/usr/bin/env python3
"""
Simple test server for ProjectGenius
"""
import os
from flask import Flask, render_template_string, jsonify

# Create Flask app
app = Flask(__name__)
app.secret_key = "test-secret-key"

# Configure basic settings
app.config["DEBUG"] = True
app.config["TESTING"] = False

# Set database URL (using the PostgreSQL URL)
db_url = os.environ.get("DATABASE_URL", "postgresql://mokwa:simple1234@localhost:5432/projectgenius")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url

# Set API keys
deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "sk-7a45473cf92f47299f8fc23ee5df6667")
huggingface_key = os.environ.get("HUGGINGFACE_API_KEY")

# Create a simple HTML template
WELCOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ProjectGenius Test Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f7f9;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .card {
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        .config-item {
            margin: 10px 0;
            padding: 10px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }
        .api-key {
            font-family: monospace;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <h1>ProjectGenius Test Server</h1>

    <div class="card">
        <h2>Status: <span class="success">Running</span></h2>
        <p>The Flask server is running correctly!</p>
    </div>

    <div class="card">
        <h2>Configuration</h2>

        <div class="config-item">
            <strong>Database URL:</strong><br>
            {{ db_url_masked }}
        </div>

        <div class="config-item">
            <strong>DeepSeek API Key:</strong><br>
            <span class="api-key">{{ deepseek_key_masked }}</span>
        </div>

        <div class="config-item">
            <strong>Hugging Face API Key:</strong><br>
            <span class="api-key">{{ huggingface_key_masked }}</span>
        </div>
    </div>

    <div class="card">
        <h2>API Endpoints</h2>
        <ul>
            <li><a href="/api/health">/api/health</a> - Health check endpoint</li>
            <li><a href="/api/config">/api/config</a> - View configuration information</li>
        </ul>
    </div>
</body>
</html>
"""

# Define routes
@app.route('/')
def index():
    """Home page route"""
    # Mask sensitive information for display
    db_parts = db_url.split('@')
    db_url_masked = db_parts[0].split(':')[0] + ':****@' + db_parts[1] if len(db_parts) > 1 else db_url

    deepseek_key_masked = deepseek_key[:5] + '...' + deepseek_key[-5:] if deepseek_key else 'Not set'
    huggingface_key_masked = huggingface_key[:5] + '...' + huggingface_key[-5:] if huggingface_key else 'Not set'

    return render_template_string(
        WELCOME_TEMPLATE,
        db_url_masked=db_url_masked,
        deepseek_key_masked=deepseek_key_masked,
        huggingface_key_masked=huggingface_key_masked
    )

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'configured',
        'ai_services': {
            'deepseek': bool(deepseek_key),
            'huggingface': bool(huggingface_key)
        }
    })

@app.route('/api/config')
def config_info():
    """Configuration information endpoint"""
    return jsonify({
        'database_type': db_url.split(':')[0] if ':' in db_url else 'unknown',
        'debug_mode': app.debug,
        'testing_mode': app.testing,
        'api_services': {
            'deepseek': 'configured' if deepseek_key else 'not configured',
            'huggingface': 'configured' if huggingface_key else 'not configured'
        }
    })

if __name__ == '__main__':
    print("Starting ProjectGenius Test Server...")
    print(f"Database URL: {db_url}")
    print(f"DeepSeek API Key: {'Configured' if deepseek_key else 'Not configured'}")
    print(f"Hugging Face API Key: {'Configured' if huggingface_key else 'Not configured'}")

    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))

    print(f"Server running at http://{host}:{port} (or http://localhost:{port} if accessing locally)")

    app.run(host=host, port=port, debug=True)
