#!/usr/bin/env python3
import json
import sys
sys.path.append('scripts')
from social_results_notifier import create_email_content

# Load the actual JSON file
with open('/Users/user/Downloads/social-media/results/posting_results_20251025_114301.json', 'r') as f:
    results = json.load(f)

# Generate HTML
html = create_email_content(results)
print(html)
