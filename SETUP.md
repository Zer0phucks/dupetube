# 🚀 DupeTube Setup Guide

This guide will walk you through setting up DupeTube for both demo and production use.

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for API access
- YouTube channel (for full functionality)
- WordPress site (optional, for publishing)

## 🎯 Quick Demo Setup

For a quick demonstration without any dependencies:

```bash
# Clone the repository
git clone https://github.com/Zer0phucks/dupetube.git
cd dupetube

# Run the demo server (no installation required)
python3 app_simple.py
```

**Access the demo:**
- Main page: http://localhost:8000
- Interactive demo: http://localhost:8000/demo

The demo includes:
- Simulated user registration
- Mock YouTube channel integration
- Sample blog post generation
- WordPress publishing simulation

## 🔧 Full Production Setup

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

If you encounter dependency issues, install core packages individually:
```bash
pip install Flask Flask-SQLAlchemy Flask-JWT-Extended python-dotenv
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
pip install python-wordpress-xmlrpc youtube-transcript-api
pip install openai  # Optional, for enhanced AI features
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Flask Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///dupetube.db

# YouTube API Configuration
YOUTUBE_API_KEY=your-youtube-api-key-here

# OpenAI API Configuration (optional)
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. API Keys Setup

#### YouTube Data API v3
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Navigate to "APIs & Services" > "Library"
4. Search for "YouTube Data API v3" and enable it
5. Go to "Credentials" > "Create Credentials" > "API Key"
6. Copy the API key to your `.env` file

#### OpenAI API (Optional)
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Navigate to API Keys section
3. Create a new API key
4. Copy to your `.env` file

⚠️ **Note**: Without OpenAI API, the system will use basic content generation instead of AI-powered generation.

### 4. Database Setup

The application will automatically create the SQLite database on first run. For production, consider using PostgreSQL:

```env
DATABASE_URL=postgresql://username:password@localhost/dupetube
```

### 5. Run the Application

```bash
python3 app.py
```

Access the application at http://localhost:5000

## 🔑 WordPress Integration Setup

### 1. WordPress Configuration

In your WordPress admin panel:

1. **Install Application Passwords Plugin** (WordPress < 5.6) or use built-in application passwords (WordPress 5.6+)
2. **Create Application Password**:
   - Go to Users > Your Profile
   - Scroll to "Application Passwords"
   - Enter "DupeTube" as application name
   - Click "Add New Application Password"
   - Copy the generated password (save it securely)

### 2. Configure in DupeTube

1. Log into DupeTube
2. Go to Settings/Profile
3. Enter:
   - WordPress URL: `https://yourblog.com`
   - Username: Your WordPress username
   - Password: The application password you generated
4. Test the connection

### 3. Enable Auto-Sync (Optional)

Check "Auto-sync enabled" to automatically create blog posts when new videos are uploaded to your YouTube channel.

## 🎬 YouTube Channel Setup

### 1. Channel Requirements

- Channel must be public
- Videos should have clear audio for transcription
- Detailed descriptions help with content generation
- Proper tags improve content quality

### 2. Adding Your Channel

1. In DupeTube, go to "Onboarding" or "Channels"
2. Enter your channel URL in any of these formats:
   - `https://youtube.com/@username`
   - `https://youtube.com/c/channelname`
   - `https://youtube.com/user/username`
   - `https://youtube.com/channel/CHANNEL_ID`

### 3. Indexing Process

- The system will fetch channel information
- All public videos will be indexed
- Processing may take time for channels with many videos
- Videos are processed on-demand for blog generation

## 🔧 Troubleshooting

### Common Issues

#### "YouTube API Key not found"
- Ensure `YOUTUBE_API_KEY` is set in `.env`
- Verify the API key is valid and has YouTube Data API v3 enabled
- Check for any quota limitations

#### "Module not found" errors
- Run `pip install -r requirements.txt`
- If issues persist, install packages individually
- Consider using a virtual environment

#### WordPress connection failed
- Verify WordPress URL (include https://)
- Check username and application password
- Ensure WordPress site is accessible
- XML-RPC must be enabled (usually enabled by default)

#### Database errors
- Delete `dupetube.db` to reset database
- Check file permissions in the application directory
- For PostgreSQL, verify connection string

### Performance Optimization

#### For Large Channels
- Index videos in batches during off-peak hours
- Consider upgrading to PostgreSQL for better performance
- Use Redis for caching (optional)

#### Content Generation
- Videos with transcripts generate better content
- Longer videos (10-30 minutes) work best
- Clear audio improves transcription quality

## 🔒 Security Best Practices

### Production Deployment

1. **Use Strong Secrets**:
   ```bash
   # Generate secure keys
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Database Security**:
   - Use PostgreSQL in production
   - Enable SSL connections
   - Regular backups

3. **API Security**:
   - Restrict API keys to specific IP addresses when possible
   - Monitor API usage
   - Rotate keys periodically

4. **WordPress Security**:
   - Use application passwords instead of main password
   - Enable two-factor authentication
   - Keep WordPress updated

### Environment Variables

Never commit sensitive information to version control:
```bash
# Add to .gitignore
.env
*.db
__pycache__/
*.pyc
```

## 📊 Monitoring and Maintenance

### Log Files
- Application logs are output to console
- For production, configure proper logging
- Monitor API usage and rate limits

### Database Maintenance
```bash
# Backup SQLite database
cp dupetube.db dupetube_backup_$(date +%Y%m%d).db

# For PostgreSQL
pg_dump dupetube > backup_$(date +%Y%m%d).sql
```

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Check for API changes
# Review changelog before updating
```

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** for specific error messages
2. **Review this setup guide** for missed steps
3. **Search GitHub Issues** for similar problems
4. **Create a new issue** with detailed information:
   - Error messages
   - System information
   - Steps to reproduce

## 🎉 Next Steps

Once setup is complete:

1. **Register your account** in the application
2. **Add your YouTube channel** during onboarding
3. **Configure WordPress** settings (if using)
4. **Generate your first blog post** from a video
5. **Explore content suggestions** for books and courses

Happy content repurposing! 🚀