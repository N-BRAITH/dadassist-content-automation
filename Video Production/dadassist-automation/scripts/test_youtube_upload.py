#!/usr/bin/env python3
"""Test YouTube upload with existing video."""

import os
import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Your credentials from the script output
CLIENT_ID = "1022710674456-s3bed4vuceqrbekjbuuracm0fqsdvcrs.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REFRESH_TOKEN = "1//0gfxJ7GPJP2NACgYIARAAGBASNwF-L9IrQARIhHI2I4YpTvI_qDp8PLk6EWVSvvQSdWsY8YC2f5Og8de9oy0VAxE-gW7X66IIxpY"

def upload_test_video(video_path):
    """Upload a test video to YouTube."""
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"📺 Testing YouTube Upload")
    print(f"📁 Video: {video_path}")
    print()
    
    # Create credentials
    credentials = Credentials(
        None,
        refresh_token=REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    # Build YouTube client
    youtube = build('youtube', 'v3', credentials=credentials)
    
    # Video metadata
    body = {
        'snippet': {
            'title': 'DadAssist Test Video - ' + os.path.basename(video_path),
            'description': 'Test upload from DadAssist automation system.',
            'tags': ['DadAssist', 'Test'],
            'categoryId': '27'  # Education
        },
        'status': {
            'privacyStatus': 'unlisted',  # unlisted so it's not public
            'selfDeclaredMadeForKids': False
        }
    }
    
    print("📤 Uploading to YouTube...")
    
    # Upload
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype='video/mp4')
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = request.execute()
    
    video_id = response['id']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print()
    print("✅ Upload successful!")
    print(f"🆔 Video ID: {video_id}")
    print(f"🔗 URL: {video_url}")
    print(f"👁️  Privacy: Unlisted (only people with link can see it)")
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 test_youtube_upload.py <path-to-video.mp4>")
        print()
        print("Example:")
        print("  python3 test_youtube_upload.py ~/Downloads/test_video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    upload_test_video(video_path)
