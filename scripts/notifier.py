#!/usr/bin/env python3
"""
DadAssist Content Automation - Email Notifier
Sends comprehensive email notifications with run results and instructions
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def load_run_summary():
    """Load the run summary created by GitHub Actions"""
    try:
        with open('run_summary.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No run summary found")
        return None

def create_email_content(summary):
    """Create comprehensive email content with instructions"""
    
    # Determine status
    status = "✅ SUCCESS" if summary.get('success') else "❌ FAILED"
    articles_found = summary.get('articles_found', 0)
    quality_articles = summary.get('quality_articles', 0)
    
    # Create HTML email content
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .status-success {{ color: #28a745; font-weight: bold; }}
            .status-failed {{ color: #dc3545; font-weight: bold; }}
            .info-box {{ background-color: #f8f9fa; border-left: 4px solid #2c5aa0; padding: 15px; margin: 15px 0; }}
            .code {{ background-color: #f1f1f1; padding: 2px 5px; font-family: monospace; }}
            .step {{ margin: 10px 0; }}
            .step-number {{ background-color: #2c5aa0; color: white; border-radius: 50%; padding: 5px 10px; margin-right: 10px; }}
            ul {{ margin: 10px 0; padding-left: 20px; }}
            li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 DadAssist Content Automation Report</h1>
            <p>Weekly Legal Content Scraping Results (v{summary.get('automation_version', '1.0.0')})</p>
        </div>
        
        <div class="content">
            <h2>📊 Run Summary</h2>
            <div class="info-box">
                <p><strong>Status:</strong> <span class="{'status-success' if summary.get('success') else 'status-failed'}">{status}</span></p>
                <p><strong>Date:</strong> {datetime.fromisoformat(summary.get('run_date', '')).strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                <p><strong>Automation Version:</strong> v{summary.get('automation_version', '1.0.0')}</p>
                <p><strong>Config Updated:</strong> {summary.get('config_last_updated', 'Unknown')}</p>
                <p><strong>Articles Found:</strong> {articles_found} articles discovered</p>
                <p><strong>Quality Articles:</strong> {quality_articles} articles extracted successfully</p>
                <p><strong>Extraction Method:</strong> {summary.get('extraction_method', 'Unknown')}</p>
                <p><strong>Email Provider:</strong> {summary.get('smtp_provider', 'amazon_ses').replace('_', ' ').title()}</p>
            </div>

            <h2>🔍 Search Configuration Used</h2>
            <div class="info-box">
                <p><strong>Search Terms:</strong></p>
                <p class="code">{summary.get('search_terms', 'Not available')}</p>
                
                <p><strong>Target Sites Searched:</strong></p>
                <ul>
    """
    
    # Add target sites
    for site in summary.get('target_sites', []):
        html_content += f"<li>{site}</li>"
    
    html_content += f"""
                </ul>
            </div>

            <h2>📂 Content Categories Found</h2>
            <div class="info-box">
    """
    
    # Add categories if available
    categories = summary.get('categories', {})
    if categories:
        for category, count in categories.items():
            category_name = category.replace('_', ' ').title()
            html_content += f"<p><strong>{category_name}:</strong> {count} articles</p>"
    else:
        html_content += "<p>No categorized content available</p>"
    
    html_content += f"""
            </div>

            <h2>📥 How to Download This Week's Articles</h2>
            <div class="info-box">
                <div class="step">
                    <span class="step-number">1</span>
                    <strong>Go to GitHub Actions:</strong> 
                    <a href="https://github.com/N-BRAITH/dadassist-content-automation/actions">https://github.com/N-BRAITH/dadassist-content-automation/actions</a>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <strong>Click:</strong> The latest "Weekly Legal Content Scraping" run
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <strong>Download:</strong> "extracted-articles" artifact (ZIP file)
                </div>
                <div class="step">
                    <span class="step-number">4</span>
                    <strong>Extract:</strong> ZIP file to your Mac desktop
                </div>
                <div class="step">
                    <span class="step-number">5</span>
                    <strong>Process:</strong> Use Q Developer to convert JSON to DadAssist HTML
                </div>
            </div>

            <h2>⚙️ How to Change Search Criteria</h2>
            <div class="info-box">
                <div class="step">
                    <span class="step-number">1</span>
                    <strong>Go to Repository:</strong> 
                    <a href="https://github.com/N-BRAITH/dadassist-content-automation">https://github.com/N-BRAITH/dadassist-content-automation</a>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <strong>Edit File:</strong> Click on <span class="code">config/apify_config.json</span>
                </div>
                <div class="step">
                    <span class="step-number">3</span>
                    <strong>Modify Settings:</strong>
                    <ul>
                        <li><strong>Search Terms:</strong> Change <span class="code">"search_queries"</span> for different topics</li>
                        <li><strong>Target Sites:</strong> Add/remove websites in <span class="code">"target_sites"</span></li>
                        <li><strong>Article Count:</strong> Adjust <span class="code">"max_articles_per_run"</span></li>
                        <li><strong>Quality Filters:</strong> Modify <span class="code">"min_word_count"</span></li>
                    </ul>
                </div>
                <div class="step">
                    <span class="step-number">4</span>
                    <strong>Commit Changes:</strong> Click "Commit changes" button
                </div>
                <div class="step">
                    <span class="step-number">5</span>
                    <strong>Next Run:</strong> Monday's automation will use your new settings
                </div>
            </div>

            <h2>💡 Example Search Configurations</h2>
            <div class="info-box">
                <p><strong>Focus on Divorce/Property:</strong></p>
                <p class="code">"property settlement divorce Australia OR asset division fathers OR spousal maintenance guide"</p>
                
                <p><strong>Mental Health Focus:</strong></p>
                <p class="code">"fathers mental health separation OR depression divorce men Australia OR wellbeing fathers"</p>
                
                <p><strong>Child Support Focus:</strong></p>
                <p class="code">"child support assessment Australia OR CSA fathers OR child support calculator guide"</p>
                
                <p><strong>Family Violence Focus:</strong></p>
                <p class="code">"family violence intervention orders OR domestic violence fathers OR FVIO applications Australia"</p>
            </div>

            <h2>📞 Support Information</h2>
            <div class="info-box">
                <p><strong>Repository:</strong> <a href="https://github.com/N-BRAITH/dadassist-content-automation">dadassist-content-automation</a></p>
                <p><strong>Schedule:</strong> Every Monday at 9:00 AM UTC</p>
                <p><strong>Retention:</strong> Artifacts kept for 30 days</p>
                <p><strong>Next Run:</strong> {(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + datetime.timedelta(days=(7-datetime.now().weekday()))).strftime('%A, %B %d at 9:00 AM UTC') if datetime.now().weekday() != 0 else 'Next Monday at 9:00 AM UTC'}</p>
            </div>

            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                <p>This is an automated message from DadAssist Content Automation System.</p>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

def send_email_notification(summary):
    """Send email notification using Microsoft 365 SMTP"""
    
    # Email configuration
    smtp_server = "email-smtp.ap-southeast-2.amazonaws.com"
    smtp_port = 587
    ses_username = os.getenv('SES_USERNAME')
    sender_password = os.getenv('EMAIL_PASSWORD')
    sender_email = os.getenv('SENDER_EMAIL', 'admin@dadassist.com.au')
    recipient_email = os.getenv('NOTIFICATION_EMAIL')
    
    if not sender_password or not ses_username:
        print("❌ SES credentials not found in environment variables")
        return False
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🤖 DadAssist Automation: {summary.get('quality_articles', 0)} Articles Ready for Review"
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Create HTML content
    html_content = create_email_content(summary)
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        # Send email
        print(f"📧 Sending notification to {recipient_email}...")
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(ses_username, sender_password)
        server.send_message(msg)
        server.quit()
        
        print("✅ Email notification sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    """Main notification function"""
    print("📧 Starting email notification system...")
    
    # Load run summary
    summary = load_run_summary()
    if not summary:
        print("❌ No run summary available for notification")
        return False
    
    # Send email notification
    success = send_email_notification(summary)
    
    if success:
        print("✅ Notification system completed successfully!")
    else:
        print("❌ Notification system failed")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
