from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# db will be set from app.py
db = None

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # WordPress integration settings
    wordpress_url = db.Column(db.String(200))
    wordpress_username = db.Column(db.String(80))
    wordpress_password = db.Column(db.String(200))
    auto_sync_enabled = db.Column(db.Boolean, default=False)
    
    # Relationships
    channels = db.relationship('Channel', backref='user', lazy=True, cascade='all, delete-orphan')
    blog_posts = db.relationship('BlogPost', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'wordpress_url': self.wordpress_url,
            'auto_sync_enabled': self.auto_sync_enabled
        }

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.String(50), nullable=False)
    channel_url = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    subscriber_count = db.Column(db.Integer, default=0)
    video_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.BigInteger, default=0)
    indexed_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_sync = db.Column(db.DateTime)
    
    # Relationships
    videos = db.relationship('Video', backref='channel', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'channel_url': self.channel_url,
            'title': self.title,
            'description': self.description,
            'subscriber_count': self.subscriber_count,
            'video_count': self.video_count,
            'view_count': self.view_count,
            'indexed_at': self.indexed_at.isoformat() if self.indexed_at else None,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None
        }

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    video_id = db.Column(db.String(50), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(300))
    duration = db.Column(db.String(20))
    view_count = db.Column(db.BigInteger, default=0)
    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime)
    tags = db.Column(db.Text)  # JSON string of tags
    category_id = db.Column(db.String(10))
    
    # Content processing
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    key_points = db.Column(db.Text)  # JSON string
    blog_ready = db.Column(db.Boolean, default=False)
    
    # Relationships
    blog_posts = db.relationship('BlogPost', backref='video', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'duration': self.duration,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'comment_count': self.comment_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'tags': self.tags,
            'category_id': self.category_id,
            'summary': self.summary,
            'blog_ready': self.blog_ready
        }

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')  # draft, published, scheduled
    wordpress_post_id = db.Column(db.Integer)
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'content': self.content,
            'excerpt': self.excerpt,
            'status': self.status,
            'wordpress_post_id': self.wordpress_post_id,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }