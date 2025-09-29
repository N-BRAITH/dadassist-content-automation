#!/usr/bin/env python3
"""
Debug script to test filtering logic with real Apify results
"""

import requests
import json

# Sample results from Apify
sample_results = [
    {
        "title": "Parenting Orders Handbook",
        "url": "https://www.familyrelationships.gov.au/sites/default/files/documents/2021-11/186-parenting-orders-what-you.pdf",
        "description": "If there are no court orders about parental responsibility, each parent ordinarily has parental responsibility for the child."
    },
    {
        "title": "Family Law – Parenting Arrangements for Children After ...",
        "url": "https://www.ag.gov.au/families-and-marriage/publications/family-law-parenting-arrangements-children-after-separation-fact-sheet",
        "description": "In Western Australia, the Family Law Act only applies to children of married or previously married parents."
    },
    {
        "title": "Fathers' Rights Australia - A Quick Guide",
        "url": "https://www.avokahlegal.com.au/fathers-rights-australia/",
        "description": "Many fathers wonder about their legal rights and responsibilities regarding custody and parenting arrangements after separation."
    }
]

def test_filtering():
    """Test the filtering logic"""
    
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
    
    target_sites = [
        "legalaid.vic.gov.au",
        "familycourt.gov.au", 
        "ag.gov.au",
        "lawhandbook.sa.gov.au",
        "lawaccess.nsw.gov.au"
    ]
    
    filtered_urls = []
    
    for item in sample_results:
        url = item.get('url', '')
        title = item.get('title', '')
        description = item.get('description', '')
        
        print(f"\n--- Testing: {title[:50]}...")
        print(f"URL: {url}")
        
        # Filter by trusted domains OR target sites
        domain_match = any(domain in url for domain in trusted_domains + target_sites)
        print(f"Domain match: {domain_match}")
        
        # Check if it's likely a legal article
        legal_keywords = ['family', 'child', 'custody', 'support', 'law', 'court', 'legal', 
                         'parenting', 'divorce', 'separation', 'intervention', 'order']
        
        title_relevant = len(title) > 10 and any(keyword in title.lower() for keyword in legal_keywords)
        desc_relevant = any(keyword in description.lower() for keyword in legal_keywords)
        
        print(f"Title relevant: {title_relevant}")
        print(f"Description relevant: {desc_relevant}")
        
        if domain_match and (title_relevant or desc_relevant):
            print("✅ PASSED FILTER")
            filtered_urls.append(item)
        else:
            print("❌ FAILED FILTER")
    
    print(f"\n🎯 Final result: {len(filtered_urls)} articles passed filtering")
    for i, item in enumerate(filtered_urls, 1):
        print(f"  {i}. {item['title']}")

if __name__ == "__main__":
    test_filtering()
