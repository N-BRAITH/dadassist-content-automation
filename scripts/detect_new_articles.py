#!/usr/bin/env python3
"""
DadAssist Social Media Automation - Article Detection
Compares current articles on website with previous run to find new articles
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def get_current_articles():
    """Scrape current articles from DadAssist website"""
    print("🔍 Scraping current articles from dadassist.com.au...")
    
    try:
        response = requests.get('https://dadassist.com.au/posts/index.html', timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all article links
        article_links = soup.find_all('a', href=lambda x: x and 'articles/' in x)
        
        current_articles = []
        for link in article_links:
            filename = link['href'].replace('articles/', '')
            title = link.get_text().strip()
            
            # Get description from next sibling div
            description_div = link.find_next_sibling('div', class_='resource-description')
            description = description_div.get_text().strip() if description_div else ""
            
            current_articles.append({
                'filename': filename,
                'title': title,
                'description': description,
                'url': f"https://dadassist.com.au/posts/articles/{filename}",
                'discovered_date': datetime.now().isoformat()
            })
        
        print(f"✅ Found {len(current_articles)} total articles on website")
        return current_articles
        
    except Exception as e:
        print(f"❌ Error scraping articles: {e}")
        return []

def load_previous_articles():
    """Load previous articles list from file"""
    previous_file = 'social-media/previous_articles.json'
    
    if os.path.exists(previous_file):
        try:
            with open(previous_file, 'r') as f:
                previous_articles = json.load(f)
            print(f"📋 Loaded {len(previous_articles)} articles from previous run")
            return previous_articles
        except Exception as e:
            print(f"⚠️ Error loading previous articles: {e}")
            return []
    else:
        print("📋 No previous articles file found - first run")
        return []

def detect_new_articles():
    """Compare current vs previous articles to find new ones"""
    current_articles = get_current_articles()
    previous_articles = load_previous_articles()
    
    if not current_articles:
        print("❌ No current articles found - aborting")
        return []
    
    # Get filenames from previous run
    previous_filenames = [article['filename'] for article in previous_articles]
    
    # Find new articles
    new_articles = [
        article for article in current_articles 
        if article['filename'] not in previous_filenames
    ]
    
    print(f"🆕 Found {len(new_articles)} new articles since last run")
    
    # Log new articles
    if new_articles:
        print("\n📝 New articles detected:")
        for i, article in enumerate(new_articles, 1):
            print(f"  {i}. {article['title']}")
            print(f"     File: {article['filename']}")
            print(f"     Description: {article['description'][:100]}...")
            print()
    else:
        print("✅ No new articles found - no social media posts needed")
    
    return new_articles, current_articles

def save_results(new_articles, current_articles):
    """Save detection results and update previous articles list"""
    
    # Ensure social-media directory exists
    os.makedirs('social-media', exist_ok=True)
    
    # Save new articles for social media posting
    with open('social-media/new_articles_found.json', 'w') as f:
        json.dump({
            'detection_date': datetime.now().isoformat(),
            'new_articles_count': len(new_articles),
            'new_articles': new_articles
        }, f, indent=2)
    
    # Update previous articles list for next run
    with open('social-media/previous_articles.json', 'w') as f:
        json.dump(current_articles, f, indent=2)
    
    print(f"💾 Saved {len(new_articles)} new articles to social-media/new_articles_found.json")
    print(f"💾 Updated previous articles list with {len(current_articles)} total articles")

def main():
    """Main article detection function"""
    print("🤖 DadAssist Social Media - Article Detection Starting...")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    new_articles, current_articles = detect_new_articles()
    
    if current_articles:
        save_results(new_articles, current_articles)
        
        if new_articles:
            print(f"✅ Detection complete: {len(new_articles)} new articles ready for social media posting")
        else:
            print("✅ Detection complete: No new articles found")
    else:
        print("❌ Detection failed: Could not retrieve current articles")
        exit(1)

if __name__ == "__main__":
    main()
