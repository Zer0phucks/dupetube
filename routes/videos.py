from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Channel, Video
from services.content_service import ContentService
from datetime import datetime

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/', methods=['GET'])
@jwt_required()
def get_videos():
    """Get all videos for the user with pagination"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        channel_id = request.args.get('channel_id', type=int)
        
        query = db.session.query(Video).join(Channel).filter(Channel.user_id == user_id)
        
        if channel_id:
            query = query.filter(Video.channel_id == channel_id)
        
        query = query.order_by(Video.published_at.desc())
        
        videos = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': videos.total,
                'pages': videos.pages,
                'has_next': videos.has_next,
                'has_prev': videos.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/<int:video_id>', methods=['GET'])
@jwt_required()
def get_video(video_id):
    """Get a specific video with full details"""
    try:
        user_id = get_jwt_identity()
        video = db.session.query(Video).join(Channel).filter(
            Video.id == video_id,
            Channel.user_id == user_id
        ).first()
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        return jsonify({'video': video.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/<int:video_id>/process', methods=['POST'])
@jwt_required()
def process_video(video_id):
    """Process video for content extraction (transcript, summary, etc.)"""
    try:
        user_id = get_jwt_identity()
        video = db.session.query(Video).join(Channel).filter(
            Video.id == video_id,
            Channel.user_id == user_id
        ).first()
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        content_service = ContentService()
        
        # Get transcript
        if not video.transcript:
            transcript = content_service.get_video_transcript(video.video_id)
            video.transcript = transcript
        
        # Generate summary and key points
        if not video.summary and video.transcript:
            summary_data = content_service.generate_summary(video.transcript, video.title)
            video.summary = summary_data.get('summary')
            video.key_points = summary_data.get('key_points')
        
        video.blog_ready = True
        db.session.commit()
        
        return jsonify({
            'message': 'Video processed successfully',
            'video': video.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/<int:video_id>/suggestions', methods=['GET'])
@jwt_required()
def get_content_suggestions(video_id):
    """Get suggestions for books, courses, and blog post ideas based on video content"""
    try:
        user_id = get_jwt_identity()
        video = db.session.query(Video).join(Channel).filter(
            Video.id == video_id,
            Channel.user_id == user_id
        ).first()
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        content_service = ContentService()
        suggestions = content_service.generate_content_suggestions(video)
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@videos_bp.route('/search', methods=['GET'])
@jwt_required()
def search_videos():
    """Search videos by title, description, or tags"""
    try:
        user_id = get_jwt_identity()
        query_text = request.args.get('q', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not query_text:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Search in title, description, and tags
        search_filter = db.or_(
            Video.title.ilike(f'%{query_text}%'),
            Video.description.ilike(f'%{query_text}%'),
            Video.tags.ilike(f'%{query_text}%')
        )
        
        videos = db.session.query(Video).join(Channel).filter(
            Channel.user_id == user_id,
            search_filter
        ).order_by(Video.published_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': videos.total,
                'pages': videos.pages,
                'has_next': videos.has_next,
                'has_prev': videos.has_prev
            },
            'query': query_text
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500