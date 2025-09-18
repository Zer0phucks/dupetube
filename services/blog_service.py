import os
from datetime import datetime
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import posts
from models import db, BlogPost
from services.content_service import ContentService

class BlogService:
    def __init__(self):
        self.content_service = ContentService()
    
    def generate_blog_post(self, video, user):
        """Generate a blog post from a video"""
        try:
            # Process video content if not already done
            if not video.transcript:
                video.transcript = self.content_service.get_video_transcript(video.video_id)
            
            if not video.summary and video.transcript:
                summary_data = self.content_service.generate_summary(video.transcript, video.title)
                video.summary = summary_data.get('summary')
                video.key_points = summary_data.get('key_points')
                video.blog_ready = True
                db.session.commit()
            
            # Generate blog content
            blog_content = self.content_service.generate_blog_content(video)
            
            # Create blog post record
            blog_post = BlogPost(
                user_id=user.id,
                video_id=video.id,
                title=blog_content['title'],
                content=blog_content['content'],
                excerpt=blog_content['excerpt'],
                status='draft'
            )
            
            db.session.add(blog_post)
            db.session.commit()
            
            return blog_post
            
        except Exception as e:
            print(f"Error generating blog post: {e}")
            raise e
    
    def auto_generate_blog_post(self, video, user):
        """Auto-generate and optionally publish a blog post"""
        try:
            # Generate the blog post
            blog_post = self.generate_blog_post(video, user)
            
            # If user has auto-sync enabled and WordPress configured, publish it
            if user.auto_sync_enabled and user.wordpress_url:
                try:
                    wordpress_post_id = self.publish_to_wordpress(blog_post, user)
                    blog_post.wordpress_post_id = wordpress_post_id
                    blog_post.status = 'published'
                    blog_post.published_at = datetime.utcnow()
                    db.session.commit()
                except Exception as e:
                    print(f"Failed to auto-publish to WordPress: {e}")
                    # Keep the blog post as draft if publishing fails
            
            return blog_post
            
        except Exception as e:
            print(f"Error in auto-generate blog post: {e}")
            raise e
    
    def publish_to_wordpress(self, blog_post, user):
        """Publish a blog post to WordPress"""
        try:
            if not user.wordpress_url or not user.wordpress_username or not user.wordpress_password:
                raise ValueError("WordPress configuration incomplete")
            
            # Prepare WordPress client
            wp_url = user.wordpress_url.rstrip('/')
            if not wp_url.endswith('/xmlrpc.php'):
                wp_url += '/xmlrpc.php'
            
            client = Client(wp_url, user.wordpress_username, user.wordpress_password)
            
            # Create WordPress post
            wp_post = WordPressPost()
            wp_post.title = blog_post.title
            wp_post.content = blog_post.content
            wp_post.excerpt = blog_post.excerpt
            wp_post.post_status = 'publish'
            
            # Add custom fields or categories if needed
            wp_post.terms_names = {
                'category': ['Video Content', 'Blog'],
                'post_tag': ['youtube', 'video', 'content']
            }
            
            # Publish the post
            wordpress_post_id = client.call(posts.NewPost(wp_post))
            
            return wordpress_post_id
            
        except Exception as e:
            print(f"Error publishing to WordPress: {e}")
            raise e
    
    def update_wordpress_post(self, blog_post, user):
        """Update an existing WordPress post"""
        try:
            if not blog_post.wordpress_post_id:
                raise ValueError("Blog post not published to WordPress yet")
            
            if not user.wordpress_url or not user.wordpress_username or not user.wordpress_password:
                raise ValueError("WordPress configuration incomplete")
            
            wp_url = user.wordpress_url.rstrip('/')
            if not wp_url.endswith('/xmlrpc.php'):
                wp_url += '/xmlrpc.php'
            
            client = Client(wp_url, user.wordpress_username, user.wordpress_password)
            
            # Update WordPress post
            wp_post = WordPressPost()
            wp_post.title = blog_post.title
            wp_post.content = blog_post.content
            wp_post.excerpt = blog_post.excerpt
            
            # Update the post
            success = client.call(posts.EditPost(blog_post.wordpress_post_id, wp_post))
            
            if success:
                blog_post.updated_at = datetime.utcnow()
                db.session.commit()
            
            return success
            
        except Exception as e:
            print(f"Error updating WordPress post: {e}")
            raise e
    
    def delete_wordpress_post(self, blog_post, user):
        """Delete a WordPress post"""
        try:
            if not blog_post.wordpress_post_id:
                return True  # Nothing to delete
            
            if not user.wordpress_url or not user.wordpress_username or not user.wordpress_password:
                raise ValueError("WordPress configuration incomplete")
            
            wp_url = user.wordpress_url.rstrip('/')
            if not wp_url.endswith('/xmlrpc.php'):
                wp_url += '/xmlrpc.php'
            
            client = Client(wp_url, user.wordpress_username, user.wordpress_password)
            
            # Delete the post
            success = client.call(posts.DeletePost(blog_post.wordpress_post_id))
            
            return success
            
        except Exception as e:
            print(f"Error deleting WordPress post: {e}")
            raise e
    
    def test_wordpress_connection(self, user):
        """Test WordPress connection settings"""
        try:
            if not user.wordpress_url or not user.wordpress_username or not user.wordpress_password:
                return {'success': False, 'message': 'WordPress configuration incomplete'}
            
            wp_url = user.wordpress_url.rstrip('/')
            if not wp_url.endswith('/xmlrpc.php'):
                wp_url += '/xmlrpc.php'
            
            client = Client(wp_url, user.wordpress_username, user.wordpress_password)
            
            # Try to get user info to test connection
            user_info = client.call(posts.GetPosts({'number': 1}))
            
            return {'success': True, 'message': 'WordPress connection successful'}
            
        except Exception as e:
            return {'success': False, 'message': f'WordPress connection failed: {str(e)}'}
    
    def get_wordpress_categories(self, user):
        """Get available WordPress categories"""
        try:
            if not user.wordpress_url or not user.wordpress_username or not user.wordpress_password:
                return []
            
            wp_url = user.wordpress_url.rstrip('/')
            if not wp_url.endswith('/xmlrpc.php'):
                wp_url += '/xmlrpc.php'
            
            client = Client(wp_url, user.wordpress_username, user.wordpress_password)
            
            from wordpress_xmlrpc.methods import taxonomies
            categories = client.call(taxonomies.GetTerms('category'))
            
            return [{'id': cat.id, 'name': cat.name, 'slug': cat.slug} for cat in categories]
            
        except Exception as e:
            print(f"Error getting WordPress categories: {e}")
            return []