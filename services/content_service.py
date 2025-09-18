import os
import json
import requests
from youtube_transcript_api import YouTubeTranscriptApi
import openai

class ContentService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def get_video_transcript(self, video_id):
        """Get transcript for a YouTube video"""
        try:
            # Try to get transcript in English first
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Look for English transcript
            try:
                transcript = transcript_list.find_transcript(['en'])
                transcript_data = transcript.fetch()
            except:
                # If no English transcript, try auto-generated
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    transcript_data = transcript.fetch()
                except:
                    # If still no transcript, try the first available
                    transcript = next(iter(transcript_list))
                    transcript_data = transcript.fetch()
            
            # Combine all transcript segments
            full_transcript = ' '.join([entry['text'] for entry in transcript_data])
            return full_transcript
            
        except Exception as e:
            print(f"Error getting transcript for video {video_id}: {e}")
            return None
    
    def generate_summary(self, transcript, title):
        """Generate summary and key points from video transcript using OpenAI"""
        if not self.openai_api_key or not transcript:
            return self._generate_simple_summary(transcript, title)
        
        try:
            prompt = f"""
            Based on the following YouTube video transcript with title "{title}", please:
            1. Create a comprehensive summary (3-4 paragraphs)
            2. Extract 5-7 key points from the content
            
            Transcript:
            {transcript[:4000]}  # Limit transcript length for API
            
            Please format your response as JSON with 'summary' and 'key_points' fields.
            The key_points should be an array of strings.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes video content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'summary': result.get('summary', ''),
                'key_points': json.dumps(result.get('key_points', []))
            }
            
        except Exception as e:
            print(f"Error generating AI summary: {e}")
            return self._generate_simple_summary(transcript, title)
    
    def _generate_simple_summary(self, transcript, title):
        """Generate a simple summary without AI"""
        if not transcript:
            return {
                'summary': f"This video titled '{title}' covers various topics. No transcript available for detailed summary.",
                'key_points': json.dumps([])
            }
        
        # Simple summary - first 300 characters + ellipsis
        words = transcript.split()
        summary_words = words[:50]  # First 50 words
        summary = ' '.join(summary_words)
        if len(words) > 50:
            summary += "..."
        
        # Simple key points - split transcript into chunks
        key_points = []
        chunks = [words[i:i+20] for i in range(0, min(len(words), 100), 20)]
        for chunk in chunks[:5]:  # Max 5 key points
            point = ' '.join(chunk)
            if len(point) > 10:  # Only add if substantial
                key_points.append(point[:100] + "..." if len(point) > 100 else point)
        
        return {
            'summary': summary,
            'key_points': json.dumps(key_points)
        }
    
    def generate_blog_content(self, video, user_preferences=None):
        """Generate blog content from video data"""
        try:
            if not self.openai_api_key:
                return self._generate_simple_blog_content(video)
            
            # Prepare context
            transcript = video.transcript if video.transcript else ""
            summary = video.summary if video.summary else ""
            title = video.title
            description = video.description
            
            prompt = f"""
            Create a comprehensive blog post based on this YouTube video:
            
            Title: {title}
            Description: {description}
            Summary: {summary}
            Transcript (excerpt): {transcript[:2000]}
            
            Please create:
            1. An engaging blog post title (may be different from video title)
            2. A compelling introduction paragraph
            3. Well-structured main content with subheadings
            4. A conclusion with call-to-action
            5. A short excerpt for social media
            
            Format as JSON with fields: title, content, excerpt
            Make the content SEO-friendly and engaging for blog readers.
            Include references to the original video where appropriate.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert content writer who creates engaging blog posts from video content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error generating blog content: {e}")
            return self._generate_simple_blog_content(video)
    
    def _generate_simple_blog_content(self, video):
        """Generate simple blog content without AI"""
        title = video.title
        summary = video.summary if video.summary else "Content summary not available."
        
        content = f"""
        <h2>{title}</h2>
        
        <p>This blog post is based on a YouTube video titled "{title}".</p>
        
        <h3>Overview</h3>
        <p>{summary}</p>
        
        <h3>Key Takeaways</h3>
        """
        
        # Add key points if available
        if video.key_points:
            try:
                key_points = json.loads(video.key_points)
                content += "<ul>"
                for point in key_points:
                    content += f"<li>{point}</li>"
                content += "</ul>"
            except:
                pass
        
        content += f"""
        <h3>Watch the Original Video</h3>
        <p>You can watch the full video on YouTube: <a href="https://youtube.com/watch?v={video.video_id}" target="_blank">{title}</a></p>
        
        <p>What are your thoughts on this topic? Let me know in the comments below!</p>
        """
        
        excerpt = summary[:200] + "..." if len(summary) > 200 else summary
        
        return {
            'title': title,
            'content': content,
            'excerpt': excerpt
        }
    
    def generate_content_suggestions(self, video):
        """Generate suggestions for books, courses, and additional content"""
        try:
            if not self.openai_api_key:
                return self._generate_simple_suggestions(video)
            
            context = f"""
            Video: {video.title}
            Description: {video.description}
            Summary: {video.summary if video.summary else 'No summary available'}
            """
            
            prompt = f"""
            Based on this video content, suggest:
            1. 3-5 related book topics that could be created from this content
            2. 2-3 online course concepts that could expand on these topics
            3. 3-5 related blog post ideas
            
            Video context:
            {context}
            
            Format as JSON with fields: book_suggestions, course_suggestions, blog_post_ideas
            Each should be an array of objects with 'title' and 'description' fields.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content strategist who creates comprehensive content plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error generating content suggestions: {e}")
            return self._generate_simple_suggestions(video)
    
    def _generate_simple_suggestions(self, video):
        """Generate simple content suggestions without AI"""
        title = video.title
        
        return {
            'book_suggestions': [
                {
                    'title': f'The Complete Guide to {title}',
                    'description': f'A comprehensive book expanding on the topics covered in "{title}"'
                },
                {
                    'title': f'Mastering {title}: Advanced Strategies',
                    'description': f'Advanced techniques and strategies based on "{title}"'
                }
            ],
            'course_suggestions': [
                {
                    'title': f'{title}: Complete Course',
                    'description': f'A step-by-step online course based on the concepts from "{title}"'
                }
            ],
            'blog_post_ideas': [
                {
                    'title': f'5 Key Takeaways from "{title}"',
                    'description': 'Break down the main points into digestible insights'
                },
                {
                    'title': f'How to Apply Lessons from "{title}"',
                    'description': 'Practical application guide for the video content'
                },
                {
                    'title': f'FAQ: Common Questions About "{title}"',
                    'description': 'Address frequently asked questions related to the video topic'
                }
            ]
        }