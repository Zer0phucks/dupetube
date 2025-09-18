from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Channel, Video, BlogPost
from services.blog_service import BlogService
from datetime import datetime

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/posts', methods=['GET'])
@jwt_required()
def get_blog_posts():
    """Get all blog posts for the user"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')  # draft, published, scheduled
        
        query = BlogPost.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        posts = query.order_by(BlogPost.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'posts': [post.to_dict() for post in posts.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': posts.total,
                'pages': posts.pages,
                'has_next': posts.has_next,
                'has_prev': posts.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['GET'])
@jwt_required()
def get_blog_post(post_id):
    """Get a specific blog post"""
    try:
        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=post_id, user_id=user_id).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        return jsonify({'post': post.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_blog_post():
    """Generate a blog post from a video"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        # Get video and verify ownership
        video = db.session.query(Video).join(Channel).filter(
            Video.id == video_id,
            Channel.user_id == user_id
        ).first()
        
        if not video:
            return jsonify({'error': 'Video not found'}), 404
        
        # Check if blog post already exists for this video
        existing_post = BlogPost.query.filter_by(video_id=video_id, user_id=user_id).first()
        if existing_post:
            return jsonify({
                'message': 'Blog post already exists for this video',
                'post': existing_post.to_dict()
            }), 200
        
        # Generate blog post
        blog_service = BlogService()
        blog_post = blog_service.generate_blog_post(video, user)
        
        return jsonify({
            'message': 'Blog post generated successfully',
            'post': blog_post.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_blog_post(post_id):
    """Update a blog post"""
    try:
        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=post_id, user_id=user_id).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            post.title = data['title']
        if 'content' in data:
            post.content = data['content']
        if 'excerpt' in data:
            post.excerpt = data['excerpt']
        if 'status' in data:
            post.status = data['status']
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post updated successfully',
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>/publish', methods=['POST'])
@jwt_required()
def publish_blog_post(post_id):
    """Publish a blog post to WordPress"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        post = BlogPost.query.filter_by(id=post_id, user_id=user_id).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        if not user.wordpress_url:
            return jsonify({'error': 'WordPress configuration not found'}), 400
        
        # Publish to WordPress
        blog_service = BlogService()
        wordpress_post_id = blog_service.publish_to_wordpress(post, user)
        
        # Update post status
        post.wordpress_post_id = wordpress_post_id
        post.status = 'published'
        post.published_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Blog post published successfully',
            'wordpress_post_id': wordpress_post_id,
            'post': post.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/posts/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_blog_post(post_id):
    """Delete a blog post"""
    try:
        user_id = get_jwt_identity()
        post = BlogPost.query.filter_by(id=post_id, user_id=user_id).first()
        
        if not post:
            return jsonify({'error': 'Blog post not found'}), 404
        
        db.session.delete(post)
        db.session.commit()
        
        return jsonify({'message': 'Blog post deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@blog_bp.route('/bulk-generate', methods=['POST'])
@jwt_required()
def bulk_generate_posts():
    """Generate blog posts for multiple videos"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        video_ids = data.get('video_ids', [])
        
        if not video_ids:
            return jsonify({'error': 'Video IDs are required'}), 400
        
        # Get videos and verify ownership
        videos = db.session.query(Video).join(Channel).filter(
            Video.id.in_(video_ids),
            Channel.user_id == user_id
        ).all()
        
        if len(videos) != len(video_ids):
            return jsonify({'error': 'Some videos not found or not accessible'}), 404
        
        blog_service = BlogService()
        generated_posts = []
        
        for video in videos:
            # Skip if blog post already exists
            existing_post = BlogPost.query.filter_by(video_id=video.id, user_id=user_id).first()
            if existing_post:
                continue
            
            try:
                blog_post = blog_service.generate_blog_post(video, user)
                generated_posts.append(blog_post.to_dict())
            except Exception as e:
                print(f"Failed to generate blog post for video {video.id}: {e}")
        
        return jsonify({
            'message': f'Generated {len(generated_posts)} blog posts',
            'posts': generated_posts
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500