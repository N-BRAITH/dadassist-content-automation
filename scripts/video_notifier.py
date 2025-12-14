#!/usr/bin/env python3
"""Video workflow notification script"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def create_email_content():
    """Create email content from workflow results"""
    
    status = os.getenv('WORKFLOW_STATUS', 'unknown')
    article_url = os.getenv('ARTICLE_URL', 'N/A')
    video_title = os.getenv('VIDEO_TITLE', 'N/A')
    category = os.getenv('VIDEO_CATEGORY', 'N/A')
    youtube_url = os.getenv('YOUTUBE_URL', 'N/A')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if status == 'success':
        status_icon = '✅'
        status_text = 'SUCCESS'
        status_color = '#28a745'
    else:
        status_icon = '❌'
        status_text = 'FAILED'
        status_color = '#dc3545'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 5px; }}
            .content {{ margin-top: 20px; }}
            .info-box {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0; }}
            .label {{ font-weight: bold; color: #495057; }}
            a {{ color: #007bff; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{status_icon} Weekly Video Generation - {status_text}</h1>
            <p>Timestamp: {timestamp}</p>
        </div>
        
        <div class="content">
            <div class="info-box">
                <p><span class="label">Status:</span> {status_text}</p>
                <p><span class="label">Article:</span> <a href="{article_url}">{article_url}</a></p>
                <p><span class="label">Video Title:</span> {video_title}</p>
                <p><span class="label">Category:</span> {category}</p>
                <p><span class="label">YouTube:</span> <a href="{youtube_url}">{youtube_url}</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def send_email():
    """Send notification email via SES"""
    
    sender = os.getenv('SENDER_EMAIL')
    recipient = os.getenv('NOTIFICATION_EMAIL')
    ses_username = os.getenv('SES_USERNAME')
    ses_password = os.getenv('EMAIL_PASSWORD')
    status = os.getenv('WORKFLOW_STATUS', 'unknown')
    
    if not all([sender, recipient, ses_username, ses_password]):
        print("❌ Missing email credentials")
        return
    
    subject = f"{'✅' if status == 'success' else '❌'} DadAssist Weekly Video - {status.upper()}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    html_content = create_email_content()
    msg.attach(MIMEText(html_content, 'html'))
    
    try:
        with smtplib.SMTP('email-smtp.ap-southeast-2.amazonaws.com', 587) as server:
            server.starttls()
            server.login(ses_username, ses_password)
            server.send_message(msg)
        print(f"✅ Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == '__main__':
    send_email()
