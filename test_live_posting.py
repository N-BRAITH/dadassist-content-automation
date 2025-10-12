#!/usr/bin/env python3
"""
DadAssist Social Media - Local Live Test
Posts child support article to live social media with actual credentials
"""

import sys
import os
sys.path.append('scripts')

from post_templates import generate_all_posts
import tweepy
import requests
from datetime import datetime

# Your actual working credentials
TWITTER_CREDENTIALS = {
    'api_key': 'LgBPdKYGrVKd4um7MESfnBpBf',
    'api_secret': 'k8cjRytwRf8BHWqQ67INqL2NAJr2shVpB8TY1GsoeEp0mDRruv',
    'access_token': '1976802841374474242-gAdhhBMATIk1bG85m0HWYJGkRlmPFr',
    'access_secret': 'z9a6kthBjMmsebi9ivUeE8tXBeitgnAlGMDOaSuFwZm1r'
}

FACEBOOK_CREDENTIALS = {
    'access_token': 'EAFgDFHIYZBS0BPlMz33Qq0UqvQnuJklmso0ApkypyGEXtD0fglNSVSSUPsuYT8kMhH4Xor9h5KJrY4p6bZADvlW5BzrB6pF7xXcaZBiocymaWotgLml5pSLNPc0M9SJeOsUYGUNT8QxZCdUNCWLI8KLMMqwSw08jqxf9jc3kTgbgvZCj5aNyGILo8WTdoV8KP0Rk52ucB0oKWQj6nME6aG9qN4pD0Ay9wWtZCMpgab',
    'page_id': '737106112829383',
    'instagram_id': '17841477240606238'
}

def post_to_twitter(post_data):
    """Post to Twitter with actual credentials"""
    try:
        client = tweepy.Client(
            consumer_key=TWITTER_CREDENTIALS['api_key'],
            consumer_secret=TWITTER_CREDENTIALS['api_secret'],
            access_token=TWITTER_CREDENTIALS['access_token'],
            access_token_secret=TWITTER_CREDENTIALS['access_secret']
        )
        
        response = client.create_tweet(text=post_data['content'])
        tweet_id = response.data['id']
        tweet_url = f'https://twitter.com/dad_assist/status/{tweet_id}'
        
        print(f"🐦 ✅ Twitter: {tweet_url}")
        return {'success': True, 'platform': 'twitter', 'url': tweet_url, 'post_id': tweet_id}
        
    except Exception as e:
        print(f"🐦 ❌ Twitter failed: {e}")
        return {'success': False, 'platform': 'twitter', 'error': str(e)}

def post_to_facebook(post_data):
    """Post to Facebook with actual credentials"""
    try:
        response = requests.post(
            f"https://graph.facebook.com/{FACEBOOK_CREDENTIALS['page_id']}/feed",
            data={
                'message': post_data['content'],
                'access_token': FACEBOOK_CREDENTIALS['access_token']
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id', 'unknown')
            post_url = f'https://facebook.com/DadAssist/posts/{post_id.split("_")[1] if "_" in post_id else post_id}'
            
            print(f"📘 ✅ Facebook: {post_url}")
            return {'success': True, 'platform': 'facebook', 'url': post_url, 'post_id': post_id}
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"📘 ❌ Facebook failed: {error}")
            return {'success': False, 'platform': 'facebook', 'error': error}
            
    except Exception as e:
        print(f"📘 ❌ Facebook failed: {e}")
        return {'success': False, 'platform': 'facebook', 'error': str(e)}

def post_to_instagram(post_data):
    """Post to Instagram with actual credentials"""
    try:
        # Default DadAssist image
        image_url = "https://dadassist.com.au/images/dadassist-logo.jpg"
        
        # Step 1: Create media
        media_response = requests.post(
            f"https://graph.facebook.com/{FACEBOOK_CREDENTIALS['instagram_id']}/media",
            data={
                'image_url': image_url,
                'caption': post_data['content'],
                'access_token': FACEBOOK_CREDENTIALS['access_token']
            }
        )
        
        if media_response.status_code != 200:
            error = media_response.json().get('error', {}).get('message', 'Media creation failed')
            print(f"📷 ❌ Instagram media failed: {error}")
            return {'success': False, 'platform': 'instagram', 'error': error}
        
        creation_id = media_response.json().get('id')
        
        # Step 2: Publish media
        publish_response = requests.post(
            f"https://graph.facebook.com/{FACEBOOK_CREDENTIALS['instagram_id']}/media_publish",
            data={
                'creation_id': creation_id,
                'access_token': FACEBOOK_CREDENTIALS['access_token']
            }
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            post_id = result.get('id', 'unknown')
            post_url = f'https://instagram.com/p/{post_id}'
            
            print(f"📷 ✅ Instagram: {post_url}")
            return {'success': True, 'platform': 'instagram', 'url': post_url, 'post_id': post_id}
        else:
            error = publish_response.json().get('error', {}).get('message', 'Publishing failed')
            print(f"📷 ❌ Instagram failed: {error}")
            return {'success': False, 'platform': 'instagram', 'error': error}
            
    except Exception as e:
        print(f"📷 ❌ Instagram failed: {e}")
        return {'success': False, 'platform': 'instagram', 'error': str(e)}

def main():
    """Post child support article to live social media"""
    print("🚀 DadAssist Live Social Media Test")
    print("📖 Article: Understanding Child Support Assessment Formulas")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Article data
    article = {
        'title': 'Understanding Child Support Assessment Formulas',
        'description': 'How child support amounts are calculated in Australia',
        'filename': 'child-support-assessment-formulas.html',
        'url': 'https://dadassist.com.au/posts/articles/child-support-assessment-formulas.html'
    }
    
    # Generate posts
    all_posts = generate_all_posts(article)
    
    results = []
    
    # Post to all platforms
    print("🎯 Posting to live social media platforms...")
    print()
    
    # Twitter
    print("🐦 Posting to Twitter...")
    twitter_result = post_to_twitter(all_posts['posts']['twitter'])
    results.append(twitter_result)
    
    # Facebook  
    print("📘 Posting to Facebook...")
    facebook_result = post_to_facebook(all_posts['posts']['facebook'])
    results.append(facebook_result)
    
    # Instagram
    print("📷 Posting to Instagram...")
    instagram_result = post_to_instagram(all_posts['posts']['instagram'])
    results.append(instagram_result)
    
    # Summary
    print()
    print("=" * 60)
    print("📊 LIVE POSTING RESULTS")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"📖 Article: {article['title']}")
    print(f"🔗 DadAssist URL: {article['url']}")
    print(f"✅ Successful posts: {successful}/3")
    print()
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        platform = result['platform'].title()
        
        if result['success']:
            print(f"{status} {platform}: {result['url']}")
        else:
            print(f"{status} {platform}: {result['error']}")
    
    print()
    print("🎉 Live posting complete!")
    print("📧 Check your social media accounts to see the posts!")

if __name__ == "__main__":
    main()
