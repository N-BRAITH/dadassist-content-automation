import json
import boto3
import time
import re

s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

def offset_srt_timestamps(srt_content, offset_seconds):
    def offset_timestamp(match):
        time_str = match.group(0)
        h, m, s_ms = time_str.split(':')
        s, ms = s_ms.split(',')
        total_ms = int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)
        total_ms += int(offset_seconds * 1000)
        new_h = total_ms // 3600000
        new_m = (total_ms % 3600000) // 60000
        new_s = (total_ms % 60000) // 1000
        new_ms = total_ms % 1000
        return f"{new_h:02d}:{new_m:02d}:{new_s:02d},{new_ms:03d}"
    
    return re.sub(r'\d{2}:\d{2}:\d{2},\d{3}', offset_timestamp, srt_content)

def lambda_handler(event, context):
    if 'statusCode' in event and 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        video_path = body.get('video_s3_path')
        execution_id = body.get('execution_id')
    else:
        video_path = event.get('video_s3_path')
        execution_id = event.get('execution_id')
    
    if not video_path or not execution_id:
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing video_s3_path or execution_id'})}
    
    audio_path = f"s3://dadassist-video-work/{execution_id}/audio/combined.mp3"
    
    parts = video_path.replace('s3://', '').split('/', 1)
    bucket = parts[0]
    
    try:
        job_name = f"caption-{execution_id}"
        
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_path},
            MediaFormat='mp3',
            LanguageCode='en-AU',
            Subtitles={'Formats': ['srt'], 'OutputStartIndex': 1}
        )
        
        for _ in range(60):
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = response['TranscriptionJob']['TranscriptionJobStatus']
            
            if status == 'COMPLETED':
                srt_url = response['TranscriptionJob']['Subtitles']['SubtitleFileUris'][0]
                
                import urllib.request
                with urllib.request.urlopen(srt_url) as resp:
                    srt_content = resp.read().decode('utf-8')
                
                srt_content = re.sub(r'\bda assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdad assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdent assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdat assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdata assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdatasist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdebt assist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                srt_content = re.sub(r'\bdadassist\b', 'DadAssist', srt_content, flags=re.IGNORECASE)
                
                srt_content = offset_srt_timestamps(srt_content, 8.0)
                
                srt_key = f"{execution_id}/captions.srt"
                s3.put_object(
                    Bucket=bucket,
                    Key=srt_key,
                    Body=srt_content,
                    ContentType='text/plain'
                )
                
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Captions generated with 8s offset',
                        'video_s3_path': video_path,
                        'srt_s3_path': f"s3://{bucket}/{srt_key}"
                    })
                }
            
            elif status == 'FAILED':
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': 'Transcription job failed'})
                }
            
            time.sleep(5)
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Transcription timeout'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
