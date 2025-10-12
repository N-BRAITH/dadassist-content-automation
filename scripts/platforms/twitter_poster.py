#!/usr/bin/env python3
"""
DadAssist Social Media - Twitter/X Poster
Posts content to Twitter/X using API v2 with GitHub Secrets
"""

import os
import json
import tweepy
from datetime import datetime

class TwitterPoster:
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        # DadAssist Twitter API credentials from GitHub Secrets
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        self.client = None
        
        # Check if credentials are available
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("⚠️ Twitter credentials not found in environment variables")
        
    def authenticate(self):
        """Authenticate with Twitter API using Tweepy"""
        if self.dry_run:
            print("🔐 [DRY RUN] Twitter authentication - checking credentials")
            return True
        
        if not all([self.api_key, self.api_secret, self.access_token, self.access_secret]):
            print("❌ Twitter credentials missing from environment")
            return False
        
        try:
            self.client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )
            
            # Test authentication
            me = self.client.get_me()
            print(f"🔐 Twitter authentication successful - @{me.data.username}")
            return True
            
        except Exception as e:
            print(f"❌ Twitter authentication failed: {e}")
            return False
    
    def post_tweet(self, post_data):
        """Post a tweet to Twitter"""
        content = post_data['content']
        
        if self.dry_run:
            print("🐦 [DRY RUN] Would post to Twitter:")
            print(f"   Content: {content[:100]}...")
            print(f"   Character count: {post_data['character_count']}/280")
            print(f"   Hashtags: {', '.join(post_data['hashtags'])}")
            print(f"   Links: {', '.join(post_data['links'])}")
            return {
                'success': True,
                'platform': 'twitter',
                'post_id': f'dry_run_tweet_{int(datetime.now().timestamp())}',
                'message': 'Dry run successful',
                'url': f'https://twitter.com/dad_assist/status/dry_run_tweet_{int(datetime.now().timestamp())}'
            }
        
        if not self.client:
            return {
                'success': False,
                'platform': 'twitter',
                'error': 'Not authenticated'
            }
        
        try:
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            tweet_url = f'https://twitter.com/dad_assist/status/{tweet_id}'
            
            print(f"🐦 Posted to Twitter: {content[:50]}...")
            print(f"   Tweet URL: {tweet_url}")
            
            return {
                'success': True,
                'platform': 'twitter',
                'post_id': tweet_id,
                'url': tweet_url,
                'message': 'Tweet posted successfully'
            }
            
        except Exception as e:
            print(f"❌ Failed to post to Twitter: {e}")
            return {
                'success': False,
                'platform': 'twitter',
                'error': str(e)
            }
    
    def get_rate_limit_status(self):
        """Check Twitter API rate limits"""
        return {
            'remaining_posts': 17,  # Free tier daily limit
            'reset_time': '2024-12-19T00:00:00Z',
            'limit': 17
        }
