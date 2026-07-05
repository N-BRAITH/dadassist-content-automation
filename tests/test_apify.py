#!/usr/bin/env python3
"""
Test script to verify Apify API token works
"""

import os
import requests

def test_apify_token():
    token = os.getenv('APIFY_TOKEN') or input("Enter Apify API token: ")

    # Test API connection
    url = f"https://api.apify.com/v2/users/me?token={token}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print("✅ Apify API token works!")
            print(f"✅ Connected to organization: {data.get('username', 'Unknown')}")
            return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    test_apify_token()
