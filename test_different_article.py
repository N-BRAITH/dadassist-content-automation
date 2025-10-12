#!/usr/bin/env python3
"""
Test with Best Interests of Children article to avoid duplicate content
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
    'access_token': 'EAFgDFHIYZBS0BPuKM2JuoMFtYoKR27pvnhibeIhB0IxWmCOO2lztqASoXD4u2ZBu4uq4PdtoRQF2rua4g9ZBKpf6N0qH79Jjz03jkxcWj72PtVQjOnICizqCvNb61wVZBUSrZA64J4LXMD8uRo83BQSGKlDSaCxa2La8yCtZB5D8dCVHwwUhhSahSSzlCkLUZCef0wZBMJCQQnLg38LpiSmJ6yHl0xepZBAkRFBBZBMTwZD',
    'page_id': '737106112829383'
}

def post_to_twitter(post_data):
    """Post to Twitter"""
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
        return {'success': True, 'platform': 'twitter', 'url': tweet_url}
        
    except Exception as e:
        print(f"🐦 ❌ Twitter failed: {e}")
        return {'success': False, 'platform': 'twitter', 'error': str(e)}

def post_to_facebook(post_data):
    """Post to Facebook page"""
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
            return {'success': True, 'platform': 'facebook', 'url': post_url}
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            print(f"📘 ❌ Facebook failed: {error}")
            return {'success': False, 'platform': 'facebook', 'error': error}
            
    except Exception as e:
        print(f"📘 ❌ Facebook failed: {e}")
        return {'success': False, 'platform': 'facebook', 'error': str(e)}

def main():
    """Test with Best Interests of Children article"""
    print("🚀 DadAssist Live Social Media Test - Different Article")
    print("📖 Article: Best Interests of Children in Family Law")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Different article to avoid duplicate content
    article = {
        'title': 'Best Interests of Children in Family Law',
        'description': 'Understanding how Australian family courts determine what is best for children in custody and parenting arrangements.',
        'filename': 'best-interests-of-children.html',
        'url': 'https://dadassist.com.au/posts/articles/best-interests-of-children.html'
    }
    
    # Generate posts
    all_posts = generate_all_posts(article)
    
    results = []
    
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
    
    # Skip Instagram for now due to API issues
    print("📷 Skipping Instagram (API permission issues)")
    
    # Summary
    print()
    print("=" * 60)
    print("📊 LIVE POSTING RESULTS")
    print("=" * 60)
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"📖 Article: {article['title']}")
    print(f"🔗 DadAssist URL: {article['url']}")
    print(f"✅ Successful posts: {successful}/2 (Twitter + Facebook)")
    print()
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        platform = result['platform'].title()
        
        if result['success']:
            print(f"{status} {platform}: {result['url']}")
        else:
            print(f"{status} {platform}: {result['error']}")
    
    print()
    if successful > 0:
        print("🎉 Live posting successful!")
        print("📧 Check your social media accounts to see the posts!")
    else:
        print("❌ No posts were successful - check credentials and permissions")

if __name__ == "__main__":
    main()
