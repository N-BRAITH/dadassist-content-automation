#!/usr/bin/env python3
"""
DadAssist Content Automation - Email Notifier
Sends comprehensive email notifications with run results and instructions
"""

import os
import json
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def get_article_section(article_title, article_content=""):
    """Determine which index section the article belongs to based on content"""
    
    # Define section keywords
    sections = {
        "👨‍👧‍👦 Parenting Arrangements": [
            "parenting", "custody", "child contact", "visitation", "parenting plan", 
            "joint custody", "sole custody", "parenting time", "child arrangements"
        ],
        "🏠 Property Settlement": [
            "property", "assets", "financial", "settlement", "division", "superannuation",
            "binding financial agreement", "prenup", "postnup", "asset protection"
        ],
        "⚖️ Legal Procedures": [
            "court", "legal process", "application", "orders", "mediation", "lawyer",
            "family court", "legal advice", "representation", "proceedings"
        ],
        "💰 Child Support": [
            "child support", "maintenance", "financial support", "payment", "assessment",
            "child support agency", "spousal maintenance", "alimony"
        ],
        "🚨 Family Violence": [
            "family violence", "intervention order", "domestic violence", "protection order",
            "safety", "abuse", "restraining order", "violence"
        ],
        "🧠 Mental Health": [
            "mental health", "wellbeing", "stress", "anxiety", "depression", "counselling",
            "therapy", "support", "emotional", "psychological"
        ],
        "💪 Self Care": [
            "self care", "coping", "resilience", "health", "fitness", "lifestyle",
            "personal development", "recovery", "healing"
        ]
    }
    
    # Combine title and content for analysis
    text_to_analyze = f"{article_title} {article_content}".lower()
    
    # Score each section based on keyword matches
    section_scores = {}
    for section, keywords in sections.items():
        score = sum(1 for keyword in keywords if keyword in text_to_analyze)
        if score > 0:
            section_scores[section] = score
    
    # Return the section with highest score, or default
    if section_scores:
        return max(section_scores, key=section_scores.get)
    else:
        return "⚖️ Legal Procedures"  # Default section

def load_run_summary():
    """Load the run summary created by GitHub Actions"""
    try:
        with open('run_summary.json', 'r') as f:
            summary = json.load(f)
    except FileNotFoundError:
        print("❌ No run summary found, creating basic summary")
        summary = {
            'automation_version': '3.4.0',
            'run_date': datetime.now().isoformat(),
            'success': False,
            'articles_found': 0,
            'quality_articles': 0
        }
    
    # Check environment variables for workflow status
    skip_generation = os.getenv('SKIP_GENERATION', 'false').lower() == 'true'
    workflow_status = os.getenv('WORKFLOW_STATUS', 'unknown')
    article_url = os.getenv('ARTICLE_URL', '')
    article_title = os.getenv('ARTICLE_TITLE', '')
    social_media_results_file = os.getenv('SOCIAL_MEDIA_RESULTS_FILE', '')
    
    # Load social media results if available
    social_media_results = None
    if social_media_results_file and os.path.exists(social_media_results_file):
        try:
            print(f"📱 Loading social media results from: {social_media_results_file}")
            with open(social_media_results_file, 'r') as f:
                social_media_results = json.load(f)
            print(f"✅ Loaded {len(social_media_results.get('results', []))} social media results")
        except Exception as e:
            print(f"⚠️ Could not load social media results: {e}")
    else:
        print(f"⚠️ Social media results file not found: {social_media_results_file}")
    
    # Update summary based on workflow results
    summary['skip_generation'] = skip_generation
    summary['workflow_status'] = workflow_status
    summary['article_url'] = article_url
    summary['article_title'] = article_title
    summary['social_media_results'] = social_media_results
    
    return summary

def create_email_content(summary):
    """Create comprehensive email content with instructions"""
    
    # Determine workflow outcome
    skip_generation = summary.get('skip_generation', False)
    workflow_status = summary.get('workflow_status', 'unknown')
    article_url = summary.get('article_url', '')
    article_title = summary.get('article_title', '')
    
    if skip_generation:
        status = "⚠️ ALL DUPLICATES"
        status_class = "status-failed"
        outcome_message = "All scraped articles were duplicates - no new content generated"
    elif workflow_status == 'success' and article_url:
        status = "✅ SUCCESS"
        status_class = "status-success"
        outcome_message = f"New article generated and posted: {article_title}"
    else:
        status = "❌ FAILED" if not summary.get('success') else "⚠️ PARTIAL"
        status_class = "status-failed"
        outcome_message = "Workflow completed with issues - check logs for details"
    
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
            .warning-box {{ background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 15px 0; }}
            .success-box {{ background-color: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }}
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
            <div class="{'success-box' if status.startswith('✅') else 'warning-box' if status.startswith('⚠️') else 'info-box'}">
                <p><strong>Status:</strong> <span class="{status_class}">{status}</span></p>
                <p><strong>Outcome:</strong> {outcome_message}</p>
                <p><strong>Date:</strong> {datetime.fromisoformat(summary.get('run_date', '')).strftime('%A, %B %d, %Y at %I:%M %p')}</p>
                <p><strong>Automation Version:</strong> v{summary.get('automation_version', '1.0.0')}</p>
                <p><strong>Articles Found:</strong> {articles_found} articles discovered</p>
                <p><strong>Quality Articles:</strong> {quality_articles} articles extracted successfully</p>"""
    
    # Add article-specific information if generated
    if article_url and article_title:
        html_content += f"""
                <p><strong>Generated Article:</strong> <a href="{article_url}">{article_title}</a></p>
                <p><strong>Live URL:</strong> <a href="{article_url}">{article_url}</a></p>"""
    
    html_content += f"""
            </div>"""
    
    # Add social media posting results if available
    social_media_results = summary.get('social_media_results')
    if social_media_results and len(social_media_results) > 0:
        html_content += f"""
            <h2>📱 Social Media Posting Results</h2>
            <div class="info-box">"""
        
        for result in social_media_results:
            if 'posting_results' in result:
                posting_results = result['posting_results']
                article_info = result.get('article', {})
                
                html_content += f"""
                <p><strong>Article:</strong> {article_info.get('title', 'Unknown')}</p>
                <table style="width: 100%; border-collapse: collapse; margin: 10px 0;">
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Platform</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Status</th>
                        <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Post URL</th>
                    </tr>"""
                
                # Twitter results
                twitter_result = posting_results.get('twitter', {})
                if twitter_result:
                    status = "✅ Success" if twitter_result.get('success') else "❌ Failed"
                    error_msg = twitter_result.get('error', '')
                    post_url = twitter_result.get('url', 'N/A')
                    
                    html_content += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">🐦 Twitter</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{status}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">
                            {f'<a href="{post_url}">{post_url}</a>' if post_url != 'N/A' else error_msg}
                        </td>
                    </tr>"""
                
                # Facebook results
                facebook_result = posting_results.get('facebook', {})
                if facebook_result:
                    status = "✅ Success" if facebook_result.get('success') else "❌ Failed"
                    error_msg = facebook_result.get('error', '')
                    post_url = facebook_result.get('url', 'N/A')
                    
                    html_content += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">📘 Facebook</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{status}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">
                            {f'<a href="{post_url}">{post_url}</a>' if post_url != 'N/A' else error_msg}
                        </td>
                    </tr>"""
                
                # Instagram results
                instagram_result = posting_results.get('instagram', {})
                if instagram_result:
                    status = "✅ Success" if instagram_result.get('success') else "❌ Failed"
                    error_msg = instagram_result.get('error', '')
                    post_url = instagram_result.get('url', 'N/A')
                    
                    html_content += f"""
                    <tr>
                        <td style="border: 1px solid #ddd; padding: 8px;">📷 Instagram</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">{status}</td>
                        <td style="border: 1px solid #ddd; padding: 8px;">
                            {f'<a href="{post_url}">{post_url}</a>' if post_url != 'N/A' else error_msg}
                        </td>
                    </tr>"""
                
                html_content += """
                </table>"""
        
        html_content += """
            </div>"""
    
    # Add specific instructions based on outcome
    if skip_generation:
        html_content += f"""
            <h2>🔄 Next Steps (All Articles Were Duplicates)</h2>
            <div class="warning-box">
                <p><strong>What happened:</strong> All scraped articles already exist on DadAssist.com.au</p>
                <p><strong>Next action:</strong> The search rotation will automatically advance to try different queries next week</p>
                <p><strong>Manual option:</strong> You can modify search terms in config/apify_config.json for more variety</p>
            </div>"""
    elif article_url:
        html_content += f"""
            <h2>✅ Article Successfully Generated</h2>
            <div class="success-box">
                <p><strong>New Article:</strong> {article_title}</p>
                <p><strong>Live URL:</strong> <a href="{article_url}">{article_url}</a></p>
                <p><strong>Social Media:</strong> Automatically posted to Twitter, Facebook, and Instagram</p>
            </div>"""
    
    html_content += f"""
            <h2>📥 How to Download This Week's Articles</h2>
            <div class="info-box">
                <div class="step">
                    <span class="step-number">1</span>
                    <strong>Go to GitHub Actions:</strong> 
                    <a href="https://github.com/N-BRAITH/dadassist-content-automation/actions">https://github.com/N-BRAITH/dadassist-content-automation/actions</a>
                </div>
                <div class="step">
                    <span class="step-number">2</span>
                    <strong>Click:</strong> The latest "Complete DadAssist Automation" run
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
                <p><strong>Next Run:</strong> {(datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=(7-datetime.now().weekday()))).strftime('%A, %B %d at 9:00 AM UTC') if datetime.now().weekday() != 0 else 'Next Monday at 9:00 AM UTC'}</p>
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
    
    # Dynamic subject based on outcome
    skip_generation = summary.get('skip_generation', False)
    article_url = summary.get('article_url', '')
    
    if skip_generation:
        subject = "⚠️ DadAssist Automation: All Articles Were Duplicates"
    elif article_url:
        subject = f"✅ DadAssist Automation: New Article Generated - {summary.get('article_title', 'Article')}"
    else:
        subject = f"🤖 DadAssist Automation: {summary.get('quality_articles', 0)} Articles Ready for Review"
    
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    # Create HTML content
    html_content = create_email_content(summary)
    
    # Save email content for debugging
    with open('debug_email_content.html', 'w') as f:
        f.write(html_content)
    print("📧 Email content saved to debug_email_content.html for review")
    
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
    
    # Load run summary (will create basic one if missing)
    summary = load_run_summary()
    
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
