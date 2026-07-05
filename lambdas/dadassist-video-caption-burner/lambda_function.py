import json
import boto3
import subprocess
import os

os.environ['PATH'] = '/opt/bin:' + os.environ['PATH']

s3 = boto3.client('s3')

def lambda_handler(event, context):
    if 'statusCode' in event and 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        video_path = body.get('video_s3_path') or body.get('s3_path')
        srt_path = body.get('srt_s3_path')
    else:
        video_path = event.get('video_s3_path') or event.get('s3_path')
        srt_path = event.get('srt_s3_path')
    
    if not video_path or not srt_path:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing video_s3_path or srt_s3_path'})}
    
    try:
        video_parts = video_path.replace('s3://', '').split('/', 1)
        video_bucket, video_key = video_parts[0], video_parts[1]
        
        srt_parts = srt_path.replace('s3://', '').split('/', 1)
        srt_bucket, srt_key = srt_parts[0], srt_parts[1]
        
        local_video = '/tmp/input_video.mp4'
        local_srt = '/tmp/captions.srt'
        s3.download_file(video_bucket, video_key, local_video)
        s3.download_file(srt_bucket, srt_key, local_srt)
        
        output_video = '/tmp/captioned_video.mp4'
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', local_video,
            '-vf', f"subtitles={local_srt}:force_style='FontName=Arial Bold,FontSize=24,PrimaryColour=&HFFFFFF,Alignment=2,MarginV=30'",
            '-c:v', 'libx264', '-c:a', 'copy',
            '-preset', 'fast', '-crf', '23',
            output_video
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return {'statusCode': 500, 'body': json.dumps({'error': f'FFmpeg failed: {result.stderr[:500]}'})}
        
        execution_id = video_key.split('/')[0]
        output_key = f"{execution_id}/final_video_captioned.mp4"
        s3.upload_file(output_video, video_bucket, output_key)
        
        file_size = os.path.getsize(output_video) / (1024 * 1024)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Captions added successfully',
                's3_path': f"s3://{video_bucket}/{output_key}",
                'file_size_mb': round(file_size, 2)
            })
        }
        
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
