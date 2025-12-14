#!/usr/bin/env python3
"""Generate Instagram image using template images with text overlay."""

import sys
import os
import random
import glob
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import subprocess

TEMPLATE_BASE = "/var/www/dadassist/images/instagram/templates"

def add_text_overlay(image_data, article_title):
    """Add article title text overlay to image."""
    try:
        image = Image.open(BytesIO(image_data))
        draw = ImageDraw.Draw(image)
        
        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Prepare text
        max_width = image.width - 100
        words = article_title.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate position
        line_height = 70
        total_height = len(lines) * line_height
        y = (image.height - total_height) // 2
        
        # Draw text with shadow
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (image.width - text_width) // 2
            
            # Shadow
            draw.text((x+3, y+3), line, font=font, fill=(0, 0, 0, 180))
            # Main text
            draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
            
            y += line_height
        
        # Save to bytes
        output = BytesIO()
        image.save(output, format='JPEG', quality=95)
        return output.getvalue()
        
    except Exception as e:
        print(f"⚠️ Text overlay failed: {e}")
        return image_data

def select_template(category):
    """Select random template image from category folder."""
    
    # Map category names
    category_map = {
        'parenting': 'parenting',
        'legal': 'legal',
        'property_settlement': 'property_settlement',
        'mental_health': 'mental_health',
        'family_violence': 'family_violence',
        'child_support': 'child_support',
        'conflict_resolution': 'conflict_resolution',
        'general_legal': 'legal'  # fallback
    }
    
    folder_name = category_map.get(category, 'legal')
    template_folder = f"{TEMPLATE_BASE}/{folder_name}"
    
    # Get all jpg files in folder
    templates = glob.glob(f"{template_folder}/*.jpg")
    
    if not templates:
        print(f"⚠️ No templates found in {template_folder}, using legal")
        templates = glob.glob(f"{TEMPLATE_BASE}/legal/*.jpg")
    
    if not templates:
        print(f"❌ No templates found at all!")
        return None
    
    # Select random template
    selected = random.choice(templates)
    print(f"🎨 Selected template: {os.path.basename(selected)}")
    
    return selected

def upload_to_webserver(image_data, filename):
    """Save image to web server and return public URL."""
    
    try:
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
    """Main function."""
    
    if len(sys.argv) < 3:
        print("Usage: python3 generate_instagram_image_templates.py 'Article Title' 'filename.jpg' ['category']")
        return None
    
    article_title = sys.argv[1]
    filename = sys.argv[2]
    category = sys.argv[3] if len(sys.argv) > 3 else 'legal'
    
    print(f"📝 Article: {article_title}")
    print(f"📁 Filename: {filename}")
    print(f"🏷️  Category: {category}")
    
    # Select template
    template_path = select_template(category)
    
    if not template_path:
        print("❌ No template available")
        return None
    
    # Load template
    with open(template_path, 'rb') as f:
        template_data = f.read()
    
    # Add text overlay
    final_image = add_text_overlay(template_data, article_title)
    
    # Upload to web server
    web_url = upload_to_webserver(final_image, filename)
    
    if web_url:
        print(f"🎯 SUCCESS!")
        print(f"🌐 Web URL: {web_url}")
        return web_url
    else:
        print("❌ Upload failed")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(result)
