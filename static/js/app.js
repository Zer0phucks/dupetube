// DupeTube Frontend Application
class DupetubeApp {
    constructor() {
        this.token = localStorage.getItem('dupetube_token');
        this.user = JSON.parse(localStorage.getItem('dupetube_user') || 'null');
        this.baseURL = window.location.origin;
        this.init();
    }

    init() {
        this.setupEventListeners();
        if (this.token && this.user) {
            this.showDashboard();
        } else {
            this.showWelcome();
        }
    }

    setupEventListeners() {
        // Login form
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        // Register form
        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
    }

    // Authentication methods
    async handleLogin() {
        const username = document.getElementById('loginUsername').value;
        const password = document.getElementById('loginPassword').value;

        try {
            const response = await fetch(`${this.baseURL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                this.user = data.user;
                localStorage.setItem('dupetube_token', this.token);
                localStorage.setItem('dupetube_user', JSON.stringify(this.user));
                this.showAlert('Login successful!', 'success');
                this.showDashboard();
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Login failed. Please try again.', 'danger');
        }
    }

    async handleRegister() {
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;

        try {
            const response = await fetch(`${this.baseURL}/api/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access_token;
                this.user = data.user;
                localStorage.setItem('dupetube_token', this.token);
                localStorage.setItem('dupetube_user', JSON.stringify(this.user));
                this.showAlert('Registration successful!', 'success');
                this.showDashboard();
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Registration failed. Please try again.', 'danger');
        }
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem('dupetube_token');
        localStorage.removeItem('dupetube_user');
        this.showWelcome();
        this.showAlert('Logged out successfully!', 'info');
    }

    // Navigation methods
    showWelcome() {
        this.hideAllSections();
        document.getElementById('welcome-section').classList.remove('d-none');
        this.updateNavbar(false);
    }

    showLogin() {
        this.hideAllSections();
        document.getElementById('login-section').classList.remove('d-none');
        this.updateNavbar(false);
    }

    showRegister() {
        this.hideAllSections();
        document.getElementById('register-section').classList.remove('d-none');
        this.updateNavbar(false);
    }

    showDashboard() {
        this.hideAllSections();
        document.getElementById('dashboard-section').classList.remove('d-none');
        this.updateNavbar(true);
        this.showOnboarding(); // Default view
    }

    hideAllSections() {
        const sections = ['welcome-section', 'login-section', 'register-section', 'dashboard-section'];
        sections.forEach(section => {
            document.getElementById(section).classList.add('d-none');
        });
    }

    updateNavbar(isLoggedIn) {
        document.getElementById('loginBtn').classList.toggle('d-none', isLoggedIn);
        document.getElementById('registerBtn').classList.toggle('d-none', isLoggedIn);
        document.getElementById('logoutBtn').classList.toggle('d-none', !isLoggedIn);
    }

    // Dashboard content methods
    async showOnboarding() {
        const content = `
            <div class="card">
                <div class="card-header">
                    <h4>Welcome to DupeTube! 🎉</h4>
                </div>
                <div class="card-body">
                    <p class="lead">Let's get you started by adding your YouTube channel.</p>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <form id="addChannelForm">
                                <div class="mb-3">
                                    <label for="channelUrl" class="form-label">YouTube Channel URL</label>
                                    <input type="url" class="form-control" id="channelUrl" 
                                           placeholder="https://www.youtube.com/@yourchannel" required>
                                    <div class="form-text">
                                        Enter your YouTube channel URL (supports various formats: @username, /c/channel, /user/username, or /channel/ID)
                                    </div>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    Add Channel
                                </button>
                            </form>
                        </div>
                        <div class="col-md-4">
                            <div class="card bg-light">
                                <div class="card-body">
                                    <h6>What happens next?</h6>
                                    <ul class="small">
                                        <li>We'll fetch your channel information</li>
                                        <li>Index all your existing videos</li>
                                        <li>Suggest content ideas for books and courses</li>
                                        <li>Start generating blog posts</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('dashboard-content').innerHTML = content;
        
        // Setup form handler
        document.getElementById('addChannelForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddChannel();
        });

        // Load existing channels
        this.loadChannels();
    }

    async handleAddChannel() {
        const channelUrl = document.getElementById('channelUrl').value;

        try {
            const response = await fetch(`${this.baseURL}/api/channels/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ channel_url: channelUrl })
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Channel added successfully!', 'success');
                document.getElementById('channelUrl').value = '';
                this.loadChannels();
                
                // Auto-index videos
                this.indexChannelVideos(data.channel.id);
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Failed to add channel. Please try again.', 'danger');
        }
    }

    async loadChannels() {
        try {
            const response = await fetch(`${this.baseURL}/api/channels/`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok && data.channels.length > 0) {
                const channelsHTML = data.channels.map(channel => `
                    <div class="card channel-card mt-3">
                        <div class="card-body">
                            <h5>${channel.title}</h5>
                            <p class="small">${channel.description.substring(0, 100)}...</p>
                            <div class="channel-stats">
                                <div class="row">
                                    <div class="col-4 text-center">
                                        <strong>${channel.subscriber_count.toLocaleString()}</strong><br>
                                        <small>Subscribers</small>
                                    </div>
                                    <div class="col-4 text-center">
                                        <strong>${channel.video_count.toLocaleString()}</strong><br>
                                        <small>Videos</small>
                                    </div>
                                    <div class="col-4 text-center">
                                        <strong>${channel.view_count.toLocaleString()}</strong><br>
                                        <small>Views</small>
                                    </div>
                                </div>
                            </div>
                            <div class="mt-3">
                                <button class="btn btn-light btn-sm" onclick="app.indexChannelVideos(${channel.id})">
                                    Index Videos
                                </button>
                                <button class="btn btn-light btn-sm" onclick="app.syncChannel(${channel.id})">
                                    Sync New Videos
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('');

                const currentContent = document.getElementById('dashboard-content').innerHTML;
                document.getElementById('dashboard-content').innerHTML = currentContent + 
                    `<div class="mt-4"><h5>Your Channels</h5>${channelsHTML}</div>`;
            }
        } catch (error) {
            console.error('Failed to load channels:', error);
        }
    }

    async indexChannelVideos(channelId) {
        try {
            this.showAlert('Indexing videos... This may take a moment.', 'info');
            
            const response = await fetch(`${this.baseURL}/api/channels/${channelId}/index`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert(`Indexed ${data.indexed_count} videos successfully!`, 'success');
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Failed to index videos. Please try again.', 'danger');
        }
    }

    async syncChannel(channelId) {
        try {
            this.showAlert('Syncing channel... Checking for new videos.', 'info');
            
            const response = await fetch(`${this.baseURL}/api/channels/${channelId}/sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                let message = `Synced ${data.new_videos} new videos.`;
                if (data.auto_created_posts > 0) {
                    message += ` ${data.auto_created_posts} blog posts auto-created.`;
                }
                this.showAlert(message, 'success');
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Failed to sync channel. Please try again.', 'danger');
        }
    }

    async showVideos() {
        const content = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4>Your Videos</h4>
                    <button class="btn btn-outline-primary" onclick="app.loadVideos()">
                        Refresh
                    </button>
                </div>
                <div class="card-body">
                    <div id="videos-list">
                        <div class="loading">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p>Loading your videos...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('dashboard-content').innerHTML = content;
        this.loadVideos();
    }

    async loadVideos() {
        try {
            const response = await fetch(`${this.baseURL}/api/videos/`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                const videosHTML = data.videos.map(video => `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card video-card h-100">
                            <img src="${video.thumbnail_url}" class="video-thumbnail" alt="${video.title}">
                            <div class="card-body">
                                <h6 class="card-title">${video.title.substring(0, 50)}...</h6>
                                <p class="card-text small text-muted">
                                    ${video.view_count.toLocaleString()} views • ${new Date(video.published_at).toLocaleDateString()}
                                </p>
                                <div class="d-flex gap-2">
                                    <button class="btn btn-sm btn-outline-primary" 
                                            onclick="app.generateBlogPost(${video.id})">
                                        Generate Blog
                                    </button>
                                    <button class="btn btn-sm btn-outline-secondary" 
                                            onclick="app.viewVideo(${video.id})">
                                        View Details
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');

                document.getElementById('videos-list').innerHTML = 
                    `<div class="row">${videosHTML}</div>`;
            } else {
                document.getElementById('videos-list').innerHTML = 
                    `<div class="alert alert-warning">No videos found. Please add a channel first.</div>`;
            }
        } catch (error) {
            document.getElementById('videos-list').innerHTML = 
                `<div class="alert alert-danger">Failed to load videos. Please try again.</div>`;
        }
    }

    async generateBlogPost(videoId) {
        try {
            this.showAlert('Generating blog post... This may take a moment.', 'info');
            
            const response = await fetch(`${this.baseURL}/api/blog/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.token}`
                },
                body: JSON.stringify({ video_id: videoId })
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Blog post generated successfully!', 'success');
                // Optionally switch to blog posts view
                this.showBlogPosts();
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Failed to generate blog post. Please try again.', 'danger');
        }
    }

    async showBlogPosts() {
        const content = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h4>Blog Posts</h4>
                    <button class="btn btn-outline-primary" onclick="app.loadBlogPosts()">
                        Refresh
                    </button>
                </div>
                <div class="card-body">
                    <div id="blog-posts-list">
                        <div class="loading">
                            <div class="spinner-border" role="status">
                                <span class="visually-hidden">Loading...</span>
                            </div>
                            <p>Loading your blog posts...</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('dashboard-content').innerHTML = content;
        this.loadBlogPosts();
    }

    async loadBlogPosts() {
        try {
            const response = await fetch(`${this.baseURL}/api/blog/posts`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                const postsHTML = data.posts.map(post => `
                    <div class="card blog-post-card mb-3">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <h5>${post.title}</h5>
                                    <p class="text-muted">${post.excerpt}</p>
                                    <small class="text-muted">
                                        Created: ${new Date(post.created_at).toLocaleDateString()}
                                        ${post.published_at ? `• Published: ${new Date(post.published_at).toLocaleDateString()}` : ''}
                                    </small>
                                </div>
                                <div class="d-flex flex-column gap-2">
                                    <span class="badge status-badge bg-${post.status === 'published' ? 'success' : 'warning'}">
                                        ${post.status}
                                    </span>
                                    <div class="btn-group-vertical">
                                        <button class="btn btn-sm btn-outline-primary" 
                                                onclick="app.editBlogPost(${post.id})">
                                            Edit
                                        </button>
                                        ${post.status === 'draft' ? 
                                            `<button class="btn btn-sm btn-success" 
                                                     onclick="app.publishBlogPost(${post.id})">
                                                Publish
                                            </button>` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('');

                document.getElementById('blog-posts-list').innerHTML = postsHTML || 
                    `<div class="alert alert-info">No blog posts yet. Generate some from your videos!</div>`;
            } else {
                document.getElementById('blog-posts-list').innerHTML = 
                    `<div class="alert alert-warning">No blog posts found.</div>`;
            }
        } catch (error) {
            document.getElementById('blog-posts-list').innerHTML = 
                `<div class="alert alert-danger">Failed to load blog posts. Please try again.</div>`;
        }
    }

    async publishBlogPost(postId) {
        try {
            this.showAlert('Publishing to WordPress...', 'info');
            
            const response = await fetch(`${this.baseURL}/api/blog/posts/${postId}/publish`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`
                }
            });

            const data = await response.json();

            if (response.ok) {
                this.showAlert('Blog post published successfully!', 'success');
                this.loadBlogPosts(); // Refresh the list
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Failed to publish blog post. Please try again.', 'danger');
        }
    }

    // Utility method to show alerts
    showAlert(message, type = 'info') {
        const alertContainer = document.getElementById('alert-container');
        const alertId = 'alert-' + Date.now();
        
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" id="${alertId}" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHTML);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.remove();
            }
        }, 5000);
    }
}

// Global functions for onclick handlers
function showLogin() { app.showLogin(); }
function showRegister() { app.showRegister(); }
function showDashboard() { app.showDashboard(); }
function logout() { app.logout(); }
function showOnboarding() { app.showOnboarding(); }
function showChannels() { app.showChannels(); }
function showVideos() { app.showVideos(); }
function showBlogPosts() { app.showBlogPosts(); }
function showSettings() { app.showSettings(); }

// Initialize the app
const app = new DupetubeApp();