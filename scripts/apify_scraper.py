#!/usr/bin/env python3
"""
DadAssist Content Automation - Apify Scraper
Handles web scraping using Apify API for legal content discovery
"""

import os
import json
import time
import random
from datetime import datetime
from apify_client import ApifyClient

def load_config():
    """Load scraping configuration"""
    with open('config/apify_config.json', 'r') as f:
        return json.load(f)

def load_scraped_urls():
    """Load previously scraped URLs from exclusion list"""
    try:
        with open('config/scraped_urls.json', 'r') as f:
            data = json.load(f)
            return set(data.get('scraped_urls', []))
    except FileNotFoundError:
        print("⚠️  No scraped_urls.json found - creating new file")
        initial_data = {
            "scraped_urls": [],
            "last_updated": datetime.now().isoformat(),
            "total_scraped": 0
        }
        os.makedirs('config', exist_ok=True)
        with open('config/scraped_urls.json', 'w') as f:
            json.dump(initial_data, f, indent=2)
        return set()

def add_to_scraped_urls(urls):
    """Add URLs to exclusion list"""
    try:
        with open('config/scraped_urls.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"scraped_urls": [], "total_scraped": 0}
    
    added_count = 0
    for url in urls:
        if url not in data['scraped_urls']:
            data['scraped_urls'].append(url)
            added_count += 1
    
    data['last_updated'] = datetime.now().isoformat()
    data['total_scraped'] = len(data['scraped_urls'])
    
    with open('config/scraped_urls.json', 'w') as f:
        json.dump(data, f, indent=2)
    
    return added_count

def run_google_search_scraper(client, config):
    """Run Google Search Results Scraper with cycling search queries"""
    print("🔍 Starting Google search for legal content...")
    
    # Get current search from rotation
    search_rotation = config["search_rotation"]
    current_index = search_rotation["current_search"]
    current_query = search_rotation["searches"][current_index]
    
    print(f"📋 Using search query #{current_index + 1}: {current_query}")
    
    # Apply randomization if enabled
    scraping_settings = config["scraping_settings"]
    randomization = scraping_settings.get("randomization", {})
    
    if randomization.get("enabled", False):
        import random
        
        # Randomize results per page
        results_per_page_options = randomization.get("results_per_page_options", [15])
        results_per_page = random.choice(results_per_page_options)
        
        # Randomize starting position (skip results)
        skip_range = randomization.get("skip_results_range", [0, 0])
        skip_results = random.randint(skip_range[0], skip_range[1])
        
        print(f"🎲 Randomization enabled:")
        print(f"   📄 Results per page: {results_per_page}")
        print(f"   ⏭️ Skipping first {skip_results} results")
    else:
        results_per_page = scraping_settings["results_per_page"]
        skip_results = 0
    
    # Configure search input
    search_input = {
        "queries": current_query,
        "maxPagesPerQuery": scraping_settings["max_pages_per_query"],
        "resultsPerPage": results_per_page,
        "countryCode": scraping_settings["country_code"],
        "languageCode": scraping_settings["language_code"],
        "includeUnfilteredResults": False,
        "mobileResults": False
    }
    
    # Add skip parameter if randomization is enabled
    if skip_results > 0:
        search_input["startUrls"] = [{"url": f"https://www.google.com/search?q={current_query}&start={skip_results}"}]
    
    # Run the Google Search scraper
    run = client.actor("apify/google-search-scraper").call(run_input=search_input)
    
    print(f"✅ Google search completed. Run ID: {run['id']}")
    return run['defaultDatasetId']

def filter_search_results(client, dataset_id, config):
    """Filter search results to get relevant legal articles"""
    print("🔍 Filtering search results...")
    
    # LOAD EXCLUSION LIST FIRST
    scraped_urls = load_scraped_urls()
    print(f"📋 Loaded {len(scraped_urls)} previously scraped URLs")
    
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
    skipped_already_scraped = 0
    skipped_not_relevant = 0
    
    # Legal keywords for relevance check
    legal_keywords = ['family', 'child', 'custody', 'support', 'law', 'court', 'legal', 
                     'parenting', 'divorce', 'separation', 'intervention', 'order', 'father']
    
    for item in all_organic_results:
        url = item.get('url', '')
        title = item.get('title', '')
        description = item.get('description', '')
        
        # CHECK 1: Already scraped?
        if url in scraped_urls:
            skipped_already_scraped += 1
            continue
        
        # CHECK 2: Relevant legal content?
        title_relevant = len(title) > 10 and any(keyword in title.lower() for keyword in legal_keywords)
        desc_relevant = any(keyword in description.lower() for keyword in legal_keywords)
        
        if not (title_relevant or desc_relevant):
            skipped_not_relevant += 1
            continue
        
        # PASSED ALL CHECKS
        filtered_urls.append({
            'url': url,
            'title': title,
            'description': description,
            'position': item.get('position', 0),
            'date': item.get('date', '')
        })
    
    print(f"✅ Filtered to {len(filtered_urls)} new relevant articles")
    print(f"   ⏭️  Skipped {skipped_already_scraped} already scraped")
    print(f"   ⏭️  Skipped {skipped_not_relevant} not relevant")
    
    # Print found URLs for debugging
    for i, url_info in enumerate(filtered_urls[:10], 1):  # Show first 10
        print(f"  {i}. {url_info['title'][:60]}...")
        print(f"     {url_info['url']}")
    
    return filtered_urls

def save_results_simple(filtered_urls, config):
    """Save filtered URLs with randomization and add to exclusion list"""
    print("💾 Saving filtered results...")
    
    if not filtered_urls:
        print("⚠️  No new URLs to save")
        # Save empty run info
        with open('downloads/latest_run.json', 'w') as f:
            json.dump({
                'success': False,
                'new_url_count': 0,
                'timestamp': datetime.now().isoformat(),
                'message': 'No new URLs found - all already scraped'
            }, f, indent=2)
        return None, 0
    
    # Randomize selection from available URLs
    max_articles = config["scraping_settings"]["max_articles_per_run"]
    selected_urls = random.sample(filtered_urls, min(max_articles, len(filtered_urls)))
    print(f"🎲 Randomly selected {len(selected_urls)} articles from {len(filtered_urls)} available")
    
    # COUNT NEW URLs BEFORE adding to exclusion list
    new_url_count = len(selected_urls)
    
    # ADD SELECTED URLs TO EXCLUSION LIST IMMEDIATELY
    urls_to_add = [item['url'] for item in selected_urls]
    added_count = add_to_scraped_urls(urls_to_add)
    print(f"💾 Added {added_count} URLs to exclusion list")
    
    # Create results directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    results_dir = f"downloads/{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    # Save results
    results_file = f"{results_dir}/filtered_urls.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(selected_urls, f, indent=2, ensure_ascii=False)
    
    # Save summary
    summary = {
        "timestamp": timestamp,
        "total_urls": len(selected_urls),
        "urls": [{"title": item.get('title'), "url": item.get('url'), "description": item.get('description')} 
                for item in selected_urls],
        "config_used": config
    }
    
    summary_file = f"{results_dir}/summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Save latest run info for workflow
    latest_run = {
        'success': True,
        'new_url_count': new_url_count,
        'timestamp': timestamp,
        'results_dir': results_dir
    }
    with open('downloads/latest_run.json', 'w') as f:
        json.dump(latest_run, f, indent=2)
    
    print(f"✅ Saved {len(selected_urls)} URLs to {results_dir}")
    return results_dir, new_url_count

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
    """Main scraping function with retry logic for unique articles"""
    print("🚀 Starting DadAssist content scraping...")
    
    max_attempts = 5  # Try up to 5 different search queries
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔍 Scraping attempt {attempt}/{max_attempts}")
        
        # Initialize Apify client
        apify_token = os.getenv('APIFY_TOKEN')
        if not apify_token:
            print("❌ APIFY_TOKEN not found in environment variables")
            return False
        
        client = ApifyClient(apify_token)
        
        try:
            # Load configuration
            config = load_config()
            
            # Get current search query
            current_search_index = config["search_rotation"]["current_search"]
            search_queries = config["search_rotation"]["searches"]
            current_query = search_queries[current_search_index]
            
            print(f"📝 Using search query {current_search_index + 1}: {current_query}")
            
            # Run scraping
            success = run_scraping(client, config, current_query)
            
            if success:
                # Check if we found unique content by looking for SKIP_GENERATION
                skip_generation = os.getenv('SKIP_GENERATION', 'false')
                
                if skip_generation.lower() == 'true':
                    print(f"⚠️ Attempt {attempt}: All articles were duplicates")
                    print("🔄 Rotating to next search query and retrying...")
                    
                    # Rotate to next search query
                    rotate_search_query()
                    
                    # Continue to next attempt
                    continue
                else:
                    print(f"✅ Attempt {attempt}: Found unique content!")
                    return True
            else:
                print(f"❌ Attempt {attempt}: Scraping failed")
                
        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {e}")
        
        # If not the last attempt, rotate search query
        if attempt < max_attempts:
            rotate_search_query()
    
    print(f"❌ All {max_attempts} attempts failed to find unique content")
    return False

def run_scraping(client, config, search_query):
    """Run the actual scraping process"""
    
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
