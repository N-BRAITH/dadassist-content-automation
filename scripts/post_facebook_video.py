#!/usr/bin/env python3
"""Post video to Facebook page."""

import os
import sys
import requests
import tempfile

def download_video(s3_url):
    """Download video from S3 to temp file."""
    print(f"⬇️  Downloading video from S3...")
    
    response = requests.get(s3_url, stream=True)
    response.raise_for_status()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    
    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)
    
    temp_file.close()
    print(f"✅ Downloaded to {temp_file.name}")
    return temp_file.name

def post_video_to_facebook(video_path, title, description):
    """Post video to Facebook page."""
    
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
    
    if not all([page_id, access_token]):
        print("❌ Missing Facebook credentials")
        sys.exit(1)
    
    print(f"📘 Uploading video to Facebook...")
    print(f"   Title: {title}")
    print(f"   Description: {description[:100]}...")
    
    url = f"https://graph-video.facebook.com/v18.0/{page_id}/videos"
    
    with open(video_path, 'rb') as video_file:
        files = {'file': video_file}
        data = {
            'title': title,
            'description': description,
            'access_token': access_token
        }
        
        response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        video_id = result.get('id')
        video_url = f"https://www.facebook.com/{page_id}/videos/{video_id}"
        
        print(f"✅ Video posted to Facebook")
        print(f"🔗 Video ID: {video_id}")
        print(f"🔗 URL: {video_url}")
        
        # Save outputs
        with open('facebook_video_id.txt', 'w') as f:
            f.write(video_id)
        with open('facebook_video_url.txt', 'w') as f:
            f.write(video_url)
        
        return video_id, video_url
    else:
        error = response.json().get('error', {})
        print(f"❌ Failed to post video: {error.get('message', 'Unknown error')}")
        sys.exit(1)

def main():
    """Main function."""
    
    # Read inputs
    with open('s3_url.txt', 'r') as f:
        s3_url = f.read().strip()
    
    with open('video_title.txt', 'r') as f:
        title = f.read().strip()
    
    # Create description
    description = f"{title}\n\nVisit dadassist.com.au for more information and support for Australian fathers."
    
    # Download video
    video_path = download_video(s3_url)
    
    try:
        # Post to Facebook
        post_video_to_facebook(video_path, title, description)
    finally:
        # Clean up temp file
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"🗑️  Cleaned up temp file")

if __name__ == '__main__':
    main()
