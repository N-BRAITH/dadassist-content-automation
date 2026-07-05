import json
import boto3
import time

stepfunctions = boto3.client('stepfunctions')
s3 = boto3.client('s3')

STATE_MACHINE_ARN = 'arn:aws:states:ap-southeast-2:519139471186:stateMachine:dadassist-video-pipeline'

def lambda_handler(event, context):
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        article_url = body.get('article_url')
        
        if not article_url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'article_url is required'})
            }
        
        # Start Step Functions execution
        print(f"Starting execution for: {article_url}")
        
        response = stepfunctions.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=json.dumps({'article_url': article_url})
        )
        
        execution_arn = response['executionArn']
        print(f"Execution started: {execution_arn}")
        
        # Wait for completion (poll every 10 seconds, max 10 minutes)
        for i in range(60):
            time.sleep(10)
            
            exec_response = stepfunctions.describe_execution(executionArn=execution_arn)
            status = exec_response['status']
            
            print(f"Status check {i+1}: {status}")
            
            if status == 'SUCCEEDED':
                # Parse output to get S3 path
                output = json.loads(exec_response['output'])
                
                if 'body' in output:
                    body_data = json.loads(output['body']) if isinstance(output['body'], str) else output['body']
                    s3_path = body_data.get('s3_path', '')
                else:
                    s3_path = output.get('s3_path', '')
                
                # Extract execution_id from S3 path
                execution_id = s3_path.split('/')[-2] if '/' in s3_path else ''
                
                # Get article data for title and category
                article_key = f"{execution_id}/article.json"
                try:
                    article_obj = s3.get_object(Bucket='dadassist-video-work', Key=article_key)
                    article_data = json.loads(article_obj['Body'].read())
                    title = article_data.get('title', 'DadAssist Video')
                    category = article_data.get('category', '')
                except:
                    title = 'DadAssist Video'
                    category = ''
                
                # Convert S3 path to public URL
                s3_url = s3_path.replace('s3://dadassist-video-work/', 
                                        'https://dadassist-video-work.s3.ap-southeast-2.amazonaws.com/')
                
                return {
                    'statusCode': 200,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'status': 'success',
                        's3_url': s3_url,
                        'title': title,
                        'category': category,
                        'execution_id': execution_id,
                        'article_url': article_url
                    })
                }
            
            elif status == 'FAILED':
                return {
                    'statusCode': 500,
                    'headers': {'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'status': 'failed',
                        'error': 'Step Functions execution failed'
                    })
                }
        
        # Timeout after 10 minutes
        return {
            'statusCode': 504,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'timeout',
                'error': 'Video generation took longer than 10 minutes'
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'error': str(e)
            })
        }
