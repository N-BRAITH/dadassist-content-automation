import json
import boto3
import requests
from bs4 import BeautifulSoup

# Version 1.1 - Added HTML-based category extraction from post-meta div
s3 = boto3.client('s3')

def lambda_handler(event, context):
    article_url = event.get('article_url', '')
    
    if not article_url:
        return {'statusCode': 400, 'body': json.dumps({'error': 'No article_url provided'})}
    
    try:
        response = requests.get(article_url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        title_element = soup.find('h1', class_='post-title')
        title = title_element.get_text().strip() if title_element else 'DadAssist Article'
        
        content_element = soup.find('div', class_='post-content')
        if content_element:
            content = content_element.get_text()
        else:
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        content = content.replace('\n\n\n', '\n\n').strip()
        
        # Extract category from post-meta div
        category = ''
        meta_element = soup.find('div', class_='post-meta')
        if meta_element:
            meta_text = meta_element.get_text()
            if 'Category:' in meta_text:
                category_text = meta_text.split('Category:')[1].split('|')[0].strip()
                
                # Map display names to internal format
                category_map = {
                    'Parenting & Custody': 'parenting',
                    'Legal Procedures': 'legal',
                    'Child Support': 'child_support',
                    'Family Violence': 'family_violence',
                    'Property Settlement': 'property_settlement',
                    'Mental Health': 'mental_health',
                    'Conflict Resolution': 'conflict_resolution'
                }
                category = category_map.get(category_text, 'legal')
        
        import uuid
        execution_id = str(uuid.uuid4())
        
        article_data = {
            'title': title,
            'content': content,
            'url': article_url,
            'category': category,
            'word_count': len(content.split()),
            'char_count': len(content),
            'timestamp': str(context.invoked_function_arn),
            'execution_id': execution_id
        }
        
        s3_key = execution_id + '/article.json'
        s3.put_object(
            Bucket='dadassist-video-work',
            Key=s3_key,
            Body=json.dumps(article_data, indent=2),
            ContentType='application/json'
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Article fetched successfully',
                's3_path': 's3://dadassist-video-work/' + s3_key,
                'title': title,
                'execution_id': execution_id
            })
        }
        
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
