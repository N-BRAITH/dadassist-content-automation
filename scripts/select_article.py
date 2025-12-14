#!/usr/bin/env python3
"""Select next unprocessed article from DadAssist website."""

import json
import random
import requests
from bs4 import BeautifulSoup

INDEX_URL = "https://www.dadassist.com.au/posts/index.html"
PROCESSED_FILE = "processed_urls.json"

def load_processed_urls():
    """Load list of already processed URLs."""
    try:
        with open(PROCESSED_FILE, 'r') as f:
            data = json.load(f)
            return {item['url'] for item in data}
    except FileNotFoundError:
        return set()

def scrape_article_urls():
    """Scrape all article URLs from index page."""
    print(f"📥 Fetching article list from {INDEX_URL}")
    
    response = requests.get(INDEX_URL, timeout=30)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all article links
    article_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('articles/') and href.endswith('.html'):
            full_url = f"https://www.dadassist.com.au/posts/{href}"
            article_links.append(full_url)
    
    print(f"📊 Found {len(article_links)} total articles")
    return article_links

def select_next_article():
    """Select a random unprocessed article."""
    processed = load_processed_urls()
    print(f"✅ Already processed: {len(processed)} articles")
    
    all_articles = scrape_article_urls()
    
    # Get all unprocessed articles
    unprocessed = [url for url in all_articles if url not in processed]
    
    if not unprocessed:
        print("⚠️  All articles have been processed!")
        return None
    
    # Select randomly
    selected = random.choice(unprocessed)
    print(f"🎯 Selected randomly from {len(unprocessed)} unprocessed articles: {selected}")
    return selected

if __name__ == "__main__":
    selected = select_next_article()
    
    if selected:
        with open('selected_url.txt', 'w') as f:
            f.write(selected)
        print(f"💾 Saved to selected_url.txt")
    else:
        print("❌ No unprocessed articles found")
        exit(1)
