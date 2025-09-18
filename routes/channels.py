from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Channel, Video
from services.youtube_service import YouTubeService
from datetime import datetime
import re

channels_bp = Blueprint('channels', __name__)

@channels_bp.route('/', methods=['POST'])
@jwt_required()
def add_channel():
    """Add a YouTube channel during onboarding"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        channel_url = data.get('channel_url')
        
        if not channel_url:
            return jsonify({'error': 'Channel URL is required'}), 400
        
        # Extract channel ID from URL
        channel_id = extract_channel_id(channel_url)
        if not channel_id:
            return jsonify({'error': 'Invalid YouTube channel URL'}), 400
        
        # Check if channel already exists for this user
        existing_channel = Channel.query.filter_by(user_id=user_id, channel_id=channel_id).first()
        if existing_channel:
            return jsonify({'error': 'Channel already added'}), 400
        
        # Get channel info from YouTube API
        youtube_service = YouTubeService()
        channel_info = youtube_service.get_channel_info(channel_id)
        
        if not channel_info:
            return jsonify({'error': 'Channel not found or API error'}), 404
        
        # Create channel record
        channel = Channel(
            user_id=user_id,
            channel_id=channel_id,
            channel_url=channel_url,
            title=channel_info.get('title', ''),
            description=channel_info.get('description', ''),
            subscriber_count=channel_info.get('subscriber_count', 0),
            video_count=channel_info.get('video_count', 0),
            view_count=channel_info.get('view_count', 0),
            indexed_at=datetime.utcnow()
        )
        
        db.session.add(channel)
        db.session.commit()
        
        return jsonify({
            'message': 'Channel added successfully',
            'channel': channel.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@channels_bp.route('/', methods=['GET'])
@jwt_required()
def get_channels():
    """Get all channels for the user"""
    try:
        user_id = get_jwt_identity()
        channels = Channel.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'channels': [channel.to_dict() for channel in channels]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@channels_bp.route('/<int:channel_id>/index', methods=['POST'])
@jwt_required()
def index_channel_videos(channel_id):
    """Index all videos from a channel"""
    try:
        user_id = get_jwt_identity()
        channel = Channel.query.filter_by(id=channel_id, user_id=user_id).first()
        
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404
        
        youtube_service = YouTubeService()
        videos_data = youtube_service.get_channel_videos(channel.channel_id)
        
        indexed_count = 0
        for video_data in videos_data:
            # Check if video already exists
            existing_video = Video.query.filter_by(video_id=video_data['video_id']).first()
            if existing_video:
                continue
            
            # Create video record
            video = Video(
                channel_id=channel.id,
                video_id=video_data['video_id'],
                title=video_data['title'],
                description=video_data['description'],
                thumbnail_url=video_data['thumbnail_url'],
                duration=video_data['duration'],
                view_count=video_data['view_count'],
                like_count=video_data['like_count'],
                comment_count=video_data['comment_count'],
                published_at=video_data['published_at'],
                tags=video_data['tags'],
                category_id=video_data['category_id']
            )
            
            db.session.add(video)
            indexed_count += 1
        
        # Update channel sync time
        channel.last_sync = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Indexed {indexed_count} new videos',
            'indexed_count': indexed_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@channels_bp.route('/<int:channel_id>/sync', methods=['POST'])
@jwt_required()
def sync_channel(channel_id):
    """Sync channel for new videos and auto-create blog posts if enabled"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        channel = Channel.query.filter_by(id=channel_id, user_id=user_id).first()
        
        if not channel:
            return jsonify({'error': 'Channel not found'}), 404
        
        # Index new videos
        youtube_service = YouTubeService()
        videos_data = youtube_service.get_channel_videos(channel.channel_id, limit=10)  # Get recent videos
        
        new_videos = []
        for video_data in videos_data:
            existing_video = Video.query.filter_by(video_id=video_data['video_id']).first()
            if existing_video:
                continue
            
            video = Video(
                channel_id=channel.id,
                video_id=video_data['video_id'],
                title=video_data['title'],
                description=video_data['description'],
                thumbnail_url=video_data['thumbnail_url'],
                duration=video_data['duration'],
                view_count=video_data['view_count'],
                like_count=video_data['like_count'],
                comment_count=video_data['comment_count'],
                published_at=video_data['published_at'],
                tags=video_data['tags'],
                category_id=video_data['category_id']
            )
            
            db.session.add(video)
            new_videos.append(video)
        
        db.session.commit()
        
        # Auto-create blog posts if enabled
        auto_created = 0
        if user.auto_sync_enabled and user.wordpress_url:
            from services.blog_service import BlogService
            blog_service = BlogService()
            
            for video in new_videos:
                try:
                    blog_service.auto_generate_blog_post(video, user)
                    auto_created += 1
                except Exception as e:
                    print(f"Failed to auto-create blog post for video {video.video_id}: {e}")
        
        # Update sync time
        channel.last_sync = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': f'Synced {len(new_videos)} new videos',
            'new_videos': len(new_videos),
            'auto_created_posts': auto_created
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_channel_id(url):
    """Extract YouTube channel ID from various URL formats"""
    patterns = [
        r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
        r'youtube\.com/c/([a-zA-Z0-9_-]+)',
        r'youtube\.com/user/([a-zA-Z0-9_-]+)',
        r'youtube\.com/@([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None