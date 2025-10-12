#!/usr/bin/env python3
"""
DadAssist Social Media Automation - Main Poster
Reads new articles and posts to all social media platforms
"""

import json
import os
import sys
import argparse
from datetime import datetime

# Import platform-specific posters
sys.path.append(os.path.join(os.path.dirname(__file__), 'platforms'))
from twitter_poster import TwitterPoster
from facebook_poster import FacebookPoster
from instagram_poster import InstagramPoster
from tiktok_poster import TikTokPoster

# Import post templates
from post_templates import generate_all_posts

def load_new_articles():
    """Load new articles from detection system"""
    articles_file = 'social-media/new_articles_found.json'
    
    if not os.path.exists(articles_file):
        print(f"❌ No new articles file found: {articles_file}")
        return None
    
    try:
        with open(articles_file, 'r') as f:
            data = json.load(f)
        
        print(f"📋 Loaded {data['new_articles_count']} new articles for social media posting")
        return data
    except Exception as e:
        print(f"❌ Error loading new articles: {e}")
        return None

def post_to_all_platforms(article, dry_run=True):
    """Post article to social media platforms (excluding TikTok for now)"""
    print(f"\n📝 Processing article: {article['title']}")
    print(f"   File: {article['filename']}")
    
    # Generate platform-specific posts
    all_posts = generate_all_posts(article)
    
    # Initialize platform posters (excluding TikTok)
    twitter = TwitterPoster(dry_run=dry_run)
    facebook = FacebookPoster(dry_run=dry_run)
    instagram = InstagramPoster(dry_run=dry_run)
    
    results = []
    
    # Post to Twitter
    print(f"\n🐦 Posting to Twitter...")
    if twitter.authenticate():
        result = twitter.post_tweet(all_posts['posts']['twitter'])
        results.append(result)
    else:
        results.append({'success': False, 'platform': 'twitter', 'error': 'Authentication failed'})
    
    # Post to Facebook
    print(f"\n📘 Posting to Facebook...")
    if facebook.authenticate():
        result = facebook.post_to_page(all_posts['posts']['facebook'])
        results.append(result)
    else:
        results.append({'success': False, 'platform': 'facebook', 'error': 'Authentication failed'})
    
    # Post to Instagram
    print(f"\n📷 Posting to Instagram...")
    if instagram.authenticate():
        result = instagram.create_image_post(all_posts['posts']['instagram'])
        results.append(result)
    else:
        results.append({'success': False, 'platform': 'instagram', 'error': 'Authentication failed'})
    
    # Skip TikTok for now
    print(f"\n🎵 Skipping TikTok (not configured)")
    
    return {
        'article': all_posts['article'],
        'posts_generated': all_posts['posts'],
        'posting_results': results
    }

def save_posting_results(all_results, dry_run=True):
    """Save posting results for review"""
    os.makedirs('social-media/results', exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'social-media/results/posting_results_{timestamp}.json'
    
    summary = {
        'run_date': datetime.now().isoformat(),
        'dry_run': dry_run,
        'articles_processed': len(all_results),
        'total_posts_attempted': len(all_results) * 4,  # 4 platforms
        'results': all_results
    }
    
    with open(filename, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    return filename

def print_summary(all_results, dry_run=True):
    """Print summary of posting results"""
    print(f"\n{'='*60}")
    print(f"🤖 DadAssist Social Media Posting {'(DRY RUN)' if dry_run else '(LIVE)'} - Summary")
    print(f"{'='*60}")
    
    total_articles = len(all_results)
    total_attempts = sum(len(result['posting_results']) for result in all_results)
    total_successes = sum(
        sum(1 for post_result in result['posting_results'] if post_result['success'])
        for result in all_results
    )
    
    print(f"📊 Articles processed: {total_articles}")
    print(f"📊 Total posts attempted: {total_attempts}")
    print(f"📊 Successful posts: {total_successes}")
    print(f"📊 Success rate: {(total_successes/total_attempts*100):.1f}%" if total_attempts > 0 else "📊 Success rate: N/A")
    
    # Platform breakdown
    platforms = ['twitter', 'facebook', 'instagram', 'tiktok']
    for platform in platforms:
        platform_successes = sum(
            1 for result in all_results
            for post_result in result['posting_results']
            if post_result['platform'] == platform and post_result['success']
        )
        print(f"   {platform.title()}: {platform_successes}/{total_articles}")
    
    print(f"{'='*60}")

def validate_credentials():
    """Validate that all required credentials are available"""
    print("🔐 Validating API credentials...")
    
    missing_credentials = []
    
    # Check Twitter credentials
    twitter_creds = ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET']
    for cred in twitter_creds:
        if not os.getenv(cred):
            missing_credentials.append(f"Twitter: {cred}")
    
    # Check Facebook/Instagram credentials
    facebook_creds = ['FACEBOOK_ACCESS_TOKEN', 'FACEBOOK_PAGE_ID', 'INSTAGRAM_ACCOUNT_ID']
    for cred in facebook_creds:
        if not os.getenv(cred):
            missing_credentials.append(f"Facebook/Instagram: {cred}")
    
    if missing_credentials:
        print("❌ Missing credentials:")
        for cred in missing_credentials:
            print(f"   - {cred}")
        print("\n🔧 To fix this:")
        print("1. Go to: https://github.com/N-BRAITH/dadassist-content-automation/settings/secrets/actions")
        print("2. Add the missing secrets")
        print("3. Re-run the automation")
        return False
    else:
        print("✅ All credentials found in environment")
        return True

def main():
    """Main social media posting function"""
    parser = argparse.ArgumentParser(description='DadAssist Social Media Poster')
    parser.add_argument('--dry-run', action='store_true', default=True, 
                       help='Run in dry-run mode (default: True)')
    parser.add_argument('--live', action='store_true', 
                       help='Run in live mode (posts to real accounts)')
    parser.add_argument('--sample', action='store_true',
                       help='Use sample article data for testing')
    
    args = parser.parse_args()
    
    # Determine run mode
    dry_run = not args.live
    
    print("🤖 DadAssist Social Media Automation Starting...")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"🔧 Mode: {'DRY RUN' if dry_run else 'LIVE POSTING'}")
    print()
    
    # Validate credentials (skip for dry run)
    if not dry_run:
        if not validate_credentials():
            print("❌ Cannot proceed without valid credentials")
            return
        print()
    
    if args.sample:
        # Use sample data for testing
        sample_data = {
            'new_articles_count': 1,
            'new_articles': [{
                'title': 'Understanding Child Support Assessment Formulas',
                'filename': 'child-support-assessment-formulas.html',
                'description': 'How child support amounts are calculated in Australia',
                'url': 'https://dadassist.com.au/posts/articles/child-support-assessment-formulas.html'
            }]
        }
        articles_data = sample_data
    else:
        # Load real article data
        articles_data = load_new_articles()
    
    if not articles_data or articles_data['new_articles_count'] == 0:
        print("✅ No new articles found - no social media posts needed")
        return
    
    # Process only 1 article per run (weekly posting)
    articles_to_process = articles_data['new_articles'][:1]  # Limit to 1 article
    
    print(f"📋 Processing 1 article from {articles_data['new_articles_count']} available articles")
    
    all_results = []
    for article in articles_to_process:
        result = post_to_all_platforms(article, dry_run=dry_run)
        all_results.append(result)
    
    # Track posted articles and remove from queue
    if not dry_run:
        tracker = ArticleTracker()
        for result in all_results:
            article_filename = result['article']['filename']
            for post_result in result['posting_results']:
                tracker.mark_article_posted(article_filename, post_result['platform'], post_result)
        
        # Remove posted article from new articles queue
        tracker.remove_posted_from_queue()
    
    # Save and display results
    results_file = save_posting_results(all_results, dry_run=dry_run)
    print_summary(all_results, dry_run=dry_run)
    
    # Send notification email
    try:
        from social_media_notifier import send_social_media_notification
        
        # Load the results we just saved
        with open(results_file, 'r') as f:
            notification_data = json.load(f)
        
        print(f"\n📧 Sending notification email...")
        send_social_media_notification(notification_data)
        
    except Exception as e:
        print(f"⚠️ Could not send notification email: {e}")
    
    if dry_run:
        print("\n💡 This was a dry run. To post live, use: --live flag")
    else:
        print("\n✅ Live posting complete!")

if __name__ == "__main__":
    main()
