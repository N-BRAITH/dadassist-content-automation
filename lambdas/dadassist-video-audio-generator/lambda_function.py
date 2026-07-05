import json
import boto3
import subprocess
import os

s3 = boto3.client('s3')
polly = boto3.client('polly', region_name='us-east-1')

def lambda_handler(event, context):
    if 'body' in event and isinstance(event['body'], str):
        body = json.loads(event['body'])
        s3_path = body.get('s3_path', '')
    else:
        s3_path = event.get('s3_path', '')
    
    if not s3_path.startswith('s3://'):
        return {'statusCode': 400, 'body': 'Invalid s3_path'}
    
    parts = s3_path.replace('s3://', '').split('/', 1)
    bucket = parts[0]
    key = parts[1]
    execution_id = key.split('/')[0]
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        script_data = json.loads(response['Body'].read())
        
        audio_files = []
        total_duration = 0
        temp_files = []
        
        for i, section_name in enumerate(script_data['sections']):
            section_text = script_data['enhanced_script'].get(section_name, '')
            
            if not section_text:
                continue
            
            ssml_text = '<speak><prosody rate="slow">' + section_text + '</prosody></speak>'
            
            response = polly.synthesize_speech(
                Text=ssml_text,
                OutputFormat='mp3',
                VoiceId='Arthur',
                Engine='neural',
                TextType='ssml'
            )
            
            temp_file = f'/tmp/{section_name}_audio.mp3'
            with open(temp_file, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            temp_files.append(temp_file)
            
            if section_name == 'intro':
                pause_file = '/tmp/pause_after_intro.mp3'
                subprocess.run(['ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=r=22050:cl=mono', '-t', '3', '-q:a', '9', '-acodec', 'libmp3lame', pause_file], capture_output=True, check=True)
                temp_files.append(pause_file)
                total_duration += 3
            
            word_count = len(section_text.split())
            estimated_duration = (word_count / 150) * 60
            total_duration += estimated_duration
            
            audio_files.append({
                'section': section_name,
                'duration': estimated_duration,
                'word_count': word_count,
                'text': section_text
            })
        
        concat_file = '/tmp/audio_concat.txt'
        with open(concat_file, 'w') as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
        
        combined_audio = '/tmp/combined_audio.mp3'
        result = subprocess.run(
            ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file, '-c', 'copy', combined_audio],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            raise Exception(f'Audio concat failed: {result.stderr[:200]}')
        
        combined_key = execution_id + '/audio/combined.mp3'
        s3.upload_file(combined_audio, bucket, combined_key)
        
        audio_data = {
            'audio_files': [{
                'section': 'combined',
                's3_key': combined_key,
                'duration': total_duration
            }],
            'total_duration': total_duration,
            'execution_id': execution_id
        }
        
        audio_metadata_key = execution_id + '/audio_metadata.json'
        s3.put_object(
            Bucket=bucket,
            Key=audio_metadata_key,
            Body=json.dumps(audio_data, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Audio generated with 3s pause after intro',
                's3_path': 's3://' + bucket + '/' + audio_metadata_key,
                'total_duration': total_duration
            })
        }
        
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
