"""
TechRealm Backend - Main Application Entry Point
File: app.py
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'techrealm-secret-key-2025')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Import and register blueprints
from api.programs import programs_bp
from api.analytics import analytics_bp
from api.chatbot import chatbot_bp
from api.emails import emails_bp

app.register_blueprint(programs_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')
app.register_blueprint(chatbot_bp, url_prefix='/api')
app.register_blueprint(emails_bp, url_prefix='/api')

@app.route('/')
def home():
    return {
        'message': 'TechRealm Backend API',
        'version': '1.0.0',
        'status': 'active',
        'endpoints': {
            'programs': '/api/programs',
            'scraper': '/api/auto-scrape',
            'analytics': '/api/analytics',
            'chatbot': '/api/chat',
            'emails': '/api/emails'
        }
    }, 200

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )
    


