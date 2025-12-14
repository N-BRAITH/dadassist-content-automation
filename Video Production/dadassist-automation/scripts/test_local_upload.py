#!/usr/bin/env python3
"""Test YouTube upload locally with existing S3 video."""

import sys
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Your YouTube credentials
CLIENT_ID = "1022710674456-s3bed4vuceqrbekjbuuracm0fqsdvcrs.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//0gfxJ7GPJP2NACgYIARAAGBASNwF-L9IrQARIhHI2I4YpTvI_qDp8PLk6EWVSvvQSdWsY8YC2f5Og8de9oy0VAxE-gW7X66IIxpY"

# S3 video URL
S3_URL = "https://dadassist-video-work.s3.ap-southeast-2.amazonaws.com/39c03fbc-8441-46e8-a05b-9c1ba54dfff5/final_video_captioned.mp4"

def test_upload():
    """Test uploading video from S3 to YouTube."""
    
    print("📺 YouTube Upload Test")
    print("=" * 50)
    print(f"📦 S3 URL: {S3_URL}")
    print()
    
    # Step 1: Download video from S3
    print("⬇️  Step 1: Downloading video from S3...")
    response = requests.get(S3_URL, stream=True, timeout=300)
    response.raise_for_status()
    
    temp_file = '/tmp/test_video.mp4'
    with open(temp_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print("✅ Downloaded successfully")
    print()
    
    # Step 2: Create YouTube client
    print("🔐 Step 2: Authenticating with YouTube...")
    credentials = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    youtube = build('youtube', 'v3', credentials=credentials)
    print("✅ Authenticated")
    print()
    
    # Step 3: Upload to YouTube
    print("📤 Step 3: Uploading to YouTube...")
    
    body = {
        'snippet': {
            'title': 'DadAssist Test Upload - Mental Health',
            'description': 'Test upload from automation system.',
            'tags': ['DadAssist', 'Test'],
            'categoryId': '27'
        },
        'status': {
            'privacyStatus': 'unlisted',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(temp_file, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = request.execute()
    
    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print("✅ Upload complete!")
    print()
    print("=" * 50)
    print("Results:")
    print("=" * 50)
    print(f"🆔 Video ID: {video_id}")
    print(f"🔗 URL: {video_url}")
    print(f"👁️  Privacy: Unlisted")
    print()

if __name__ == "__main__":
    try:
        test_upload()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
