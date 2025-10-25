#!/usr/bin/env python3
"""
Standalone Instagram Image Generator using Amazon Nova Canvas
Creates custom images for DadAssist articles and uploads to S3
"""

import boto3
import json
import base64
import sys
import subprocess
from datetime import datetime
import os
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_image_prompt(article_title, article_content=""):
    """Generate Nova Canvas prompt based on article content"""
    
    # Extract key themes from title/content
    legal_themes = {
        'property': 'property settlement, house division, financial assets',
        'child': 'children, parenting, family time, custody',
        'support': 'child support, financial responsibility, payments',
        'violence': 'safety, protection, legal orders, intervention',
        'divorce': 'separation, legal process, court documents',
        'mental': 'wellbeing, support, counseling, mental health'
    }
    
    # Determine theme from title
    title_lower = article_title.lower()
    theme = "professional legal consultation"
    
    for key, description in legal_themes.items():
        if key in title_lower:
            theme = description
            break
    
    prompt = f"""
    Create a professional Instagram post image with text overlay for a legal article.
    
    Background: Clean, modern professional setting related to {theme}
    Style: Professional, trustworthy, approachable
    Colors: Navy blue, white, light gray, gold accents
    
    TEXT OVERLAY REQUIREMENTS:
    - Main heading: "{article_title}" 
    - Font: Bold, professional, highly readable
    - Text color: White or dark navy blue (high contrast)
    - Text placement: Center or upper portion of image
    - Text should be prominent and easy to read on mobile
    
    Background elements: Subtle legal symbols, modern office, professional atmosphere
    Mood: Supportive, expert guidance, family-friendly
    
    Ensure the text "{article_title}" is clearly visible and professionally formatted.
    The image should work well for Instagram posts about Australian family law.
    """
    
    return prompt.strip()

def add_text_overlay(image_data, article_title):
    """Add text overlay to the generated image"""
    
    try:
        # Load image from bytes
        from io import BytesIO
        image = Image.open(BytesIO(image_data))
        
        # Create drawing context
        draw = ImageDraw.Draw(image)
        
        # Try to load a font (fallback to default if not available)
        try:
            font_size = 60
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
            font_size = 40
        
        # Wrap text for better display (15 characters per line)
        wrapper = textwrap.TextWrapper(width=15)
        wrapped_text = wrapper.fill(article_title)
        
        # Get image dimensions
        img_width, img_height = image.size
        
        # Calculate text position (center, upper third)
        lines = wrapped_text.split('\n')
        line_height = font_size + 20  # Increased spacing between lines
        total_text_height = len(lines) * line_height
        
        y_start = img_height // 3 - total_text_height // 2
        
        # Add text without background (translucent effect)
        for i, line in enumerate(lines):
            # Get text dimensions
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (img_width - text_width) // 2
            y = y_start + i * line_height
            
            # Draw text with outline for better visibility (no background rectangle)
            # Draw outline in black
            outline_width = 3
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0, 255))
            
            # Draw white text on top
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        
        # Convert back to bytes
        output = BytesIO()
        image.save(output, format='JPEG', quality=95)
        return output.getvalue()
        
    except Exception as e:
        print(f"⚠️ Text overlay failed: {e}")
        print("📝 Returning original image without text")
        return image_data
def generate_image_with_nova(prompt, output_filename, article_title):
    """Generate image using Amazon Nova Canvas and add text overlay"""
    
    try:
        # Initialize bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Nova Canvas model ID
        model_id = "amazon.nova-canvas-v1:0"
        
        # Prepare request
        request_body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {
                "numberOfImages": 1,
                "height": 1024,
                "width": 1024,
                "cfgScale": 8.0
            }
        }
        
        print(f"🎨 Generating image with Nova Canvas...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Call Nova Canvas
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        if 'images' in response_body and len(response_body['images']) > 0:
            # Decode base64 image
            image_data = base64.b64decode(response_body['images'][0])
            
            print(f"✅ Base image generated successfully")
            print(f"📝 Adding text overlay: {article_title}")
            
            # Add text overlay
            final_image_data = add_text_overlay(image_data, article_title)
            
            # Save locally for testing
            local_path = f"/tmp/{output_filename}"
            with open(local_path, 'wb') as f:
                f.write(final_image_data)
            
            print(f"✅ Final image with text saved: {local_path}")
            return final_image_data, local_path
        else:
            print("❌ No image returned from Nova Canvas")
            return None, None
            
    except Exception as e:
        print(f"❌ Error generating image: {e}")
        return None, None

def upload_to_webserver(image_data, filename):
    """Save image to web server and return public URL"""
    
    try:
        # Ensure directory exists
        import subprocess
        subprocess.run(['sudo', 'mkdir', '-p', '/var/www/dadassist/images/instagram'], check=True)
        
        # Web server path
        web_path = f"/var/www/dadassist/images/instagram/{filename}"
        
        print(f"💾 Saving to web server: {web_path}")
        
        # Save to temporary location first
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'wb') as f:
            f.write(image_data)
        
        # Copy to web server with sudo
        subprocess.run(['sudo', 'cp', temp_path, web_path], check=True)
        
        # Set proper permissions
        subprocess.run(['sudo', 'chown', 'www-data:www-data', web_path], check=True)
        subprocess.run(['sudo', 'chmod', '644', web_path], check=True)
        
        # Generate public URL
        url = f"https://dadassist.com.au/images/instagram/{filename}"
        print(f"🌐 Public URL: {url}")
        
        return url
        
    except Exception as e:
        print(f"❌ Error saving to web server: {e}")
        return None

def main():
    """Main function - can be called from command line or imported"""
    
    if len(sys.argv) < 2:
        print("Usage: python3 generate_instagram_image.py 'Article Title' ['Article Content']")
        print("Example: python3 generate_instagram_image.py 'Property Settlement Guide'")
        return None
    
    article_title = sys.argv[1]
    article_content = sys.argv[2] if len(sys.argv) > 2 else ""
    
    print(f"🚀 Generating Instagram image for: {article_title}")
    
    # Generate filename
    safe_title = "".join(c for c in article_title.lower() if c.isalnum() or c in (' ', '-')).rstrip()
    safe_title = safe_title.replace(' ', '-')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_title}_{timestamp}.jpg"
    
    # Generate prompt
    prompt = generate_image_prompt(article_title, article_content)
    
    # Generate image
    image_data, local_path = generate_image_with_nova(prompt, filename, article_title)
    
    if image_data:
        # Save to web server
        web_url = upload_to_webserver(image_data, filename)
        
        if web_url:
            print(f"🎯 SUCCESS!")
            print(f"📁 Local file: {local_path}")
            print(f"🌐 Web URL: {web_url}")
            return web_url
        else:
            print(f"⚠️ Image generated locally but web server save failed")
            print(f"📁 Local file: {local_path}")
            return local_path
    else:
        print("❌ Image generation failed")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n✅ Final result: {result}")
    else:
        print(f"\n❌ Generation failed")
        sys.exit(1)
