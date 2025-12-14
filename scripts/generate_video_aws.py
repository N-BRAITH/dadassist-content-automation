#!/usr/bin/env python3
"""Generate video using AWS Step Functions directly."""

import json
import time
import boto3
import sys

STATE_MACHINE_ARN = 'arn:aws:states:ap-southeast-2:519139471186:stateMachine:dadassist-video-pipeline'

def main():
    with open('selected_url.txt', 'r') as f:
        article_url = f.read().strip()
    
    print(f"🚀 Starting video generation")
    print(f"📝 Article: {article_url}")
    
    stepfunctions = boto3.client('stepfunctions', region_name='ap-southeast-2')
    s3 = boto3.client('s3', region_name='ap-southeast-2')
    
    # Start execution
    response = stepfunctions.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        input=json.dumps({'article_url': article_url})
    )
    
    execution_arn = response['executionArn']
    print(f"⏳ Execution started: {execution_arn.split(':')[-1]}")
    
    # Poll for completion
    for i in range(120):  # 20 minutes max
        time.sleep(10)
        
        exec_response = stepfunctions.describe_execution(executionArn=execution_arn)
        status = exec_response['status']
        
        if i % 6 == 0:  # Print every minute
            print(f"⏱️  Status: {status} ({i//6} min)")
        
        if status == 'SUCCEEDED':
            output = json.loads(exec_response['output'])
            
            if 'body' in output:
                body_data = json.loads(output['body']) if isinstance(output['body'], str) else output['body']
                s3_path = body_data.get('s3_path', '')
            else:
                s3_path = output.get('s3_path', '')
            
            execution_id = s3_path.split('/')[-2] if '/' in s3_path else ''
            
            # Get article data
            article_key = f"{execution_id}/article.json"
            article_obj = s3.get_object(Bucket='dadassist-video-work', Key=article_key)
            article_data = json.loads(article_obj['Body'].read())
            
            title = article_data.get('title', 'DadAssist Video')
            category = article_data.get('category', '')
            
            s3_url = s3_path.replace('s3://dadassist-video-work/', 
                                    'https://dadassist-video-work.s3.ap-southeast-2.amazonaws.com/')
            
            # Write outputs
            with open('s3_url.txt', 'w') as f:
                f.write(s3_url)
            with open('video_title.txt', 'w') as f:
                f.write(title)
            with open('video_category.txt', 'w') as f:
                f.write(category)
            
            print(f"✅ Video generated successfully")
            print(f"📹 Title: {title}")
            print(f"🏷️  Category: {category}")
            return 0
        
        elif status == 'FAILED':
            print(f"❌ Execution failed")
            sys.exit(1)
    
    print(f"❌ Timeout after 20 minutes")
    sys.exit(1)

if __name__ == '__main__':
    main()
