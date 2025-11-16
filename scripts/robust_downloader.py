#!/usr/bin/env python3
"""
Robust Content Downloader - Handles blocking and failures
Implements 4-layer fallback strategy
"""

import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

class RobustDownloader:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        
    def download_article(self, url, title):
        """Try all 4 methods to download article"""
        
        # METHOD 1: Direct download with retry
        print(f"  📥 Method 1: Direct download...")
        content = self._direct_download(url)
        if content:
            return content
        
        # METHOD 2: Different user agent
        print(f"  🔄 Method 2: Trying different user agent...")
        content = self._download_with_different_ua(url)
        if content:
            return content
        
        # METHOD 3: Google Cache
        print(f"  💾 Method 3: Trying Google Cache...")
        content = self._download_from_cache(url)
        if content:
            return content
        
        # METHOD 4: Archive.org
        print(f"  🗄️ Method 4: Trying Archive.org...")
        content = self._download_from_archive(url)
        if content:
            return content
        
        # All methods failed
        print(f"  ❌ All methods failed for {url}")
        return None
    
    def _direct_download(self, url):
        """Method 1: Direct download"""
        try:
            headers = {'User-Agent': self.user_agents[0]}
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return self._extract_content(response.content, url)
            
        except Exception as e:
            print(f"    ⚠️ Direct download failed: {e}")
        return None
    
    def _download_with_different_ua(self, url):
        """Method 2: Try different user agents"""
        for ua in self.user_agents[1:]:
            try:
                headers = {
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.google.com/'
                }
                response = requests.get(url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    return self._extract_content(response.content, url)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                continue
        return None
    
    def _download_from_cache(self, url):
        """Method 3: Google Cache"""
        try:
            cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
            headers = {'User-Agent': self.user_agents[0]}
            response = requests.get(cache_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                return self._extract_content(response.content, url)
                
        except Exception as e:
            print(f"    ⚠️ Google Cache failed: {e}")
        return None
    
    def _download_from_archive(self, url):
        """Method 4: Archive.org"""
        try:
            # Get latest snapshot
            api_url = f"https://archive.org/wayback/available?url={url}"
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'archived_snapshots' in data and 'closest' in data['archived_snapshots']:
                    archive_url = data['archived_snapshots']['closest']['url']
                    
                    # Download from archive
                    headers = {'User-Agent': self.user_agents[0]}
                    archive_response = requests.get(archive_url, headers=headers, timeout=30)
                    
                    if archive_response.status_code == 200:
                        return self._extract_content(archive_response.content, url)
                        
        except Exception as e:
            print(f"    ⚠️ Archive.org failed: {e}")
        return None
    
    def _extract_content(self, html_content, url):
        """Extract article content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Try different content selectors
            content = ""
            selectors = ['article', '.content', '.main-content', '#content', 'main']
            
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
            
            # Clean up
            content = ' '.join(content.split())
            
            # Extract title
            title_elem = soup.find('h1') or soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else "No title found"
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'wordCount': len(content.split()),
                'contentLength': len(content),
                'extractedAt': datetime.now().isoformat(),
                'extractionMethod': 'robust_downloader'
            }
            
        except Exception as e:
            print(f"    ⚠️ Content extraction failed: {e}")
            return None


# Expanded source list (Option 2)
EXPANDED_SOURCES = [
    # Government sites (may block)
    "legalaid.vic.gov.au",
    "familycourt.gov.au", 
    "ag.gov.au",
    "lawhandbook.sa.gov.au",
    "lawaccess.nsw.gov.au",
    "familyrelationships.gov.au",
    "justice.gov.au",
    "courts.justice.nsw.gov.au",
    "legalaid.nsw.gov.au",
    "legalaid.qld.gov.au",
    "legalaid.wa.gov.au",
    "legalaid.sa.gov.au",
    
    # Community Legal Centers (less blocking)
    "fclc.org.au",  # Fitzroy Community Legal Centre
    "wlsnsw.org.au",  # Women's Legal Service NSW
    "legalanswers.sl.nsw.gov.au",  # State Library Legal Answers
    "relationships.org.au",  # Relationships Australia
    "mensline.org.au",  # Men's support services
    
    # Legal Information Sites (easier to scrape)
    "gotocourt.com.au",
    "findlaw.com.au",
    "lawhandbook.org.au",
    "legalaid.vic.gov.au",
    "communitylegalwa.org.au",
    
    # Law Firms (public articles)
    "legalvision.com.au",
    "turnerlawyers.com.au",
    "familylawyers.com.au"
]
