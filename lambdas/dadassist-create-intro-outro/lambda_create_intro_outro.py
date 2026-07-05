import boto3
import subprocess
import os

os.environ['PATH'] = '/opt/bin:' + os.environ['PATH']
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Download assets
    s3.download_file('dadassist-video-library', 'intro_outro/logo_with_website.png', '/tmp/logo.png')
    s3.download_file('dadassist-video-library', 'intro_outro/intro_audio.mp3', '/tmp/intro_audio.mp3')
    
    # Create intro video (logo + audio)
    intro_cmd = [
        'ffmpeg', '-loop', '1', '-i', '/tmp/logo.png',
        '-i', '/tmp/intro_audio.mp3',
        '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-shortest', '-y', '/tmp/intro.mp4'
    ]
    result = subprocess.run(intro_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {'statusCode': 500, 'body': f'Intro error: {result.stderr}'}
    
    s3.upload_file('/tmp/intro.mp4', 'dadassist-video-library', 'intro_outro/intro.mp4')
    
    # Create outro video (3 seconds with fade)
    outro_cmd = [
        'ffmpeg', '-loop', '1', '-i', '/tmp/logo.png', '-t', '3',
        '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,fade=in:0:30',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23', '-pix_fmt', 'yuv420p',
        '-an', '-y', '/tmp/outro.mp4'
    ]
    result = subprocess.run(outro_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return {'statusCode': 500, 'body': f'Outro error: {result.stderr}'}
    
    s3.upload_file('/tmp/outro.mp4', 'dadassist-video-library', 'intro_outro/outro.mp4')
    
    return {'statusCode': 200, 'body': 'Created intro/outro with white text on transparent logo'}
