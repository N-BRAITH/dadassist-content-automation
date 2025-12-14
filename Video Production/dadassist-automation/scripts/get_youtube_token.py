#!/usr/bin/env python3
"""Get YouTube OAuth refresh token."""

import json
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

def get_refresh_token():
    """Run OAuth flow to get refresh token."""
    print("🔐 YouTube OAuth Setup")
    print("=" * 50)
    print()
    print("This will open your browser to authorize the app.")
    print("Make sure you downloaded the OAuth credentials JSON file.")
    print()
    
    credentials_file = input("Enter path to credentials JSON file: ").strip()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file,
            SCOPES
        )
        
        # Run local server to handle OAuth callback
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            success_message='Authorization successful! You can close this window.'
        )
        
        print()
        print("✅ Authorization successful!")
        print()
        print("=" * 50)
        print("GitHub Secrets to Add:")
        print("=" * 50)
        print()
        print(f"YOUTUBE_CLIENT_ID:")
        print(f"  {credentials.client_id}")
        print()
        print(f"YOUTUBE_CLIENT_SECRET:")
        print(f"  {credentials.client_secret}")
        print()
        print(f"YOUTUBE_REFRESH_TOKEN:")
        print(f"  {credentials.refresh_token}")
        print()
        print("=" * 50)
        print()
        print("📋 Next Steps:")
        print("1. Go to your GitHub repository")
        print("2. Settings → Secrets and variables → Actions")
        print("3. Click 'New repository secret'")
        print("4. Add each of the three secrets above")
        print()
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {credentials_file}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    get_refresh_token()
