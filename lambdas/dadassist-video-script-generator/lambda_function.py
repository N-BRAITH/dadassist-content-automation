import json
import boto3

s3 = boto3.client("s3")
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

INTRO_TEXT = "This video is brought to you by DadAssist. We are an Australian-based organisation supporting fathers through separation and family law matters. Please visit our website for more information or you can find us on Instagram and Facebook. Don't delay. Reach out today for assistance. We hope you enjoy the video."

def lambda_handler(event, context):
    if "body" in event and isinstance(event["body"], str):
        body = json.loads(event["body"])
        s3_path = body.get("s3_path", "")
        category = body.get("category", "")
    else:
        s3_path = event.get("s3_path", "")
        category = event.get("category", "")
    
    if not s3_path.startswith("s3://"):
        return {"statusCode": 400, "body": "Invalid s3_path"}
    
    parts = s3_path.replace("s3://", "").split("/", 1)
    bucket = parts[0]
    key = parts[1]
    execution_id = key.split("/")[0]
    
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        article_data = json.loads(response["Body"].read())
        
        if not category:
            category = article_data.get("category", "")
        
        prompt = f"""Transform this legal article into an engaging video script for Australian fathers.

Article Title: {article_data["title"]}
Article Content: {article_data["content"][:3000]}...

CRITICAL REQUIREMENTS - DO NOT EXCEED WORD LIMIT:
1. Total script MAXIMUM 200 words - DO NOT EXCEED THIS UNDER ANY CIRCUMSTANCES
2. Distribute words across 5 sections (hook, section1, section2, section3, conclusion)
3. Use conversational, supportive tone
4. Speak directly to fathers using "you"
5. Include practical advice and key takeaways
6. End with call to action for DadAssist services
7. Keep language simple and accessible
8. DO NOT include section labels like "hook:", "section1:" in the actual script text
9. Return ONLY the JSON object with no additional text or explanations

Output as JSON:
{{
  "hook": "Opening that grabs attention",
  "section1": "First main point",
  "section2": "Second main point", 
  "section3": "Third main point",
  "conclusion": "Call to action"
}}

REMEMBER: Total words across all sections MUST NOT EXCEED 200 words."""

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response["body"].read())
        enhanced_script = response_body["content"][0]["text"]
        
        import re
        json_match = re.search(r'\{[^{}]*"hook"[^{}]*"section1"[^{}]*"section2"[^{}]*"section3"[^{}]*"conclusion"[^{}]*\}', enhanced_script, re.DOTALL)
        if json_match:
            enhanced_script = json_match.group(0)
        
        try:
            script_json = json.loads(enhanced_script)
        except:
            script_json = {
                "hook": enhanced_script[:200],
                "section1": enhanced_script[200:400],
                "section2": enhanced_script[400:600],
                "section3": enhanced_script[600:800],
                "conclusion": enhanced_script[800:]
            }
        
        script_with_intro = {
            "intro": INTRO_TEXT,
            "hook": script_json["hook"],
            "section1": script_json["section1"],
            "section2": script_json["section2"],
            "section3": script_json["section3"],
            "conclusion": script_json["conclusion"]
        }
        
        script_data = {
            "enhanced_script": script_with_intro,
            "sections": list(script_with_intro.keys()),
            "article_title": article_data["title"],
            "category": category,
            "execution_id": execution_id
        }
        
        s3_key = execution_id + "/script.json"
        s3.put_object(
            Bucket="dadassist-video-work",
            Key=s3_key,
            Body=json.dumps(script_data, indent=2),
            ContentType="application/json"
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Script generated successfully",
                "s3_path": "s3://dadassist-video-work/" + s3_key,
                "category": category,
                "sections": len(script_with_intro)
            })
        }
        
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
