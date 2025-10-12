#!/usr/bin/env python3
"""
DadAssist Social Media - Facebook Poster
Posts content to Facebook page using Graph API with GitHub Secrets
"""

import os
import json
import requests
from datetime import datetime

class FacebookPoster:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        # DadAssist Facebook API credentials from GitHub Secrets
        self.page_access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
        self.page_id = os.getenv('FACEBOOK_PAGE_ID')
        
        # Check if credentials are available
        if not all([self.page_access_token, self.page_id]):
            print("⚠️ Facebook credentials not found in environment variables")
        
    def authenticate(self):
        """Authenticate with Facebook API"""
        if self.dry_run:
            print("🔐 [DRY RUN] Facebook authentication - checking credentials")
            return True
        
        if not all([self.page_access_token, self.page_id]):
            print("❌ Facebook credentials missing from environment")
            return False
        
        try:
            # Test authentication by getting page info
            response = requests.get(
                f'https://graph.facebook.com/{self.page_id}',
                params={'access_token': self.page_access_token}
            )
            
            if response.status_code == 200:
                page_data = response.json()
                print(f"🔐 Facebook authentication successful - {page_data.get('name', 'DadAssist')}")
                return True
            else:
                print(f"❌ Facebook authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Facebook authentication failed: {e}")
            return False
    
    def post_to_page(self, post_data):
        """Post content to Facebook page"""
        content = post_data['content']
        
        if self.dry_run:
            print("📘 [DRY RUN] Would post to Facebook:")
            print(f"   Content: {content[:100]}...")
            print(f"   Character count: {post_data['character_count']}")
            print(f"   Hashtags: {', '.join(post_data['hashtags'])}")
            print(f"   Links: {', '.join(post_data['links'])}")
            return {
                'success': True,
                'platform': 'facebook',
                'post_id': f'dry_run_fb_{int(datetime.now().timestamp())}',
                'message': 'Dry run successful',
                'url': f'https://facebook.com/DadAssist/posts/dry_run_fb_{int(datetime.now().timestamp())}'
            }
        
        if not all([self.page_access_token, self.page_id]):
            return {
                'success': False,
                'platform': 'facebook',
                'error': 'Missing credentials'
            }
        
        try:
            response = requests.post(
                f'https://graph.facebook.com/{self.page_id}/feed',
                data={
                    'message': content,
                    'access_token': self.page_access_token
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get('id', 'unknown')
                post_url = f'https://facebook.com/DadAssist/posts/{post_id.split("_")[1] if "_" in post_id else post_id}'
                
                print(f"📘 Posted to Facebook: {content[:50]}...")
                print(f"   Post URL: {post_url}")
                
                return {
                    'success': True,
                    'platform': 'facebook',
                    'post_id': post_id,
                    'url': post_url,
                    'message': 'Facebook post successful'
                }
            else:
                error_msg = response.json().get('error', {}).get('message', 'Unknown error')
                print(f"❌ Failed to post to Facebook: {error_msg}")
                return {
                    'success': False,
                    'platform': 'facebook',
                    'error': error_msg
                }
                
        except Exception as e:
            print(f"❌ Failed to post to Facebook: {e}")
            return {
                'success': False,
                'platform': 'facebook',
                'error': str(e)
            }
