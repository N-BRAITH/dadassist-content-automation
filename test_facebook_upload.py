#!/usr/bin/env python3
"""Test Facebook video upload locally."""

import os
import sys
import requests
import tempfile

# Use existing video from S3
S3_URL = "https://dadassist-video-work.s3.ap-southeast-2.amazonaws.com/ffefd82a-c6a1-481a-b411-3b812108c8f2/final_video_captioned.mp4"
VIDEO_TITLE = "Property Settlement Guide for Divorce - DadAssist"

# Facebook credentials (will prompt if not in env)
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID') or input("Enter Facebook Page ID: ")
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN') or input("Enter Facebook Access Token: ")

def download_video(s3_url):
    """Download video from S3 to temp file."""
    print(f"⬇️  Downloading video from S3...")
    print(f"   URL: {s3_url}")
    
    response = requests.get(s3_url, stream=True)
    response.raise_for_status()
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    
    total_size = 0
    for chunk in response.iter_content(chunk_size=8192):
        temp_file.write(chunk)
        total_size += len(chunk)
    
    temp_file.close()
    print(f"✅ Downloaded {total_size / 1024 / 1024:.1f} MB to {temp_file.name}")
    return temp_file.name

def test_facebook_auth():
    """Test Facebook authentication."""
    print(f"\n🔐 Testing Facebook authentication...")
    
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}"
    params = {'access_token': FACEBOOK_ACCESS_TOKEN}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        page_data = response.json()
        print(f"✅ Authenticated as: {page_data.get('name', 'Unknown')}")
        return True
    else:
        print(f"❌ Authentication failed: {response.json()}")
        return False

def post_video_to_facebook(video_path, title):
    """Post video to Facebook page."""
    
    print(f"\n📘 Uploading video to Facebook...")
    print(f"   Title: {title}")
    print(f"   Page ID: {FACEBOOK_PAGE_ID}")
    
    url = f"https://graph-video.facebook.com/v18.0/{FACEBOOK_PAGE_ID}/videos"
    
    description = f"{title}\n\nVisit dadassist.com.au for more information and support for Australian fathers."
    
    print(f"   Opening video file...")
    with open(video_path, 'rb') as video_file:
        files = {'file': video_file}
        data = {
            'title': title,
            'description': description,
            'access_token': FACEBOOK_ACCESS_TOKEN
        }
        
        print(f"   Uploading... (this may take a minute)")
        response = requests.post(url, files=files, data=data, timeout=300)
    
    print(f"\n📊 Response status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        video_id = result.get('id')
        video_url = f"https://www.facebook.com/{FACEBOOK_PAGE_ID}/videos/{video_id}"
        
        print(f"\n✅ Video posted to Facebook!")
        print(f"🔗 Video ID: {video_id}")
        print(f"🔗 URL: {video_url}")
        
        return True
    else:
        error = response.json().get('error', {})
        print(f"\n❌ Failed to post video")
        print(f"   Error type: {error.get('type', 'Unknown')}")
        print(f"   Error message: {error.get('message', 'Unknown error')}")
        print(f"   Error code: {error.get('code', 'N/A')}")
        
        if 'permissions' in error.get('message', '').lower():
            print(f"\n⚠️  This looks like a permissions issue.")
            print(f"   The access token needs 'pages_manage_posts' permission.")
        
        return False

def main():
    """Main function."""
    
    print("="*60)
    print("📘 Facebook Video Upload Test")
    print("="*60)
    
    # Test auth first
    if not test_facebook_auth():
        print("\n❌ Authentication failed. Check your credentials.")
        sys.exit(1)
    
    # Download video
    video_path = download_video(S3_URL)
    
    try:
        # Post to Facebook
        success = post_video_to_facebook(video_path, VIDEO_TITLE)
        
        if success:
            print("\n" + "="*60)
            print("✅ Test completed successfully!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ Test failed - see error above")
            print("="*60)
            sys.exit(1)
            
    finally:
        # Clean up temp file
        if os.path.exists(video_path):
            os.remove(video_path)
            print(f"\n🗑️  Cleaned up temp file")

if __name__ == '__main__':
    main()
