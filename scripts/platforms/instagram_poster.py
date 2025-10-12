#!/usr/bin/env python3
"""
DadAssist Social Media - Instagram Poster
Posts content to Instagram using Facebook Graph API with GitHub Secrets
"""

import os
import json
import requests
from datetime import datetime

class InstagramPoster:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        # DadAssist Instagram API credentials from GitHub Secrets (separate token)
        self.instagram_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID')
        
        # Check if credentials are available
        if not all([self.instagram_access_token, self.instagram_account_id]):
            print("⚠️ Instagram credentials not found in environment variables")
        
    def authenticate(self):
        """Authenticate with Instagram API via Facebook"""
        if self.dry_run:
            print("🔐 [DRY RUN] Instagram authentication - checking credentials")
            return True
        
        if not all([self.instagram_access_token, self.instagram_account_id]):
            print("❌ Instagram credentials missing from environment")
            return False
        
        try:
            # Test authentication by getting Instagram account info
            response = requests.get(
                f'https://graph.facebook.com/{self.instagram_account_id}',
                params={
                    'fields': 'username',
                    'access_token': self.instagram_access_token
                }
            )
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"🔐 Instagram authentication successful - @{account_data.get('username', 'dadassist')}")
                return True
            else:
                print(f"❌ Instagram authentication failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Instagram authentication failed: {e}")
            return False
    
    def create_image_post(self, post_data, image_url=None):
        """Create Instagram image post"""
        content = post_data['content']
        
        # Default professional image if none provided (reliable stock photo)
        if not image_url:
            image_url = "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1080&h=1080&fit=crop&crop=center"
        
        if self.dry_run:
            print("📷 [DRY RUN] Would post to Instagram:")
            print(f"   Caption: {content[:100]}...")
            print(f"   Character count: {post_data['character_count']}")
            print(f"   Hashtags: {', '.join(post_data['hashtags'])}")
            print(f"   Image: {image_url}")
            return {
                'success': True,
                'platform': 'instagram',
                'post_id': f'dry_run_ig_{int(datetime.now().timestamp())}',
                'message': 'Dry run successful',
                'url': f'https://instagram.com/p/dry_run_ig_{int(datetime.now().timestamp())}'
            }
        
        if not all([self.instagram_access_token, self.instagram_account_id]):
            return {
                'success': False,
                'platform': 'instagram',
                'error': 'Missing credentials'
            }
        
        try:
            # Step 1: Create media container
            media_response = requests.post(
                f'https://graph.facebook.com/{self.instagram_account_id}/media',
                data={
                    'image_url': image_url,
                    'caption': content,
                    'access_token': self.instagram_access_token
                }
            )
            
            if media_response.status_code != 200:
                error_msg = media_response.json().get('error', {}).get('message', 'Media creation failed')
                print(f"❌ Failed to create Instagram media: {error_msg}")
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': error_msg
                }
            
            creation_id = media_response.json().get('id')
            
            # Step 2: Publish media
            publish_response = requests.post(
                f'https://graph.facebook.com/{self.instagram_account_id}/media_publish',
                data={
                    'creation_id': creation_id,
                    'access_token': self.instagram_access_token
                }
            )
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id', 'unknown')
                post_url = f'https://instagram.com/p/{post_id}'
                
                print(f"📷 Posted to Instagram: {content[:50]}...")
                print(f"   Post URL: {post_url}")
                
                return {
                    'success': True,
                    'platform': 'instagram',
                    'post_id': post_id,
                    'url': post_url,
                    'message': 'Instagram post successful'
                }
            else:
                error_msg = publish_response.json().get('error', {}).get('message', 'Publishing failed')
                print(f"❌ Failed to publish Instagram post: {error_msg}")
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': error_msg
                }
                
        except Exception as e:
            print(f"❌ Failed to post to Instagram: {e}")
            return {
                'success': False,
                'platform': 'instagram',
                'error': str(e)
            }
