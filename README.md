# 🎬 DupeTube

**Transform your YouTube videos into engaging blog posts, ebooks, and online courses**

DupeTube is a comprehensive content repurposing platform that helps content creators maximize the value of their YouTube videos by automatically converting them into various formats for different audiences and platforms.

## ✨ Features

### Core Functionality
- **🔗 YouTube Integration**: Connect your channel and automatically index all videos
- **📝 AI-Powered Content Generation**: Transform video content into blog posts using advanced AI
- **🔄 WordPress Sync**: Seamlessly publish to WordPress with automatic or manual sync
- **📚 Content Suggestions**: Get intelligent recommendations for ebooks and courses
- **⚡ Bulk Processing**: Handle large video libraries efficiently

### User Experience
- **🚀 Simple Onboarding**: Quick setup with YouTube channel URL
- **📊 Dashboard**: Comprehensive overview of your content pipeline
- **🎯 Content Calendar**: Schedule and manage your content strategy
- **📈 Analytics**: Track performance across platforms

## 🚀 Quick Start

### Demo Version (No Dependencies)
```bash
# Clone the repository
git clone https://github.com/Zer0phucks/dupetube.git
cd dupetube

# Run the demo server
python3 app_simple.py
```

Visit `http://localhost:8000` to see the application and `http://localhost:8000/demo` for an interactive demo.

### Full Version Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Configuration**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys:
# - YOUTUBE_API_KEY: Your YouTube Data API v3 key
# - OPENAI_API_KEY: Your OpenAI API key (optional, for enhanced content generation)
# - SECRET_KEY: Flask secret key
# - JWT_SECRET_KEY: JWT signing key
```

3. **Run the Application**
```bash
python3 app.py
```

## 🔧 Configuration

### Required API Keys

1. **YouTube Data API v3**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable YouTube Data API v3
   - Create credentials (API Key)
   - Add key to `.env` file

2. **OpenAI API** (Optional - for enhanced content generation)
   - Sign up at [OpenAI](https://openai.com/)
   - Generate API key
   - Add to `.env` file

### WordPress Integration
Configure WordPress settings in the user profile:
- WordPress site URL
- Username and password (or application password)
- Enable/disable auto-sync

## 📋 User Journey

### 1. Onboarding
- Register account
- Add YouTube channel URL
- System indexes all existing videos
- Get content suggestions for books/courses

### 2. Content Generation
- Select videos for blog post generation
- AI processes video content (transcript, summary, key points)
- Generate SEO-optimized blog posts
- Review and edit generated content
- Preview before publishing

### 3. Publishing & Sync
- Manual publishing to WordPress
- Automatic sync for new videos
- Bulk operations for multiple posts
- Content scheduling

### 4. Content Strategy
- View analytics and performance
- Get suggestions for additional content
- Plan ebooks and course creation
- Manage content calendar

## 🏗️ Architecture

### Backend Components
- **Flask Web Application**: Core API and web interface
- **SQLAlchemy**: Database ORM for data management
- **YouTube API Integration**: Video and channel data fetching
- **Content Processing**: AI-powered content generation
- **WordPress XML-RPC**: Publishing integration

### Frontend
- **Responsive Web Interface**: Built with Bootstrap
- **JavaScript SPA**: Dynamic user interface
- **RESTful API Integration**: Seamless backend communication

### Database Schema
- **Users**: Account management and settings
- **Channels**: YouTube channel information
- **Videos**: Video metadata and processed content
- **Blog Posts**: Generated content and publishing status

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user settings

### Channels
- `POST /api/channels/` - Add YouTube channel
- `GET /api/channels/` - List user's channels
- `POST /api/channels/{id}/index` - Index channel videos
- `POST /api/channels/{id}/sync` - Sync new videos

### Videos
- `GET /api/videos/` - List videos with pagination
- `GET /api/videos/{id}` - Get video details
- `POST /api/videos/{id}/process` - Process video content
- `GET /api/videos/search` - Search videos

### Blog Posts
- `POST /api/blog/generate` - Generate blog post from video
- `GET /api/blog/posts` - List blog posts
- `PUT /api/blog/posts/{id}` - Update blog post
- `POST /api/blog/posts/{id}/publish` - Publish to WordPress
- `DELETE /api/blog/posts/{id}` - Delete blog post

## 🛠️ Development

### Project Structure
```
dupetube/
├── app.py                 # Main Flask application
├── app_simple.py         # Demo version (no dependencies)
├── models.py             # Database models
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
├── routes/              # API route handlers
│   ├── auth.py
│   ├── channels.py
│   ├── videos.py
│   └── blog.py
├── services/            # Business logic
│   ├── youtube_service.py
│   ├── content_service.py
│   └── blog_service.py
├── templates/           # HTML templates
│   └── index.html
└── static/             # CSS, JS, images
    ├── css/
    └── js/
```

### Running Tests
```bash
# Run the demo to test core functionality
python3 app_simple.py

# For full version testing (requires dependencies)
python3 -m pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 🔒 Security Considerations

- **API Key Management**: Store sensitive keys in environment variables
- **User Authentication**: JWT-based authentication with secure tokens
- **WordPress Security**: Use application passwords instead of main passwords
- **Input Validation**: All user inputs are validated and sanitized
- **Rate Limiting**: API calls are rate-limited to prevent abuse

## 📊 Use Cases

### Content Creators
- **YouTubers**: Repurpose video content for blog audiences
- **Educators**: Convert tutorials into written guides
- **Marketers**: Create multi-platform content strategies
- **Podcasters**: Generate show notes and articles

### Business Applications
- **Marketing Teams**: Scale content production
- **E-learning Platforms**: Convert video courses to text-based materials
- **Content Agencies**: Offer repurposing services to clients
- **Bloggers**: Expand into video content while maintaining written presence

## 🚦 Roadmap

### Phase 1 (Current)
- ✅ YouTube channel integration
- ✅ Basic blog post generation
- ✅ WordPress publishing
- ✅ User management

### Phase 2
- 🔄 Enhanced AI content generation
- 🔄 Multiple blog platform support
- 🔄 Content scheduling
- 🔄 Analytics dashboard

### Phase 3
- 📝 Ebook generation
- 📚 Course creation tools
- 🎨 Custom templates
- 📊 Advanced analytics

## 💡 Tips for Best Results

### Content Quality
- Ensure videos have clear audio for better transcription
- Use descriptive titles and detailed descriptions
- Add relevant tags to your YouTube videos
- Consider video length (10-30 minutes work best)

### Blog Optimization
- Review and edit generated content before publishing
- Add relevant images and media
- Optimize for SEO with proper headings
- Include calls-to-action

### WordPress Integration
- Use application passwords for better security
- Test connection before bulk operations
- Configure categories and tags appropriately
- Set up proper permalink structure

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check the wiki for detailed guides
- **Community**: Join discussions in GitHub Discussions
- **Contact**: Reach out via the repository

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- YouTube Data API for video information
- OpenAI for content generation capabilities
- WordPress XML-RPC for publishing integration
- Flask and SQLAlchemy for the web framework
- Bootstrap for responsive UI components

---

**Ready to transform your video content?** Start with the demo version and see how DupeTube can revolutionize your content strategy!