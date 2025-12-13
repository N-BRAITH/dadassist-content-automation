#!/usr/bin/env python3
"""Upload video to YouTube."""

import os
import sys
import json
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def get_youtube_client():
    """Create YouTube API client from environment variables."""
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ Missing YouTube credentials in environment variables")
        sys.exit(1)
    
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    return build('youtube', 'v3', credentials=credentials)

def upload_to_youtube(s3_url, title, category):
    """Upload video to YouTube using S3 URL."""
    print(f"📺 Preparing YouTube upload")
    print(f"📄 Title: {title}")
    print(f"🏷️  Category: {category}")
    
    youtube = get_youtube_client()
    
    # Generate description
    description = f"""Learn about {title.lower()} for Australian fathers.

This video is brought to you by DadAssist - supporting fathers through separation and family law matters.

🌐 Visit: https://www.dadassist.com.au
📱 Instagram: @dadassist
📘 Facebook: /dadassist

Category: {category}

#DadAssist #AustralianFathers #FamilyLaw #Parenting"""
    
    # Video metadata
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['DadAssist', 'Australian Fathers', 'Family Law', 'Parenting', category],
            'categoryId': '27'  # Education category
        },
        'status': {
            'privacyStatus': 'public',  # or 'unlisted' or 'private'
            'selfDeclaredMadeForKids': False
        }
    }
    
    # Download video from S3 temporarily
    print(f"⬇️  Downloading video from S3...")
    import requests
    response = requests.get(s3_url, stream=True, timeout=300)
    response.raise_for_status()
    
    temp_file = '/tmp/video.mp4'
    with open(temp_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"📤 Uploading to YouTube...")
    
    # Upload video
    media = MediaFileUpload(temp_file, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = request.execute()
    
    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"✅ Upload complete!")
    print(f"🆔 Video ID: {video_id}")
    print(f"🔗 URL: {video_url}")
    
    # Save video ID
    with open('youtube_id.txt', 'w') as f:
        f.write(video_id)
    
    # Clean up temp file
    os.remove(temp_file)
    
    return video_id, video_url

def update_processed_urls(article_url, youtube_id, category):
    """Update processed_urls.json with new entry."""
    print(f"💾 Updating processed_urls.json")
    
    try:
        with open('processed_urls.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []
    
    # Add new entry
    data.append({
        'url': article_url,
        'processed_date': datetime.now().isoformat(),
        'youtube_video_id': youtube_id,
        'category': category
    })
    
    # Save back
    with open('processed_urls.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Updated processed_urls.json ({len(data)} total videos)")

if __name__ == "__main__":
    # Read inputs
    try:
        with open('s3_url.txt', 'r') as f:
            s3_url = f.read().strip()
        with open('video_title.txt', 'r') as f:
            title = f.read().strip()
        with open('video_category.txt', 'r') as f:
            category = f.read().strip()
        with open('selected_url.txt', 'r') as f:
            article_url = f.read().strip()
    except FileNotFoundError as e:
        print(f"❌ Missing input file: {e}")
        sys.exit(1)
    
    # Upload to YouTube
    video_id, video_url = upload_to_youtube(s3_url, title, category)
    
    # Update processed URLs
    update_processed_urls(article_url, video_id, category)
    
    print(f"🎉 All done!")
