#!/usr/bin/env python3
"""Call API Gateway to generate video."""

import requests
import time
import sys

API_URL = "https://l5a6iab630.execute-api.ap-southeast-2.amazonaws.com/prod/start-video"

def call_api_with_progress(article_url):
    """Call API and show progress while waiting."""
    print(f"🚀 Starting video generation")
    print(f"📝 Article: {article_url}")
    print(f"🌐 API: {API_URL}")
    
    start_time = time.time()
    
    try:
        # Make API call with 10 minute timeout
        print("⏳ Calling API (this will take 3-5 minutes)...")
        
        response = requests.post(
            API_URL,
            json={"article_url": article_url},
            timeout=600
        )
        
        elapsed = int(time.time() - start_time)
        print(f"⏱️  Response received after {elapsed} seconds")
        
        if response.status_code != 200:
            print(f"❌ API returned status {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)
        
        result = response.json()
        
        if result.get('status') != 'success':
            print(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
        
        # Extract results
        s3_url = result['s3_url']
        title = result['title']
        category = result['category']
        execution_id = result['execution_id']
        
        print(f"✅ Video ready!")
        print(f"📦 S3 URL: {s3_url}")
        print(f"📄 Title: {title}")
        print(f"🏷️  Category: {category}")
        print(f"🆔 Execution ID: {execution_id}")
        
        # Save to files for next step
        with open('s3_url.txt', 'w') as f:
            f.write(s3_url)
        with open('video_title.txt', 'w') as f:
            f.write(title)
        with open('video_category.txt', 'w') as f:
            f.write(category)
        with open('execution_id.txt', 'w') as f:
            f.write(execution_id)
        
        return result
        
    except requests.Timeout:
        print("❌ ERROR: API timeout after 10 minutes")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"❌ ERROR: Request failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Read selected URL
    try:
        with open('selected_url.txt', 'r') as f:
            url = f.read().strip()
    except FileNotFoundError:
        print("❌ selected_url.txt not found")
        sys.exit(1)
    
    call_api_with_progress(url)
