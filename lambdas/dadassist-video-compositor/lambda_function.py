import json
import boto3
import subprocess
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    if 'statusCode' in event and 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        s3_path = body.get('s3_path', '')
    else:
        s3_path = event.get('s3_path', '')
    
    if not s3_path or not s3_path.startswith('s3://'):
        return {'statusCode': 400, 'body': json.dumps({'error': 'Invalid s3_path'})}
    
    parts = s3_path.replace('s3://', '').split('/', 1)
    bucket, key = parts[0], parts[1]
    execution_id = key.split('/')[0]
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        audio_data = json.loads(response['Body'].read())
        
        article_key = execution_id + '/article.json'
        article_response = s3.get_object(Bucket=bucket, Key=article_key)
        article_data = json.loads(article_response['Body'].read())
        category = article_data.get('category', '')
        
        category_map = {
            'parenting': 'parenting_backing.mp4',
            'legal': 'legal_backing.mp4',
            'property_settlement': 'property_settlement_backing.mp4',
            'mental_health': 'mental_health_backing.mp4',
            'family_violence': 'family_violence_backing.mp4',
            'child_support': 'child_support_backing.mp4',
            'conflict_resolution': 'conflict_resolution_backing.mp4'
        }
        
        backing_video_file = category_map.get(category, 'legal_backing.mp4')
        backing_video_key = 'backing-videos/' + backing_video_file
        
        local_video = '/tmp/background.mp4'
        s3.download_file('dadassist-video-library', backing_video_key, local_video)
        
        audio_key = audio_data['audio_files'][0]['s3_key']
        local_audio = '/tmp/audio.mp3'
        s3.download_file(bucket, audio_key, local_audio)
        
        silent_start = '/tmp/silent_start.mp3'
        subprocess.run(['/opt/bin/ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', '4', '-q:a', '9', '-acodec', 'libmp3lame', silent_start], capture_output=True, check=True)
        
        silent_pause = '/tmp/silent_pause.mp3'
        subprocess.run(['/opt/bin/ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', '4', '-q:a', '9', '-acodec', 'libmp3lame', silent_pause], capture_output=True, check=True)
        
        silent_end = '/tmp/silent_end.mp3'
        subprocess.run(['/opt/bin/ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', '4', '-q:a', '9', '-acodec', 'libmp3lame', silent_end], capture_output=True, check=True)
        
        audio_concat_list = '/tmp/audio_concat.txt'
        with open(audio_concat_list, 'w') as f:
            f.write(f"file '{silent_start}'\n")
            f.write(f"file '{silent_pause}'\n")
            f.write(f"file '{local_audio}'\n")
            f.write(f"file '{silent_end}'\n")
        
        full_audio = '/tmp/full_audio.mp3'
        subprocess.run(['/opt/bin/ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', audio_concat_list, '-c', 'copy', full_audio], capture_output=True, check=True)
        
        output_video = '/tmp/output.mp4'
        subprocess.run(['/opt/bin/ffmpeg', '-y', '-i', local_video, '-i', full_audio, '-c:v', 'copy', '-c:a', 'aac', '-map', '0:v:0', '-map', '1:a:0', output_video], capture_output=True, check=True)
        
        video_key = execution_id + '/video_no_captions.mp4'
        s3.upload_file(output_video, bucket, video_key)
        
        file_size = os.path.getsize(output_video) / (1024 * 1024)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Video composed',
                'video_s3_path': 's3://' + bucket + '/' + video_key,
                'execution_id': execution_id,
                'file_size_mb': round(file_size, 2)
            })
        }
        
    except Exception as e:
        print(f'ERROR: {str(e)}')
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
