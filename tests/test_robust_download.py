#!/usr/bin/env python3
"""
Test the robust downloader with a real URL
"""

import sys
sys.path.insert(0, 'scripts')

from robust_downloader import RobustDownloader

# Test with a government site that often blocks
test_url = "https://www.familycourt.gov.au/wps/wcm/connect/fcoaweb/family-law-matters/parenting-arrangements/parenting-orders/parenting-orders"

print("🧪 Testing Robust Downloader")
print("=" * 60)
print(f"Test URL: {test_url}")
print("=" * 60)

downloader = RobustDownloader()
result = downloader.download_article(test_url, "Test Article")

if result:
    print("\n✅ SUCCESS!")
    print(f"Title: {result['title']}")
    print(f"Word Count: {result['wordCount']}")
    print(f"Content Length: {result['contentLength']}")
    print(f"Method: {result.get('extractionMethod', 'unknown')}")
    print(f"\nFirst 200 chars of content:")
    print(result['content'][:200] + "...")
else:
    print("\n❌ FAILED - All methods exhausted")
