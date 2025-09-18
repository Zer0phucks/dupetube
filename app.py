from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dupetube.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Update database reference in models
import models
models.db = db

# Import models and routes after db initialization
from models import User, Channel, Video, BlogPost
from routes.auth import auth_bp
from routes.channels import channels_bp
from routes.videos import videos_bp
from routes.blog import blog_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(channels_bp, url_prefix='/api/channels')
app.register_blueprint(videos_bp, url_prefix='/api/videos')
app.register_blueprint(blog_bp, url_prefix='/api/blog')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'DupeTube API is running'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)