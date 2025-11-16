#!/usr/bin/env python3
"""
Update article metadata after generation
"""

import json
import sys
from datetime import datetime

def update_metadata(filename, title, source_url, article_url):
    """Add new article to metadata"""
    
    # Load metadata
    with open('config/article_metadata.json', 'r') as f:
        metadata = json.load(f)
    
    # Add new article
    article_id = metadata['next_article_id']
    metadata['articles'].append({
        'article_id': article_id,
        'filename': filename,
        'title': title,
        'source_url': source_url,
        'generated_date': datetime.now().isoformat(),
        'live_url': article_url,
        'category': 'Legal Procedures'
    })
    
    # Increment counter
    metadata['next_article_id'] = article_id + 1
    metadata['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open('config/article_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f'✅ Added article {article_id} to metadata')
    return article_id

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: update_metadata.py <filename> <title> <source_url> <article_url>")
        sys.exit(1)
    
    filename = sys.argv[1]
    title = sys.argv[2]
    source_url = sys.argv[3]
    article_url = sys.argv[4]
    
    update_metadata(filename, title, source_url, article_url)
