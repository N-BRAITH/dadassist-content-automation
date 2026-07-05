import json
import boto3
import subprocess
import os

os.environ['PATH'] = '/opt/bin:' + os.environ['PATH']
s3 = boto3.client('s3')

def lambda_handler(event, context):
    """Create intro/outro slides from logo with proper text positioning"""
    
    slide_type = event.get('type', 'intro')
    duration = event.get('duration', 5)  # seconds
    
    # Download logo
    logo_path = '/tmp/logo.png'
    s3.download_file('dadassist-video-library', 'intro_outro/logo_with_website.png', logo_path)
    
    # Create video from logo image with text overlay
    output_path = f'/tmp/{slide_type}_new.mp4'
    
    # Create 5-second video from static image with centered text at bottom
    subprocess.run([
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', logo_path,
        '-vf', f"scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,drawtext=text='www.dadassist.com.au':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=h-120:box=1:boxcolor=black@0.7:boxborderw=30",
        '-c:v', 'libx264',
        '-t', str(duration),
        '-pix_fmt', 'yuv420p',
        '-r', '25',
        output_path
    ], check=True, capture_output=True)
    
    # Upload
    output_key = f"fix/{slide_type}_new.mp4"
    s3.upload_file(output_path, 'dadassist-video-work', output_key)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f'Created {slide_type}',
            's3_path': f"s3://dadassist-video-work/{output_key}"
        })
    }
