#!/usr/bin/env python3
"""
DadAssist Content Automation - Content Downloader
Downloads scraped content and organizes locally
"""

import os
import json
import requests
from datetime import datetime
from bs4 import BeautifulSoup

def load_latest_run():
    """Load the latest scraping run information"""
    try:
        with open('downloads/latest_run.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No latest run found. Run apify_scraper.py first.")
        return None

def extract_content_simple(url, title, description):
    """Simple content extraction using requests and BeautifulSoup"""
    try:
        print(f"  📄 Extracting: {title[:50]}...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try different content selectors
        content = ""
        selectors = [
            'article',
            '.content',
            '.main-content',
            '#content',
            '.page-content',
            'main',
            '.post-content'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(strip=True, separator=' ')
                if len(content) > 500:
                    break
        
        # Fallback to body
        if not content or len(content) < 500:
            body = soup.find('body')
            if body:
                content = body.get_text(strip=True, separator=' ')
        
        # Clean up content
        content = ' '.join(content.split())  # Normalize whitespace
        
        # Extract title if not provided
        if not title or title == "No title found":
            title_elem = soup.find('h1') or soup.find('title')
            if title_elem:
                title = title_elem.get_text(strip=True)
        
        return {
            'url': url,
            'title': title,
            'content': content,
            'description': description,
            'wordCount': len(content.split()),
            'contentLength': len(content),
            'extractedAt': datetime.now().isoformat(),
            'extractionMethod': 'requests_beautifulsoup'
        }
        
    except Exception as e:
        print(f"    ❌ Error extracting {url}: {e}")
        return {
            'url': url,
            'title': title,
            'description': description,
            'error': str(e),
            'extractedAt': datetime.now().isoformat()
        }

def categorize_content(article):
    """Categorize article based on title and content"""
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    description = article.get('description', '').lower()
    
    text_to_check = f"{title} {content[:1000]} {description}"
    
    # Define category keywords
    categories = {
        'child_support': ['child support', 'csa', 'assessment', 'maintenance', 'financial support'],
        'family_violence': ['family violence', 'intervention order', 'restraining order', 'domestic violence', 'fvio'],
        'parenting_custody': ['parenting', 'custody', 'children', 'arrangements', 'contact', 'residence'],
        'mental_health': ['mental health', 'wellbeing', 'stress', 'depression', 'anxiety', 'support']
    }
    
    # Check for category keywords
    for category, keywords in categories.items():
        if any(keyword in text_to_check for keyword in keywords):
            return category
    
    return 'general_legal'

def process_articles(filtered_urls):
    """Process all articles and extract content"""
    print(f"📄 Extracting content from {len(filtered_urls)} articles...")
    
    extracted_articles = []
    
    for url_data in filtered_urls:
        article = extract_content_simple(
            url_data['url'], 
            url_data.get('title', ''), 
            url_data.get('description', '')
        )
        
        if not article.get('error'):
            # Quality check
            word_count = article.get('wordCount', 0)
            content_length = article.get('contentLength', 0)
            
            if word_count >= 100 and content_length >= 500:
                article['category'] = categorize_content(article)
                article['originalPosition'] = url_data.get('position', 0)
                extracted_articles.append(article)
                print(f"    ✅ Success: {word_count} words")
            else:
                print(f"    ⚠️  Low quality: {word_count} words, {content_length} chars")
        
    return extracted_articles

def organize_and_save_content(articles, results_dir):
    """Organize content by category and save for Q Developer"""
    print("📁 Organizing content by category...")
    
    organized = {
        'child_support': [],
        'family_violence': [],
        'parenting_custody': [],
        'mental_health': [],
        'general_legal': []
    }
    
    # Organize by category
    for article in articles:
        category = article.get('category', 'general_legal')
        organized[category].append(article)
    
    # Save by category
    for category, category_articles in organized.items():
        if category_articles:
            category_file = f"{results_dir}/{category}_articles.json"
            with open(category_file, 'w', encoding='utf-8') as f:
                json.dump(category_articles, f, indent=2, ensure_ascii=False)
            print(f"  📂 {category}: {len(category_articles)} articles")
    
    # Save all articles
    all_articles_file = f"{results_dir}/all_extracted_content.json"
    with open(all_articles_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    # Create Q Developer processing file
    q_developer_input = {
        "processing_instructions": {
            "task": "Rewrite and summarize legal articles for DadAssist audience",
            "target_audience": "Fathers going through family law issues",
            "tone": "Supportive, clear, practical",
            "format": "DadAssist HTML article format",
            "requirements": [
                "Simplify legal language to 8th grade reading level",
                "Focus on practical advice for fathers",
                "Add actionable steps and tips",
                "Include relevant headings and bullet points",
                "Maintain legal accuracy while improving readability",
                "Add DadAssist branding and call-to-action sections"
            ]
        },
        "articles": articles,
        "total_articles": len(articles),
        "categories": {cat: len(arts) for cat, arts in organized.items() if arts},
        "processing_date": datetime.now().isoformat(),
        "ready_for_q_developer": True
    }
    
    q_input_file = f"{results_dir}/q_developer_input.json"
    with open(q_input_file, 'w', encoding='utf-8') as f:
        json.dump(q_developer_input, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created Q Developer input file: {q_input_file}")
    
    return len(articles)

def main():
    """Main content download function"""
    print("📥 Starting content download and extraction...")
    
    # Load latest scraping run
    run_info = load_latest_run()
    if not run_info or not run_info.get('success'):
        print("❌ No successful scraping run found")
        return False
    
    print(f"📋 Processing {run_info.get('url_count', 0)} URLs from {run_info['results_dir']}")
    
    # Load filtered URLs
    try:
        urls_file = f"{run_info['results_dir']}/filtered_urls.json"
        with open(urls_file, 'r', encoding='utf-8') as f:
            filtered_urls = json.load(f)
    except FileNotFoundError:
        print(f"❌ URLs file not found: {urls_file}")
        return False
    
    try:
        # Extract content from all articles
        extracted_articles = process_articles(filtered_urls)
        
        if not extracted_articles:
            print("❌ No quality articles extracted")
            return False
        
        # Organize and save content
        article_count = organize_and_save_content(extracted_articles, run_info['results_dir'])
        
        print(f"✅ Content download completed successfully!")
        print(f"📊 Results: {article_count} quality articles ready for Q Developer processing")
        
        # Update run info
        run_info.update({
            "content_extracted": True,
            "quality_articles": article_count,
            "q_developer_ready": True,
            "extraction_method": "requests_beautifulsoup"
        })
        
        with open("downloads/latest_run.json", 'w') as f:
            json.dump(run_info, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"❌ Content download failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
