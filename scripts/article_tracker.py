#!/usr/bin/env python3
"""
DadAssist Social Media - Article Tracking System
Tracks which articles have been posted to which platforms and when
"""

import json
import os
from datetime import datetime

class ArticleTracker:
    def __init__(self):
        self.tracking_file = 'social-media/posted_articles_tracking.json'
        self.previous_articles_file = 'social-media/previous_articles.json'
        
    def load_tracking_data(self):
        """Load existing tracking data"""
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error loading tracking data: {e}")
                return {}
        return {}
    
    def save_tracking_data(self, tracking_data):
        """Save tracking data to file"""
        os.makedirs('social-media', exist_ok=True)
        with open(self.tracking_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)
    
    def mark_article_posted(self, article_filename, platform, post_result):
        """Mark an article as posted to a specific platform"""
        tracking_data = self.load_tracking_data()
        
        if article_filename not in tracking_data:
            tracking_data[article_filename] = {
                'first_posted': datetime.now().isoformat(),
                'platforms': {}
            }
        
        # Record platform-specific posting details
        tracking_data[article_filename]['platforms'][platform] = {
            'posted_date': datetime.now().isoformat(),
            'success': post_result.get('success', False),
            'post_id': post_result.get('post_id', ''),
            'url': post_result.get('url', ''),
            'message': post_result.get('message', ''),
            'error': post_result.get('error', '')
        }
        
        # Update last posted date
        tracking_data[article_filename]['last_posted'] = datetime.now().isoformat()
        
        self.save_tracking_data(tracking_data)
        print(f"📝 Tracked: {article_filename} posted to {platform}")
    
    def is_article_posted(self, article_filename, platform=None):
        """Check if article has been posted to a platform"""
        tracking_data = self.load_tracking_data()
        
        if article_filename not in tracking_data:
            return False
        
        if platform:
            # Check specific platform
            return platform in tracking_data[article_filename]['platforms']
        else:
            # Check if posted to any platform
            return len(tracking_data[article_filename]['platforms']) > 0
    
    def get_article_posting_status(self, article_filename):
        """Get detailed posting status for an article"""
        tracking_data = self.load_tracking_data()
        
        if article_filename not in tracking_data:
            return {
                'posted': False,
                'platforms': [],
                'first_posted': None,
                'last_posted': None
            }
        
        article_data = tracking_data[article_filename]
        return {
            'posted': len(article_data['platforms']) > 0,
            'platforms': list(article_data['platforms'].keys()),
            'first_posted': article_data.get('first_posted'),
            'last_posted': article_data.get('last_posted'),
            'platform_details': article_data['platforms']
        }
    
    def get_unposted_articles(self, all_articles, platforms=['twitter', 'facebook', 'instagram']):
        """Get articles that haven't been posted to all specified platforms"""
        unposted = []
        
        for article in all_articles:
            filename = article['filename']
            missing_platforms = []
            
            for platform in platforms:
                if not self.is_article_posted(filename, platform):
                    missing_platforms.append(platform)
            
            if missing_platforms:
                article_copy = article.copy()
                article_copy['missing_platforms'] = missing_platforms
                unposted.append(article_copy)
        
        return unposted
    
    def remove_posted_from_queue(self, new_articles_file='social-media/new_articles_found.json'):
        """Remove fully posted articles from the new articles queue"""
        if not os.path.exists(new_articles_file):
            return
        
        try:
            with open(new_articles_file, 'r') as f:
                queue_data = json.load(f)
            
            original_count = len(queue_data['new_articles'])
            platforms = ['twitter', 'facebook', 'instagram']
            
            # Filter out articles posted to all platforms
            filtered_articles = []
            for article in queue_data['new_articles']:
                filename = article['filename']
                posted_platforms = []
                
                if self.is_article_posted(filename):
                    status = self.get_article_posting_status(filename)
                    posted_platforms = status['platforms']
                
                # Keep article if not posted to all platforms
                if len(posted_platforms) < len(platforms):
                    article['remaining_platforms'] = [p for p in platforms if p not in posted_platforms]
                    filtered_articles.append(article)
            
            # Update queue
            queue_data['new_articles'] = filtered_articles
            queue_data['new_articles_count'] = len(filtered_articles)
            queue_data['last_filtered'] = datetime.now().isoformat()
            
            with open(new_articles_file, 'w') as f:
                json.dump(queue_data, f, indent=2)
            
            removed_count = original_count - len(filtered_articles)
            print(f"📋 Filtered queue: {removed_count} fully posted articles removed, {len(filtered_articles)} remaining")
            
        except Exception as e:
            print(f"⚠️ Error filtering queue: {e}")
    
    def generate_posting_report(self):
        """Generate a report of all posting activity"""
        tracking_data = self.load_tracking_data()
        
        report = {
            'generated_date': datetime.now().isoformat(),
            'total_articles_posted': len(tracking_data),
            'platform_stats': {
                'twitter': 0,
                'facebook': 0,
                'instagram': 0,
                'tiktok': 0
            },
            'recent_posts': [],
            'failed_posts': []
        }
        
        for filename, data in tracking_data.items():
            for platform, post_data in data['platforms'].items():
                if post_data['success']:
                    report['platform_stats'][platform] += 1
                    
                    # Add to recent posts (last 7 days)
                    post_date = datetime.fromisoformat(post_data['posted_date'].replace('Z', '+00:00'))
                    days_ago = (datetime.now() - post_date.replace(tzinfo=None)).days
                    
                    if days_ago <= 7:
                        report['recent_posts'].append({
                            'filename': filename,
                            'platform': platform,
                            'posted_date': post_data['posted_date'],
                            'url': post_data.get('url', '')
                        })
                else:
                    report['failed_posts'].append({
                        'filename': filename,
                        'platform': platform,
                        'error': post_data.get('error', 'Unknown error'),
                        'attempted_date': post_data['posted_date']
                    })
        
        # Sort recent posts by date
        report['recent_posts'].sort(key=lambda x: x['posted_date'], reverse=True)
        
        return report

# Test function
if __name__ == "__main__":
    tracker = ArticleTracker()
    
    # Test with sample data
    sample_result = {
        'success': True,
        'platform': 'twitter',
        'post_id': '1234567890',
        'url': 'https://twitter.com/dad_assist/status/1234567890',
        'message': 'Posted successfully'
    }
    
    tracker.mark_article_posted('best-interests-of-children.html', 'twitter', sample_result)
    
    status = tracker.get_article_posting_status('best-interests-of-children.html')
    print(f"Article status: {status}")
    
    report = tracker.generate_posting_report()
    print(f"Posting report: {json.dumps(report, indent=2)}")
