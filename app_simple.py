#!/usr/bin/env python3
"""
DupeTube - Simplified Demo Version
A basic demonstration of the core functionality without external dependencies.
"""

import json
import sqlite3
import hashlib
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

class DupeTubeHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db_path = 'dupetube_demo.db'
        self.init_db()
        super().__init__(*args, **kwargs)
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                wordpress_url TEXT,
                auto_sync_enabled BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id TEXT NOT NULL,
                channel_url TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                subscriber_count INTEGER DEFAULT 0,
                video_count INTEGER DEFAULT 0,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL,
                video_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                view_count INTEGER DEFAULT 0,
                published_at TIMESTAMP,
                summary TEXT,
                blog_ready BOOLEAN DEFAULT 0,
                FOREIGN KEY (channel_id) REFERENCES channels (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blog_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                video_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path == '/':
            self.serve_homepage()
        elif path == '/api/health':
            self.json_response({'status': 'healthy', 'message': 'DupeTube Demo API is running'})
        elif path.startswith('/static/'):
            self.serve_static_file(path)
        elif path == '/demo':
            self.serve_demo_page()
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}
        
        if path == '/api/demo/register':
            self.handle_demo_register(data)
        elif path == '/api/demo/add-channel':
            self.handle_demo_add_channel(data)
        elif path == '/api/demo/generate-blog':
            self.handle_demo_generate_blog(data)
        else:
            self.send_error(404, 'Not Found')
    
    def serve_homepage(self):
        """Serve the main homepage"""
        html_content = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DupeTube - YouTube Content Repurposing</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f7fa; }}
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 60px 20px; text-align: center; margin-bottom: 40px; }}
                .header h1 {{ margin: 0; font-size: 3rem; font-weight: bold; }}
                .header p {{ margin: 20px 0 0; font-size: 1.2rem; opacity: 0.9; }}
                .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 50px; }}
                .feature {{ background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .feature h3 {{ color: #333; margin-top: 0; }}
                .feature p {{ color: #666; line-height: 1.6; }}
                .cta {{ text-align: center; margin: 50px 0; }}
                .btn {{ background: #667eea; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 1.1rem; cursor: pointer; text-decoration: none; display: inline-block; }}
                .btn:hover {{ background: #5a6fd8; }}
                .demo-section {{ background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .status {{ padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
                input[type="text"], input[type="email"], textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 DupeTube</h1>
                <p>Transform your YouTube videos into engaging blog posts, ebooks, and online courses</p>
            </div>
            
            <div class="container">
                <div class="features">
                    <div class="feature">
                        <h3>📺 YouTube Integration</h3>
                        <p>Connect your YouTube channel and automatically index all your videos for easy content management and repurposing.</p>
                    </div>
                    <div class="feature">
                        <h3>📝 AI-Powered Blog Generation</h3>
                        <p>Automatically generate engaging blog posts from your video content using advanced content processing algorithms.</p>
                    </div>
                    <div class="feature">
                        <h3>🔄 WordPress Sync</h3>
                        <p>Seamlessly publish generated content to your WordPress blog with automatic or manual synchronization options.</p>
                    </div>
                    <div class="feature">
                        <h3>📚 Content Suggestions</h3>
                        <p>Get intelligent suggestions for ebooks, online courses, and additional blog content based on your video library.</p>
                    </div>
                </div>
                
                <div class="cta">
                    <a href="/demo" class="btn">Try Interactive Demo</a>
                </div>
                
                <div class="demo-section">
                    <h2>How DupeTube Works</h2>
                    <ol>
                        <li><strong>Onboarding:</strong> Register and provide your YouTube channel URL</li>
                        <li><strong>Indexing:</strong> We analyze and index all your existing video content</li>
                        <li><strong>Content Generation:</strong> Generate blog posts from your videos automatically or manually</li>
                        <li><strong>Publishing:</strong> Publish directly to WordPress or download for manual posting</li>
                        <li><strong>Sync & Automation:</strong> Set up automatic posting for new videos</li>
                    </ol>
                    
                    <h3>Key Features:</h3>
                    <ul>
                        <li>Automatic video transcription and content analysis</li>
                        <li>SEO-optimized blog post generation</li>
                        <li>WordPress integration with one-click publishing</li>
                        <li>Content calendar and scheduling</li>
                        <li>Bulk processing for existing video libraries</li>
                        <li>Custom templates and styling options</li>
                        <li>Analytics and performance tracking</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_demo_page(self):
        """Serve the interactive demo page"""
        html_content = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>DupeTube - Interactive Demo</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; }
                .container { max-width: 800px; margin: 0 auto; }
                .header { text-align: center; margin-bottom: 40px; }
                .demo-step { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 30px; }
                .demo-step h3 { color: #333; margin-top: 0; }
                .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                .btn:hover { background: #5a6fd8; }
                .btn:disabled { background: #ccc; cursor: not-allowed; }
                input[type="text"], input[type="email"], textarea { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
                .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
                .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
                .video-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px; }
                .video-card { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: #f9f9f9; }
                .video-card h4 { margin: 0 0 10px 0; font-size: 14px; }
                .video-card p { margin: 0; font-size: 12px; color: #666; }
                .blog-preview { border: 1px solid #ddd; border-radius: 8px; padding: 20px; background: #f9f9f9; margin-top: 20px; }
                .blog-preview h4 { margin-top: 0; color: #333; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 DupeTube Demo</h1>
                    <p>Experience the full workflow of content repurposing</p>
                    <a href="/" style="color: #667eea; text-decoration: none;">← Back to Home</a>
                </div>
                
                <div class="demo-step">
                    <h3>Step 1: User Registration</h3>
                    <p>First, let's create your account:</p>
                    <input type="text" id="username" placeholder="Username" value="demo_user">
                    <input type="email" id="email" placeholder="Email" value="demo@example.com">
                    <button class="btn" onclick="registerUser()">Register</button>
                    <div id="register-status"></div>
                </div>
                
                <div class="demo-step">
                    <h3>Step 2: Add YouTube Channel</h3>
                    <p>Connect your YouTube channel to start indexing content:</p>
                    <input type="text" id="channel-url" placeholder="YouTube Channel URL" value="https://youtube.com/@TechReviews">
                    <button class="btn" onclick="addChannel()" id="add-channel-btn" disabled>Add Channel</button>
                    <div id="channel-status"></div>
                    <div id="channel-videos"></div>
                </div>
                
                <div class="demo-step">
                    <h3>Step 3: Generate Blog Content</h3>
                    <p>Select a video to generate a blog post:</p>
                    <button class="btn" onclick="generateBlog()" id="generate-blog-btn" disabled>Generate Blog Post</button>
                    <div id="blog-status"></div>
                    <div id="blog-preview"></div>
                </div>
                
                <div class="demo-step">
                    <h3>Step 4: WordPress Integration</h3>
                    <p>In the full version, you would configure WordPress settings and publish automatically:</p>
                    <input type="text" placeholder="WordPress Site URL" value="https://myblog.com">
                    <input type="text" placeholder="WordPress Username" value="admin">
                    <button class="btn" onclick="publishToWordPress()" id="publish-btn" disabled>Publish to WordPress</button>
                    <div class="info">
                        <strong>Demo Note:</strong> WordPress publishing is simulated in this demo. The full version includes real WordPress XML-RPC integration.
                    </div>
                </div>
            </div>
            
            <script>
                let demoState = {
                    registered: false,
                    channelAdded: false,
                    selectedVideo: null
                };
                
                function registerUser() {
                    const username = document.getElementById('username').value;
                    const email = document.getElementById('email').value;
                    
                    if (!username || !email) {
                        showStatus('register-status', 'Please fill in all fields', 'error');
                        return;
                    }
                    
                    fetch('/api/demo/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ username, email })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showStatus('register-status', 'Registration successful! ✅', 'success');
                            demoState.registered = true;
                            document.getElementById('add-channel-btn').disabled = false;
                        } else {
                            showStatus('register-status', data.message || 'Registration failed', 'error');
                        }
                    })
                    .catch(error => {
                        showStatus('register-status', 'Registration completed (demo mode)', 'success');
                        demoState.registered = true;
                        document.getElementById('add-channel-btn').disabled = false;
                    });
                }
                
                function addChannel() {
                    const channelUrl = document.getElementById('channel-url').value;
                    
                    if (!channelUrl) {
                        showStatus('channel-status', 'Please enter a channel URL', 'error');
                        return;
                    }
                    
                    showStatus('channel-status', 'Adding channel and indexing videos...', 'info');
                    
                    fetch('/api/demo/add-channel', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ channel_url: channelUrl })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showStatus('channel-status', `Channel added! Found ${data.video_count} videos.`, 'success');
                            displayDemoVideos();
                            demoState.channelAdded = true;
                            document.getElementById('generate-blog-btn').disabled = false;
                        } else {
                            showStatus('channel-status', data.message || 'Failed to add channel', 'error');
                        }
                    })
                    .catch(error => {
                        // Demo fallback
                        showStatus('channel-status', 'Channel added! Found 5 demo videos.', 'success');
                        displayDemoVideos();
                        demoState.channelAdded = true;
                        document.getElementById('generate-blog-btn').disabled = false;
                    });
                }
                
                function displayDemoVideos() {
                    const videos = [
                        { title: "10 Best Tech Gadgets of 2024", views: "125K", date: "2024-01-15" },
                        { title: "iPhone vs Android: Ultimate Comparison", views: "89K", date: "2024-01-10" },
                        { title: "Future of AI in Mobile Technology", views: "67K", date: "2024-01-05" },
                        { title: "Smart Home Setup Guide", views: "45K", date: "2023-12-28" },
                        { title: "Best Budget Laptops for Students", views: "123K", date: "2023-12-20" }
                    ];
                    
                    const videosHtml = videos.map((video, index) => `
                        <div class="video-card" onclick="selectVideo(${index})">
                            <h4>${video.title}</h4>
                            <p>${video.views} views • ${video.date}</p>
                        </div>
                    `).join('');
                    
                    document.getElementById('channel-videos').innerHTML = 
                        '<h4>Your Indexed Videos:</h4><div class="video-grid">' + videosHtml + '</div>';
                }
                
                function selectVideo(index) {
                    demoState.selectedVideo = index;
                    document.querySelectorAll('.video-card').forEach((card, i) => {
                        card.style.border = i === index ? '2px solid #667eea' : '1px solid #ddd';
                    });
                }
                
                function generateBlog() {
                    if (demoState.selectedVideo === null) {
                        showStatus('blog-status', 'Please select a video first', 'error');
                        return;
                    }
                    
                    showStatus('blog-status', 'Generating blog post from video content...', 'info');
                    
                    setTimeout(() => {
                        const blogContent = generateDemoBlogContent(demoState.selectedVideo);
                        showStatus('blog-status', 'Blog post generated successfully! ✅', 'success');
                        document.getElementById('blog-preview').innerHTML = blogContent;
                        document.getElementById('publish-btn').disabled = false;
                    }, 2000);
                }
                
                function generateDemoBlogContent(videoIndex) {
                    const blogPosts = [
                        {
                            title: "The 10 Must-Have Tech Gadgets That Will Transform Your 2024",
                            content: `<h4>The 10 Must-Have Tech Gadgets That Will Transform Your 2024</h4>
                            <p>Technology continues to evolve at breakneck speed, and 2024 has brought us some incredible gadgets that are changing the way we work, play, and live. From revolutionary AI-powered devices to sustainable tech solutions, this year's lineup is truly impressive.</p>
                            <h5>Top 5 Gadgets You Need to Know:</h5>
                            <ul>
                                <li><strong>AI Smart Glasses:</strong> The future of augmented reality is here</li>
                                <li><strong>Wireless Power Banks:</strong> Never worry about cables again</li>
                                <li><strong>Smart Home Hubs:</strong> Control everything with voice commands</li>
                                <li><strong>Foldable Tablets:</strong> The perfect blend of phone and tablet</li>
                                <li><strong>Eco-Friendly Chargers:</strong> Tech that cares about the planet</li>
                            </ul>
                            <p>Each of these gadgets represents a significant leap forward in their respective categories. Whether you're a tech enthusiast or just looking to upgrade your daily tools, these devices offer compelling reasons to make the investment.</p>
                            <p><em>Want to see these gadgets in action? Check out the full video review where I demonstrate each device and share my honest thoughts on their real-world performance.</em></p>`
                        }
                    ];
                    
                    return `<div class="blog-preview">${blogPosts[0].content}</div>`;
                }
                
                function publishToWordPress() {
                    showStatus('blog-status', 'Publishing to WordPress...', 'info');
                    setTimeout(() => {
                        showStatus('blog-status', 'Blog post published successfully to WordPress! 🎉', 'success');
                    }, 1500);
                }
                
                function showStatus(elementId, message, type) {
                    const element = document.getElementById(elementId);
                    element.innerHTML = `<div class="${type}">${message}</div>`;
                }
            </script>
        </body>
        </html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def handle_demo_register(self, data):
        """Handle demo registration"""
        self.json_response({
            'success': True,
            'message': 'Demo user registered successfully',
            'user_id': 1
        })
    
    def handle_demo_add_channel(self, data):
        """Handle demo channel addition"""
        self.json_response({
            'success': True,
            'message': 'Channel added successfully',
            'video_count': 5,
            'channel_id': 1
        })
    
    def handle_demo_generate_blog(self, data):
        """Handle demo blog generation"""
        self.json_response({
            'success': True,
            'message': 'Blog post generated successfully',
            'blog_post': {
                'title': 'Generated Blog Post',
                'content': 'Demo blog content...'
            }
        })
    
    def json_response(self, data):
        """Send JSON response"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_static_file(self, path):
        """Serve static files (placeholder)"""
        self.send_error(404, 'Static files not available in demo')
    
    def log_message(self, format, *args):
        """Override to reduce log noise"""
        pass

def run_server(port=8000):
    """Run the demo server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, DupeTubeHandler)
    print(f"🎬 DupeTube Demo Server running on http://localhost:{port}")
    print(f"Visit http://localhost:{port} to see the application")
    print(f"Visit http://localhost:{port}/demo for the interactive demo")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()