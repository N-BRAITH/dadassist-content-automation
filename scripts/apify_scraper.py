#!/usr/bin/env python3
"""
DadAssist Content Automation - Apify Scraper
Handles web scraping using Apify API for legal content discovery
"""

import os
import json
import time
from datetime import datetime
from apify_client import ApifyClient

def load_config():
    """Load scraping configuration"""
    with open('config/apify_config.json', 'r') as f:
        return json.load(f)

def run_google_search_scraper(client, config):
    """Run Google Search Results Scraper with cycling search queries"""
    print("🔍 Starting Google search for legal content...")
    
    # Get current search from rotation
    search_rotation = config["search_rotation"]
    current_index = search_rotation["current_search"]
    current_query = search_rotation["searches"][current_index]
    
    print(f"📋 Using search query #{current_index + 1}: {current_query}")
    
    # Configure search input
    search_input = {
        "queries": current_query,
        "maxPagesPerQuery": config["scraping_settings"]["max_pages_per_query"],
        "resultsPerPage": config["scraping_settings"]["results_per_page"],
        "countryCode": config["scraping_settings"]["country_code"],
        "languageCode": config["scraping_settings"]["language_code"],
        "includeUnfilteredResults": False,
        "mobileResults": False
    }
    
    # Run the Google Search scraper
    run = client.actor("apify/google-search-scraper").call(run_input=search_input)
    
    print(f"✅ Google search completed. Run ID: {run['id']}")
    return run['defaultDatasetId']

def filter_search_results(client, dataset_id, config):
    """Filter search results to get relevant legal articles"""
    print("🔍 Filtering search results...")
    
    # Get search results - need to get the full dataset, not just iterate
    dataset_items = list(client.dataset(dataset_id).iterate_items())
    
    # Extract organic results from the dataset structure
    all_organic_results = []
    for item in dataset_items:
        if 'organicResults' in item:
            for organic_result in item['organicResults']:
                all_organic_results.append(organic_result)
    
    print(f"📊 Found {len(all_organic_results)} total search results")
    
    filtered_urls = []
    
    # Expanded list of trusted Australian legal sites
    trusted_domains = [
        "legalaid.vic.gov.au",
        "familycourt.gov.au", 
        "ag.gov.au",
        "lawhandbook.sa.gov.au",
        "lawaccess.nsw.gov.au",
        "familyrelationships.gov.au",
        "childrenscourt.justice.nsw.gov.au",
        "justice.gov.au",
        "courts.justice.nsw.gov.au",
        "supremecourt.justice.nsw.gov.au",
        "legalaid.nsw.gov.au",
        "legalaid.qld.gov.au",
        "legalaid.wa.gov.au",
        "legalaid.sa.gov.au",
        "legalaid.tas.gov.au",
        "legalaid.act.gov.au",
        "legalaid.nt.gov.au"
    ]
    
    target_sites = config["target_sites"]
    
    for item in all_organic_results:
        url = item.get('url', '')
        title = item.get('title', '')
        description = item.get('description', '')
        
        # Filter by trusted domains OR target sites
        domain_match = any(domain in url for domain in trusted_domains + target_sites)
        
        # Check if it's likely a legal article
        legal_keywords = ['family', 'child', 'custody', 'support', 'law', 'court', 'legal', 
                         'parenting', 'divorce', 'separation', 'intervention', 'order']
        
        title_relevant = len(title) > 10 and any(keyword in title.lower() for keyword in legal_keywords)
        desc_relevant = any(keyword in description.lower() for keyword in legal_keywords)
        
        if domain_match and (title_relevant or desc_relevant):
            filtered_urls.append({
                'url': url,
                'title': title,
                'description': description,
                'position': item.get('position', 0),
                'date': item.get('date', '')
            })
    
    # Limit to max articles per run
    max_articles = config["scraping_settings"]["max_articles_per_run"]
    filtered_urls = filtered_urls[:max_articles]
    
    print(f"✅ Filtered to {len(filtered_urls)} relevant articles")
    
    # Print found URLs for debugging
    for i, url_info in enumerate(filtered_urls, 1):
        print(f"  {i}. {url_info['title'][:60]}...")
        print(f"     {url_info['url']}")
    
    return filtered_urls

def save_results_simple(filtered_urls, config):
    """Save filtered URLs without content extraction for testing"""
    print("💾 Saving filtered results...")
    
    # Create results directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = f"downloads/{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results
    results_file = f"{results_dir}/filtered_urls.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_urls, f, indent=2, ensure_ascii=False)
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "total_urls": len(filtered_urls),
        "urls": [{"title": item.get('title'), "url": item.get('url'), "description": item.get('description')} 
                for item in filtered_urls],
        "config_used": config
    }
    
    summary_file = f"{results_dir}/summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(filtered_urls)} URLs to {results_dir}")
    return results_dir, len(filtered_urls)

def update_search_rotation(config):
    """Update the search rotation to use next query"""
    search_rotation = config["search_rotation"]
    current_index = search_rotation["current_search"]
    total_searches = len(search_rotation["searches"])
    
    # Move to next search (cycle back to 0 after last search)
    next_index = (current_index + 1) % total_searches
    config["search_rotation"]["current_search"] = next_index
    
    print(f"🔄 Updated search rotation: {current_index + 1} → {next_index + 1}")
    
    # Save updated config
    with open('config/apify_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    return next_index

def main():
    """Main scraping function"""
    print("🚀 Starting DadAssist content scraping...")
    
    # Initialize Apify client
    apify_token = os.getenv('APIFY_TOKEN')
    if not apify_token:
        print("❌ APIFY_TOKEN not found in environment variables")
        return False
    
    client = ApifyClient(apify_token)
    
    # Load configuration
    try:
        config = load_config()
        print(f"📋 Configuration loaded: targeting {config['scraping_settings']['max_articles_per_run']} articles")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    try:
        # Step 1: Search for legal articles
        search_dataset_id = run_google_search_scraper(client, config)
        
        # Step 2: Filter results to relevant articles
        filtered_urls = filter_search_results(client, search_dataset_id, config)
        
        if not filtered_urls:
            print("⚠️  No relevant articles found")
            return False
        
        # Step 3: Save filtered URLs (simplified for testing)
        results_dir, url_count = save_results_simple(filtered_urls, config)
        
        print(f"✅ Scraping completed successfully!")
        print(f"📊 Results: {url_count} URLs saved to {results_dir}")
        
        # Save run info for other scripts
        run_info = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "results_dir": results_dir,
            "url_count": url_count
        }
        
        with open("downloads/latest_run.json", 'w') as f:
            json.dump(run_info, f, indent=2)
        
        # Update search rotation for next run
        update_search_rotation(config)
        
        return True
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
        
        # Save error info
        error_info = {
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }
        
        os.makedirs("downloads", exist_ok=True)
        with open("downloads/latest_run.json", 'w') as f:
            json.dump(error_info, f, indent=2)
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
