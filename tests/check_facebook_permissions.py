#!/usr/bin/env python3
"""Check Facebook access token permissions."""

import os
import requests
import json

# Get credentials
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID') or input("Enter Facebook Page ID: ")
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN') or input("Enter Facebook Access Token: ")

print("="*60)
print("🔍 Facebook Token Permission Checker")
print("="*60)

# 1. Check token info
print("\n📋 Checking token information...")
url = "https://graph.facebook.com/v18.0/me"
params = {'access_token': FACEBOOK_ACCESS_TOKEN}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Token is valid")
    print(f"   Token belongs to: {data.get('name', 'Unknown')}")
    print(f"   ID: {data.get('id', 'Unknown')}")
else:
    print(f"❌ Token is invalid: {response.json()}")
    exit(1)

# 2. Check token permissions
print("\n🔐 Checking token permissions...")
url = "https://graph.facebook.com/v18.0/me/permissions"
params = {'access_token': FACEBOOK_ACCESS_TOKEN}

response = requests.get(url, params=params)

if response.status_code == 200:
    permissions = response.json().get('data', [])
    
    granted = [p['permission'] for p in permissions if p['status'] == 'granted']
    declined = [p['permission'] for p in permissions if p['status'] == 'declined']
    
    print(f"\n✅ Granted permissions ({len(granted)}):")
    for perm in sorted(granted):
        print(f"   • {perm}")
    
    if declined:
        print(f"\n❌ Declined permissions ({len(declined)}):")
        for perm in sorted(declined):
            print(f"   • {perm}")
    
    # Check for video-specific permissions
    print("\n📹 Video upload requirements:")
    required = ['pages_manage_posts', 'pages_read_engagement']
    
    for req in required:
        if req in granted:
            print(f"   ✅ {req}")
        else:
            print(f"   ❌ {req} - MISSING!")
    
    if all(req in granted for req in required):
        print("\n✅ Token has all required permissions for video uploads!")
    else:
        print("\n⚠️  Token is missing required permissions for video uploads")
        print("   You need to regenerate the token with these permissions:")
        for req in required:
            if req not in granted:
                print(f"   • {req}")
else:
    print(f"❌ Failed to check permissions: {response.json()}")

# 3. Check page access
print("\n📄 Checking page access...")
url = f"https://graph.facebook.com/v18.0/{FACEBOOK_PAGE_ID}"
params = {'access_token': FACEBOOK_ACCESS_TOKEN}

response = requests.get(url, params=params)

if response.status_code == 200:
    page_data = response.json()
    print(f"✅ Can access page: {page_data.get('name', 'Unknown')}")
    print(f"   Page ID: {page_data.get('id', 'Unknown')}")
else:
    print(f"❌ Cannot access page: {response.json()}")

print("\n" + "="*60)
print("✅ Permission check complete")
print("="*60)
