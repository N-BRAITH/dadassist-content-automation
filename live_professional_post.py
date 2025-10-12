#!/usr/bin/env python3
"""
DadAssist Professional Social Media Post - All Three Platforms
Posts a professional article promotion to Twitter, Facebook, and Instagram
"""

import sys
import os
sys.path.append('scripts')

from post_templates import generate_all_posts
import tweepy
import requests
from datetime import datetime

# Working credentials
TWITTER_CREDENTIALS = {
    'api_key': 'LgBPdKYGrVKd4um7MESfnBpBf',
    'api_secret': 'k8cjRytwRf8BHWqQ67INqL2NAJr2shVpB8TY1GsoeEp0mDRruv',
    'access_token': '1976802841374474242-gAdhhBMATIk1bG85m0HWYJGkRlmPFr',
    'access_secret': 'z9a6kthBjMmsebi9ivUeE8tXBeitgnAlGMDOaSuFwZm1r'
}

FACEBOOK_TOKEN = 'EAALwm5pQA0kBPk07sZC4xL4iY2TnkJu5vx66Oon6pbHxq86hZCAlokMnGsK6EBJx3h38sb716FB1WEWoaVIXsbGdKPZCcJtZC4iECfA7ikPSxciEZAtEZAVErTtKhPZCifHZAVqL6ROViGk883vXAn1iSoWpHcH4ObxXolV8gwfyPPbX2fvl5N9wFZBcRzZCXShFEprZCk5Fogrt6S74dqbS46zG670H5rJW52ALd7JUnRvsgZDZD'

INSTAGRAM_TOKEN = 'EAFgDFHIYZBS0BPrmE4rmfuSC5dRIsqnpzddnbv0w9aAU113zydGcLhgx2vLTq2VuANV1lqG4s1pHl5HqiQORp3yy0QyIHmItWtRZAZA6iHBCUto8YbcKdxVmNoX7UZA2t1wkQLuun96zKMIHr3jc5Gpuh7vcYJZAkTZAIBjfxVxSy35kRqileeq0kS4k8wZB85gZAZAbHiRQvDyq00HsLdihZBITQ8zgvrozsEHqJvokS7'

FACEBOOK_PAGE_ID = '737106112829383'
INSTAGRAM_ACCOUNT_ID = '17841477240606238'

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
        
        return {'success': True, 'platform': 'twitter', 'url': tweet_url, 'post_id': tweet_id}
        
    except Exception as e:
        return {'success': False, 'platform': 'twitter', 'error': str(e)}

def post_to_facebook(post_data):
    """Post to Facebook"""
    try:
        response = requests.post(
            f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed",
            data={
                'message': post_data['content'],
                'access_token': FACEBOOK_TOKEN
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            post_id = result.get('id', 'unknown')
            post_url = f'https://facebook.com/DadAssist'
            
            return {'success': True, 'platform': 'facebook', 'url': post_url, 'post_id': post_id}
        else:
            error = response.json().get('error', {}).get('message', 'Unknown error')
            return {'success': False, 'platform': 'facebook', 'error': error}
            
    except Exception as e:
        return {'success': False, 'platform': 'facebook', 'error': str(e)}

def post_to_instagram(post_data):
    """Post to Instagram"""
    try:
        # Professional image for DadAssist
        image_url = 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1080&h=1080&fit=crop'
        
        # Step 1: Create media container
        media_response = requests.post(
            f"https://graph.facebook.com/{INSTAGRAM_ACCOUNT_ID}/media",
            data={
                'image_url': image_url,
                'caption': post_data['content'],
                'access_token': INSTAGRAM_TOKEN
            }
        )
        
        if media_response.status_code == 200:
            creation_id = media_response.json().get('id')
            
            # Step 2: Publish media
            publish_response = requests.post(
                f"https://graph.facebook.com/{INSTAGRAM_ACCOUNT_ID}/media_publish",
                data={
                    'creation_id': creation_id,
                    'access_token': INSTAGRAM_TOKEN
                }
            )
            
            if publish_response.status_code == 200:
                result = publish_response.json()
                post_id = result.get('id', 'unknown')
                post_url = f'https://instagram.com/dadassist'
                
                return {'success': True, 'platform': 'instagram', 'url': post_url, 'post_id': post_id}
            else:
                error = publish_response.json().get('error', {}).get('message', 'Publishing failed')
                return {'success': False, 'platform': 'instagram', 'error': error}
        else:
            error = media_response.json().get('error', {}).get('message', 'Media creation failed')
            return {'success': False, 'platform': 'instagram', 'error': error}
            
    except Exception as e:
        return {'success': False, 'platform': 'instagram', 'error': str(e)}

def main():
    """Post professional DadAssist article to all three platforms"""
    print("🚀 DadAssist Professional Social Media Campaign")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Professional article selection - Parenting Orders
    article = {
        'title': 'Parenting Orders and Plans',
        'description': 'A comprehensive guide to creating and implementing effective parenting arrangements that prioritize your children\'s wellbeing while protecting your parental rights.',
        'filename': 'parenting-orders-and-plans.html',
        'url': 'https://dadassist.com.au/posts/articles/parenting-orders-and-plans.html'
    }
    
    print(f"📖 Article: {article['title']}")
    print(f"🔗 URL: {article['url']}")
    print()
    
    # Generate professional posts
    all_posts = generate_all_posts(article)
    
    results = []
    
    print("🎯 Publishing to all platforms...")
    print()
    
    # Post to Twitter
    print("🐦 Publishing to Twitter...")
    twitter_result = post_to_twitter(all_posts['posts']['twitter'])
    results.append(twitter_result)
    
    if twitter_result['success']:
        print(f"   ✅ Success: {twitter_result['url']}")
    else:
        print(f"   ❌ Failed: {twitter_result['error']}")
    
    # Post to Facebook  
    print("📘 Publishing to Facebook...")
    facebook_result = post_to_facebook(all_posts['posts']['facebook'])
    results.append(facebook_result)
    
    if facebook_result['success']:
        print(f"   ✅ Success: {facebook_result['url']}")
    else:
        print(f"   ❌ Failed: {facebook_result['error']}")
    
    # Post to Instagram
    print("📷 Publishing to Instagram...")
    instagram_result = post_to_instagram(all_posts['posts']['instagram'])
    results.append(instagram_result)
    
    if instagram_result['success']:
        print(f"   ✅ Success: {instagram_result['url']}")
    else:
        print(f"   ❌ Failed: {instagram_result['error']}")
    
    # Summary
    print()
    print("=" * 70)
    print("📊 PROFESSIONAL CAMPAIGN RESULTS")
    print("=" * 70)
    
    successful = sum(1 for r in results if r['success'])
    
    print(f"📖 Article: {article['title']}")
    print(f"🔗 DadAssist URL: {article['url']}")
    print(f"✅ Successful publications: {successful}/3")
    print()
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        platform = result['platform'].title()
        
        if result['success']:
            print(f"{status} {platform}: {result['url']}")
        else:
            print(f"{status} {platform}: {result['error']}")
    
    print()
    if successful == 3:
        print("🎉 Complete success! Article published across all platforms!")
        print("📱 Check your social media accounts to see the professional posts!")
    elif successful > 0:
        print(f"✅ Partial success! {successful} platforms published successfully.")
    else:
        print("❌ Campaign failed - check credentials and try again.")

if __name__ == "__main__":
    main()
