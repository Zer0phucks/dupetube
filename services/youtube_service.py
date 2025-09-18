import os
import json
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class YouTubeService:
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def get_channel_info(self, channel_id):
        """Get channel information from YouTube API"""
        try:
            # Try different channel ID formats
            channel_info = None
            
            # First try as channel ID
            try:
                request = self.youtube.channels().list(
                    part='snippet,statistics',
                    id=channel_id
                )
                response = request.execute()
                if response['items']:
                    channel_info = response['items'][0]
            except:
                pass
            
            # If not found, try as username
            if not channel_info:
                try:
                    request = self.youtube.channels().list(
                        part='snippet,statistics',
                        forUsername=channel_id
                    )
                    response = request.execute()
                    if response['items']:
                        channel_info = response['items'][0]
                except:
                    pass
            
            # If still not found, try searching
            if not channel_info:
                try:
                    search_request = self.youtube.search().list(
                        part='snippet',
                        q=channel_id,
                        type='channel',
                        maxResults=1
                    )
                    search_response = search_request.execute()
                    
                    if search_response['items']:
                        found_channel_id = search_response['items'][0]['snippet']['channelId']
                        request = self.youtube.channels().list(
                            part='snippet,statistics',
                            id=found_channel_id
                        )
                        response = request.execute()
                        if response['items']:
                            channel_info = response['items'][0]
                except:
                    pass
            
            if not channel_info:
                return None
            
            snippet = channel_info['snippet']
            statistics = channel_info.get('statistics', {})
            
            return {
                'channel_id': channel_info['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'subscriber_count': int(statistics.get('subscriberCount', 0)),
                'video_count': int(statistics.get('videoCount', 0)),
                'view_count': int(statistics.get('viewCount', 0)),
                'thumbnail_url': snippet.get('thumbnails', {}).get('default', {}).get('url', '')
            }
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None
    
    def get_channel_videos(self, channel_id, limit=50):
        """Get videos from a channel"""
        try:
            videos = []
            next_page_token = None
            
            while len(videos) < limit:
                # Get uploads playlist ID
                channel_request = self.youtube.channels().list(
                    part='contentDetails',
                    id=channel_id
                )
                channel_response = channel_request.execute()
                
                if not channel_response['items']:
                    break
                
                uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
                
                # Get videos from uploads playlist
                playlist_request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=uploads_playlist_id,
                    maxResults=min(50, limit - len(videos)),
                    pageToken=next_page_token
                )
                playlist_response = playlist_request.execute()
                
                video_ids = []
                for item in playlist_response['items']:
                    video_ids.append(item['snippet']['resourceId']['videoId'])
                
                # Get detailed video information
                if video_ids:
                    videos_request = self.youtube.videos().list(
                        part='snippet,statistics,contentDetails',
                        id=','.join(video_ids)
                    )
                    videos_response = videos_request.execute()
                    
                    for video in videos_response['items']:
                        video_data = self._parse_video_data(video)
                        if video_data:
                            videos.append(video_data)
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return videos[:limit]
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return []
        except Exception as e:
            print(f"Error getting channel videos: {e}")
            return []
    
    def get_video_info(self, video_id):
        """Get detailed information about a specific video"""
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response['items']:
                return None
            
            return self._parse_video_data(response['items'][0])
            
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
    
    def _parse_video_data(self, video):
        """Parse video data from YouTube API response"""
        try:
            snippet = video['snippet']
            statistics = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            
            # Parse published date
            published_at = None
            if snippet.get('publishedAt'):
                published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
            
            # Parse tags
            tags = json.dumps(snippet.get('tags', []))
            
            return {
                'video_id': video['id'],
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'published_at': published_at,
                'tags': tags,
                'category_id': snippet.get('categoryId', '')
            }
            
        except Exception as e:
            print(f"Error parsing video data: {e}")
            return None