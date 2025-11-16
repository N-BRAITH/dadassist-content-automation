#!/usr/bin/env python3
"""
Analyze video library and create metadata for intelligent matching
"""
import json
import os

def create_video_metadata():
    """Create metadata for each video in the library"""
    
    # Video metadata based on Pexels content analysis
    video_metadata = {
        "pexels_8061655.mp4": {
            "themes": ["business meeting", "professional discussion", "corporate"],
            "mood": "serious",
            "setting": "office",
            "people": "multiple",
            "keywords": ["meeting", "discussion", "professional", "business", "corporate", "legal"]
        },
        "pexels_7735488.mp4": {
            "themes": ["handshake", "agreement", "partnership"],
            "mood": "positive",
            "setting": "office",
            "people": "two",
            "keywords": ["handshake", "agreement", "partnership", "deal", "cooperation"]
        },
        "pexels_8135731.mp4": {
            "themes": ["consultation", "advice", "guidance"],
            "mood": "supportive",
            "setting": "office",
            "people": "two",
            "keywords": ["consultation", "advice", "guidance", "help", "support"]
        },
        "pexels_6101325.mp4": {
            "themes": ["family", "father child", "parenting"],
            "mood": "emotional",
            "setting": "home",
            "people": "family",
            "keywords": ["family", "father", "child", "parenting", "relationship", "care"]
        },
        "pexels_3738655.mp4": {
            "themes": ["legal documents", "paperwork", "contracts"],
            "mood": "focused",
            "setting": "office",
            "people": "single",
            "keywords": ["documents", "paperwork", "legal", "contracts", "forms"]
        },
        "pexels_4812264.mp4": {
            "themes": ["court", "justice", "legal system"],
            "mood": "formal",
            "setting": "courthouse",
            "people": "multiple",
            "keywords": ["court", "justice", "legal", "formal", "system", "law"]
        },
        "pexels_8747881.mp4": {
            "themes": ["stress", "pressure", "difficulty"],
            "mood": "tense",
            "setting": "office",
            "people": "single",
            "keywords": ["stress", "pressure", "difficulty", "challenge", "problem"]
        },
        "pexels_6565218.mp4": {
            "themes": ["resolution", "solution", "success"],
            "mood": "positive",
            "setting": "office",
            "people": "multiple",
            "keywords": ["resolution", "solution", "success", "achievement", "positive"]
        },
        "pexels_3326745.mp4": {
            "themes": ["communication", "phone call", "contact"],
            "mood": "active",
            "setting": "office",
            "people": "single",
            "keywords": ["communication", "phone", "contact", "call", "discussion"]
        },
        "pexels_5713278.mp4": {
            "themes": ["planning", "strategy", "preparation"],
            "mood": "thoughtful",
            "setting": "office",
            "people": "single",
            "keywords": ["planning", "strategy", "preparation", "thinking", "organize"]
        }
    }
    
    return video_metadata

def match_content_to_videos(article_content, video_metadata):
    """Use Bedrock to analyze content and match with best videos"""
    
    # Content analysis prompt for Bedrock
    analysis_prompt = f"""
    Analyze this family law article content and identify the 10 most relevant video themes in sequence:
    
    Article Content: {article_content[:2000]}...
    
    Available video themes:
    {json.dumps({k: v['keywords'] for k, v in video_metadata.items()}, indent=2)}
    
    Return a JSON array of the 10 best matching video filenames in the order they should appear, 
    considering the emotional flow and content progression of the article.
    
    Consider:
    1. Content relevance to keywords
    2. Emotional progression (start supportive, show challenges, end positive)
    3. Visual variety (different settings/people)
    4. Narrative flow
    
    Format: ["video1.mp4", "video2.mp4", ...]
    """
    
    return analysis_prompt

if __name__ == "__main__":
    metadata = create_video_metadata()
    print("Video metadata created:")
    print(json.dumps(metadata, indent=2))
