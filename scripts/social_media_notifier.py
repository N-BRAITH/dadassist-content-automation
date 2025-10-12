#!/usr/bin/env python3
"""
DadAssist Social Media Automation - Posting Results Notifier
Sends comprehensive email notifications with social media posting results
Uses same architecture as existing content automation notifier
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import glob

def load_latest_posting_results():
    """Load the latest social media posting results"""
    try:
        # Find the most recent results file
        results_files = glob.glob('social-media/results/posting_results_*.json')
        if not results_files:
            print("❌ No posting results found")
            return None
        
        latest_file = max(results_files, key=os.path.getctime)
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading posting results: {e}")
        return None

def create_social_media_email_content(results):
    """Create comprehensive email content with social media posting results"""
    
    # Determine overall status
    total_attempts = results.get('total_posts_attempted', 0)
    successful_posts = sum(
        sum(1 for post_result in article['posting_results'] if post_result['success'])
        for article in results['results']
    )
    
    status = "✅ SUCCESS" if successful_posts > 0 else "❌ FAILED"
    success_rate = (successful_posts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get posting details
    articles_processed = results.get('articles_processed', 0)
    run_mode = "DRY RUN" if results.get('dry_run', True) else "LIVE POSTING"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #E09900, #FF7F00); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 20px; }}
            .status-success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .status-failed {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .info-box {{ background: #e8f4f8; border: 1px solid #bee5eb; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .warning-box {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .stats {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .stat {{ text-align: center; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            .stat-number {{ font-size: 24px; font-weight: bold; color: #E09900; }}
            .platform-results {{ margin: 20px 0; }}
            .platform {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #E09900; }}
            .success {{ border-left-color: #28a745; }}
            .failed {{ border-left-color: #dc3545; }}
            .post-content {{ background: #ffffff; padding: 10px; margin: 10px 0; border: 1px solid #dee2e6; border-radius: 3px; font-family: monospace; font-size: 12px; }}
            .step {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }}
            .step-number {{ background: #E09900; color: white; padding: 5px 10px; border-radius: 50%; margin-right: 10px; font-weight: bold; }}
            .code {{ background: #f1f3f4; padding: 2px 6px; border-radius: 3px; font-family: monospace; }}
            a {{ color: #E09900; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 DadAssist Social Media Automation Report</h1>
            <p>Social Media Posting Results - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </div>

        <div class="{'status-success' if successful_posts > 0 else 'status-failed'}">
            <h2>{status} - Social Media Posting Complete</h2>
            <p><strong>Mode:</strong> {run_mode}</p>
            <p><strong>Articles Processed:</strong> {articles_processed}</p>
            <p><strong>Posts Attempted:</strong> {total_attempts}</p>
            <p><strong>Successful Posts:</strong> {successful_posts}</p>
            <p><strong>Success Rate:</strong> {success_rate:.1f}%</p>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">{articles_processed}</div>
                <div>Articles</div>
            </div>
            <div class="stat">
                <div class="stat-number">{successful_posts}</div>
                <div>Successful Posts</div>
            </div>
            <div class="stat">
                <div class="stat-number">{success_rate:.0f}%</div>
                <div>Success Rate</div>
            </div>
        </div>

        <h2>📊 Platform Results</h2>
        <div class="platform-results">
    """
    
    # Add platform-specific results
    platform_stats = {'twitter': 0, 'facebook': 0, 'instagram': 0}
    platform_urls = {'twitter': [], 'facebook': [], 'instagram': []}
    
    for article_result in results['results']:
        article_title = article_result['article']['title']
        article_url = article_result['article'].get('url', 'URL not available')
        
        html_content += f"""
        <div class="platform">
            <h3>📖 {article_title}</h3>
            <p><strong>📄 DadAssist Article:</strong> <a href="{article_url}">{article_url}</a></p>
        """
        
        for post_result in article_result['posting_results']:
            platform = post_result['platform']
            success = post_result['success']
            
            if success:
                platform_stats[platform] += 1
                if 'url' in post_result:
                    platform_urls[platform].append(post_result['url'])
            
            status_class = 'success' if success else 'failed'
            status_icon = '✅' if success else '❌'
            
            html_content += f"""
            <div class="platform {status_class}">
                <strong>{status_icon} {platform.title()}</strong>
                {f"- <a href='{post_result.get('url', '#')}'>View Post</a>" if success and 'url' in post_result else ''}
                {f"- Error: {post_result.get('error', 'Unknown error')}" if not success else ''}
            </div>
            """
        
        # Show post content preview
        if 'posts_generated' in article_result:
            html_content += "<h4>📝 Generated Content Preview:</h4>"
            for platform, post_data in article_result['posts_generated'].items():
                if platform != 'tiktok':  # Skip TikTok for now
                    content_preview = post_data['content'][:100] + "..." if len(post_data['content']) > 100 else post_data['content']
                    html_content += f"""
                    <div class="post-content">
                        <strong>{platform.title()}:</strong> {content_preview}
                        <br><small>Hashtags: {', '.join(post_data['hashtags'])}</small>
                    </div>
                    """
        
        html_content += "</div>"
    
    # Add article summary with URLs
    html_content += f"""
        <h2>📚 Articles Posted</h2>
        <div class="info-box">
            <p><strong>DadAssist Knowledge Base Articles Promoted:</strong></p>
            <ul>
    """
    
    for article_result in results['results']:
        article_title = article_result['article']['title']
        article_url = article_result['article'].get('url', '#')
        article_filename = article_result['article'].get('filename', 'unknown')
        
        html_content += f"""
                <li>
                    <strong>{article_title}</strong><br>
                    <small>File: {article_filename}</small><br>
                    <a href="{article_url}">{article_url}</a>
                </li>
        """
    
    html_content += """
            </ul>
        </div>
    """
    
    # Add platform summary
    html_content += f"""
        </div>

        <h2>🎯 Platform Summary</h2>
        <div class="info-box">
            <p><strong>Twitter:</strong> {platform_stats['twitter']} posts successful</p>
            <p><strong>Facebook:</strong> {platform_stats['facebook']} posts successful</p>
            <p><strong>Instagram:</strong> {platform_stats['instagram']} posts successful</p>
        </div>
    """
    
    # Add live post links if available
    if any(platform_urls.values()) and not results.get('dry_run', True):
        html_content += """
        <h2>🔗 Live Post Links</h2>
        <div class="info-box">
        """
        
        for platform, urls in platform_urls.items():
            if urls:
                html_content += f"<p><strong>{platform.title()}:</strong></p><ul>"
                for url in urls:
                    html_content += f'<li><a href="{url}">{url}</a></li>'
                html_content += "</ul>"
        
        html_content += "</div>"
    
    # Add troubleshooting section if there are failures
    failed_posts = sum(
        sum(1 for post_result in article['posting_results'] if not post_result['success'])
        for article in results['results']
    )
    
    if failed_posts > 0:
        html_content += f"""
        <h2>🔧 Troubleshooting Failed Posts</h2>
        <div class="warning-box">
            <p><strong>⚠️ {failed_posts} posts failed.</strong> Common causes and solutions:</p>
        </div>

        <h3>🔑 Update API Credentials</h3>
        <div class="info-box">
            <p><strong>If posts failed due to authentication errors, update your GitHub Secrets:</strong></p>
            
            <div class="step">
                <span class="step-number">1</span>
                <strong>Go to GitHub Secrets:</strong> 
                <a href="https://github.com/N-BRAITH/dadassist-content-automation/settings/secrets/actions">Repository Secrets</a>
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <strong>Update Twitter Credentials:</strong>
                <ul>
                    <li><span class="code">TWITTER_API_KEY</span> - Get from <a href="https://developer.twitter.com/en/portal/dashboard">Twitter Developer Portal</a></li>
                    <li><span class="code">TWITTER_API_SECRET</span> - API Secret Key</li>
                    <li><span class="code">TWITTER_ACCESS_TOKEN</span> - Access Token</li>
                    <li><span class="code">TWITTER_ACCESS_SECRET</span> - Access Token Secret</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <strong>Update Facebook/Instagram Credentials:</strong>
                <ul>
                    <li><span class="code">FACEBOOK_ACCESS_TOKEN</span> - Get from <a href="https://developers.facebook.com/tools/explorer/">Facebook Graph API Explorer</a></li>
                    <li><span class="code">FACEBOOK_PAGE_ID</span> - DadAssist Facebook Page ID</li>
                    <li><span class="code">INSTAGRAM_ACCOUNT_ID</span> - @dadassist Instagram Account ID</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">4</span>
                <strong>Refresh Facebook Token (Every 60 Days):</strong>
                <ul>
                    <li>Go to <a href="https://developers.facebook.com/tools/explorer/">Facebook Graph API Explorer</a></li>
                    <li>Select your DadAssist app</li>
                    <li>Generate new Page Access Token</li>
                    <li>Update <span class="code">FACEBOOK_ACCESS_TOKEN</span> secret</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">5</span>
                <strong>Test Credentials:</strong>
                <ul>
                    <li>Run: <span class="code">python3 scripts/social_media_poster.py --dry-run --sample</span></li>
                    <li>Check for authentication success messages</li>
                    <li>If still failing, verify API permissions and account status</li>
                </ul>
            </div>
        </div>

        <h3>📋 Platform-Specific Issues</h3>
        <div class="info-box">
            <div class="step">
                <span class="step-number">🐦</span>
                <strong>Twitter Issues:</strong>
                <ul>
                    <li><strong>Rate Limit:</strong> Free tier allows 17 tweets per 24 hours</li>
                    <li><strong>Content Policy:</strong> Avoid duplicate content or spam-like posts</li>
                    <li><strong>Account Status:</strong> Ensure @dad_assist account is in good standing</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">📘</span>
                <strong>Facebook Issues:</strong>
                <ul>
                    <li><strong>Token Expiry:</strong> Page tokens expire every 60 days - refresh regularly</li>
                    <li><strong>Page Permissions:</strong> Ensure app has pages_manage_posts permission</li>
                    <li><strong>Content Policy:</strong> Check Facebook community standards compliance</li>
                </ul>
            </div>
            
            <div class="step">
                <span class="step-number">📷</span>
                <strong>Instagram Issues:</strong>
                <ul>
                    <li><strong>Image Required:</strong> Instagram posts need images - check default image URL</li>
                    <li><strong>Business Account:</strong> Ensure @dadassist is connected to Facebook page</li>
                    <li><strong>Content Guidelines:</strong> Follow Instagram community guidelines</li>
                </ul>
            </div>
        </div>

        <h3>🆘 Emergency Credential Reset</h3>
        <div class="warning-box">
            <p><strong>If all platforms are failing:</strong></p>
            <ol>
                <li><strong>Check GitHub Secrets:</strong> Ensure all 7 secrets are properly set</li>
                <li><strong>Regenerate All Tokens:</strong> Create fresh API credentials</li>
                <li><strong>Test Manually:</strong> Use Q Developer to test individual platform posting</li>
                <li><strong>Contact Support:</strong> Reach out to platform support if issues persist</li>
            </ol>
        </div>
        """
    
    # Add next steps
    html_content += f"""
        <h2>📋 Next Steps</h2>
        <div class="info-box">
            <div class="step">
                <span class="step-number">1</span>
                <strong>Review Results:</strong> Check the success rate and any failed posts above
            </div>
            <div class="step">
                <span class="step-number">2</span>
                <strong>View Live Posts:</strong> Visit your social media accounts to see the posts
                <ul>
                    <li><strong>Twitter:</strong> <a href="https://twitter.com/dad_assist">@dad_assist</a></li>
                    <li><strong>Facebook:</strong> <a href="https://facebook.com/DadAssist">DadAssist Page</a></li>
                    <li><strong>Instagram:</strong> <a href="https://instagram.com/dadassist">@dadassist</a></li>
                </ul>
            </div>
            <div class="step">
                <span class="step-number">3</span>
                <strong>Check Original Articles:</strong> Verify the DadAssist articles being promoted
                <ul>"""
    
    for article_result in results['results']:
        article_title = article_result['article']['title']
        article_url = article_result['article'].get('url', '#')
        html_content += f"""
                    <li><a href="{article_url}">{article_title}</a></li>"""
    
    html_content += f"""
                </ul>
            </div>
            <div class="step">
                <span class="step-number">4</span>
                <strong>Monitor Engagement:</strong> Track likes, comments, and clicks on SubmitForm.html links
            </div>
            <div class="step">
                <span class="step-number">5</span>
                <strong>Queue Management:</strong> {articles_processed - successful_posts//3} articles remaining in queue
            </div>
        </div>

        <h2>⚙️ Automation Settings</h2>
        <div class="info-box">
            <p><strong>Repository:</strong> <a href="https://github.com/N-BRAITH/dadassist-content-automation">dadassist-content-automation</a></p>
            <p><strong>Workflow:</strong> Social Media Posts (Tuesday 6 PM UTC)</p>
            <p><strong>Mode:</strong> {run_mode}</p>
            <p><strong>Platforms:</strong> Twitter, Facebook, Instagram (TikTok disabled)</p>
        </div>

        <div class="warning-box">
            <p><strong>📧 This is an automated report from your DadAssist social media system.</strong></p>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_social_media_notification(results):
    """Send email notification with social media posting results"""
    
    # Email configuration (using same setup as existing notifier)
    sender_email = os.getenv('SENDER_EMAIL', 'noreply@dadassist.com.au')
    notification_email = os.getenv('NOTIFICATION_EMAIL')
    email_password = os.getenv('EMAIL_PASSWORD')
    ses_username = os.getenv('SES_USERNAME')
    
    if not notification_email:
        print("❌ No notification email configured")
        return False
    
    # Create email content
    html_content = create_social_media_email_content(results)
    
    # Determine subject based on results
    successful_posts = sum(
        sum(1 for post_result in article['posting_results'] if post_result['success'])
        for article in results['results']
    )
    
    run_mode = "DRY RUN" if results.get('dry_run', True) else "LIVE"
    status = "✅ SUCCESS" if successful_posts > 0 else "❌ FAILED"
    
    subject = f"🤖 DadAssist Social Media Report - {status} ({run_mode}) - {successful_posts} posts"
    
    # Create email message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = notification_email
    
    # Add HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        # Send via Amazon SES (same as existing notifier)
        server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com', 587)
        server.starttls()
        server.login(ses_username, email_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Social media notification sent to {notification_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")
        return False

def main():
    """Main notification function"""
    print("📧 DadAssist Social Media Notification System")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    
    # Load posting results
    results = load_latest_posting_results()
    if not results:
        print("❌ No posting results to notify about")
        return
    
    # Send notification
    success = send_social_media_notification(results)
    
    if success:
        print("✅ Social media notification sent successfully")
    else:
        print("❌ Failed to send social media notification")

if __name__ == "__main__":
    main()
