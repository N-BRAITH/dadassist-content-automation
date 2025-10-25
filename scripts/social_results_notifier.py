#!/usr/bin/env python3
"""
DadAssist Social Media Results Notifier
Simple, accurate notification script that reads actual posting results
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_social_media_results():
    """Load social media results from environment variable"""
    results_file = os.getenv('SOCIAL_MEDIA_RESULTS_FILE', '')
    
    if not results_file or not os.path.exists(results_file):
        print(f"❌ No results file found: {results_file}")
        return None
    
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
        print(f"✅ Loaded results from: {results_file}")
        return results
    except Exception as e:
        print(f"❌ Error loading results: {e}")
        return None

def create_email_content(results):
    """Create email content from actual posting results"""
    
    if not results:
        return "<h1>❌ No social media results available</h1>"
    
    # Get article info
    article_results = results.get('results', [])
    if not article_results:
        return "<h1>❌ No articles processed</h1>"
    
    article = article_results[0]['article']
    posting_results = article_results[0]['posting_results']
    
    # Count successes
    successful_posts = sum(1 for post in posting_results if post['success'])
    total_posts = len(posting_results)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #E09900; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .platform {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; }}
            .platform.success {{ border-left: 4px solid #28a745; }}
            .platform.failed {{ border-left: 4px solid #dc3545; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 DadAssist Social Media Report</h1>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </div>

        <div class="success">
            <h2>✅ Social Media Posting Complete</h2>
            <p><strong>Success Rate:</strong> {successful_posts}/{total_posts} ({successful_posts/total_posts*100:.0f}%)</p>
        </div>

        <h2>📖 New Article</h2>
        <div class="platform">
            <p><strong>Title:</strong> {article['title']}</p>
            <p><strong>Filename:</strong> {article.get('filename', 'N/A')}</p>
            <p><strong>Live URL:</strong> <a href="{article['url']}">{article['url']}</a></p>
        </div>

        <h2>🔍 Workflow Details</h2>
        <div class="platform">
            <p><strong>Run Date:</strong> {results.get('run_date', 'N/A')}</p>
            <p><strong>Mode:</strong> {'LIVE POSTING' if not results.get('dry_run', True) else 'DRY RUN'}</p>
            <p><strong>Articles Processed:</strong> {results.get('articles_processed', 0)}</p>
            <p><strong>Search Query Used:</strong> {os.getenv('CURRENT_SEARCH_QUERY', 'Query not available - add to workflow')}</p>
        </div>

        <h2>📱 Social Media Results</h2>
    """
    
    # Add actual posting results
    for post in posting_results:
        platform = post['platform'].title()
        status = "✅ Success" if post['success'] else "❌ Failed"
        status_class = "success" if post['success'] else "failed"
        
        if post['success'] and 'url' in post:
            link = f"<a href='{post['url']}'>{post['url']}</a>"
        elif not post['success'] and 'error' in post:
            link = f"Error: {post['error']}"
        else:
            link = "No details available"
        
        html += f"""
        <div class="platform {status_class}">
            <strong>{platform}:</strong> {status}<br>
            {link}
        </div>
        """
    
    html += """
        <h2>📋 Next Steps</h2>
        <div class="platform">
            <p>✅ Check your social media accounts to see the live posts</p>
            <p>✅ Monitor engagement and clicks to SubmitForm.html</p>
            <p>✅ Next article will be posted next week</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_notification(results):
    """Send email notification"""
    
    # Email config
    sender_email = os.getenv('SENDER_EMAIL', 'admin@dadassist.com.au')
    notification_email = os.getenv('NOTIFICATION_EMAIL')
    email_password = os.getenv('EMAIL_PASSWORD')
    ses_username = os.getenv('SES_USERNAME')
    
    if not notification_email:
        print("❌ No notification email configured")
        return False
    
    # Create email
    html_content = create_email_content(results)
    
    # Determine subject
    if results:
        article_results = results.get('results', [])
        if article_results:
            posting_results = article_results[0]['posting_results']
            successful_posts = sum(1 for post in posting_results if post['success'])
            status = "✅ SUCCESS" if successful_posts > 0 else "❌ FAILED"
            subject = f"🤖 DadAssist Social Media - {status} ({successful_posts} posts)"
        else:
            subject = "🤖 DadAssist Social Media - No Results"
    else:
        subject = "🤖 DadAssist Social Media - Error"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = notification_email
    
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        server = smtplib.SMTP('email-smtp.ap-southeast-2.amazonaws.com', 587)
        server.starttls()
        server.login(ses_username, email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Notification sent to {notification_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False

def main():
    """Main function"""
    print("📧 DadAssist Social Media Results Notifier")
    
    # Load results
    results = load_social_media_results()
    
    # Send notification
    success = send_notification(results)
    
    if success:
        print("✅ Social media notification sent successfully")
    else:
        print("❌ Failed to send notification")

if __name__ == "__main__":
    main()
