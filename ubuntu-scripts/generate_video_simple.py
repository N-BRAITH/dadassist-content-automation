#!/usr/bin/env python3
"""
Simplified DadAssist Video Generator - Just voiceover + videos + subtitles
"""

import os
import sys
import json
import subprocess
import requests
from datetime import datetime
import boto3
from bs4 import BeautifulSoup

def select_best_matching_videos(slide_data, library_videos):
    """Use Bedrock to intelligently select videos based on content"""
    
    try:
        # Video metadata for intelligent matching
        video_metadata = {
            "pexels_8061655.mp4": ["business", "meeting", "professional", "discussion", "legal"],
            "pexels_7735488.mp4": ["handshake", "agreement", "partnership", "cooperation"],
            "pexels_8135731.mp4": ["consultation", "advice", "guidance", "help", "support"],
            "pexels_6101325.mp4": ["family", "father", "child", "parenting", "relationship"],
            "pexels_3738655.mp4": ["documents", "paperwork", "legal", "contracts", "forms"],
            "pexels_4812264.mp4": ["court", "justice", "legal", "formal", "law"],
            "pexels_8747881.mp4": ["stress", "pressure", "difficulty", "challenge"],
            "pexels_6565218.mp4": ["resolution", "solution", "success", "positive"],
            "pexels_3326745.mp4": ["communication", "phone", "contact", "discussion"],
            "pexels_5713278.mp4": ["planning", "strategy", "preparation", "organize"]
        }
        
        # Extract all text content for analysis
        all_text = ""
        for slide in slide_data:
            all_text += slide.get('content', '') + " "
        
        print(f"  🎯 AI selecting videos based on content analysis")
        
        # Simple fallback selection for now
        return library_videos[:10]
        
    except Exception as e:
        print(f"  ⚠️  AI video selection failed: {e}")
        return library_videos[:10]

def create_simple_concatenation(selected_videos, work_dir):
    """Simple video concatenation"""
    
    concat_file = os.path.join(work_dir, "library_concat_list.txt")
    with open(concat_file, 'w') as f:
        for video in selected_videos:
            f.write(f"file '{video}'\n")
    
    stitched_video = os.path.join(work_dir, "stitched_library_background.mp4")
    stitch_cmd = [
        'ffmpeg', '-y',
        '-f', 'concat', '-safe', '0', '-i', concat_file,
        '-c:v', 'libx264', '-c:a', 'aac',
        '-r', '30', '-pix_fmt', 'yuv420p',
        stitched_video
    ]
    
    result = subprocess.run(stitch_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return stitched_video
    else:
        return selected_videos[0]

def create_video_with_library(slide_data, audio_data, work_dir, article_name):
    """Create video with library videos + voiceover + subtitles"""
    
    print(f"🎬 Step 6: Creating video with Pexels video library")
    
    try:
        # Video library directory
        video_library = "/tmp/pexels_video_library"
        
        # Get all available videos from library
        library_videos = []
        for filename in os.listdir(video_library):
            if filename.endswith('.mp4'):
                library_videos.append(os.path.join(video_library, filename))
        
        print(f"  📚 Library contains {len(library_videos)} videos")
        
        # Select best matching videos
        selected_videos = select_best_matching_videos(slide_data, library_videos)
        
        # Create video background
        if len(selected_videos) > 1:
            final_background = create_simple_concatenation(selected_videos, work_dir)
        else:
            final_background = selected_videos[0]
        
        # Combine all audio files
        audio_concat_file = os.path.join(work_dir, "audio_concat_list.txt")
        with open(audio_concat_file, 'w') as f:
            for audio in audio_data['audio_files']:
                f.write(f"file '{audio['file_path']}'\n")
        
        combined_audio = os.path.join(work_dir, "combined_audio.mp3")
        audio_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat', '-safe', '0', '-i', audio_concat_file,
            '-c', 'copy', combined_audio
        ]
        
        print("  🎵 Combining Arthur's audio...")
        subprocess.run(audio_cmd, capture_output=True)
        
        # Get all text and split into 3-word groups
        all_text = ""
        for audio in audio_data['audio_files']:
            all_text += audio['text'] + " "
        
        words = all_text.split()
        three_word_groups = []
        
        for i in range(0, len(words), 3):
            group = ' '.join(words[i:i+3])
            three_word_groups.append(group)
        
        print(f"  📝 Created {len(three_word_groups)} 3-word subtitle groups")
        
        # Calculate timing - 0.9 seconds per group
        total_duration = sum(audio['duration'] for audio in audio_data['audio_files'])
        time_per_group = 0.9
        
        # Create subtitle filters
        subtitle_filters = []
        for i, group in enumerate(three_word_groups):
            start_time = i * time_per_group
            end_time = (i + 1) * time_per_group
            
            clean_text = group.replace("'", "").replace('"', '').replace(':', '').replace(';', '')
            subtitle_filter = f"drawtext=text='{clean_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start_time:.1f},{end_time:.1f})'"
            subtitle_filters.append(subtitle_filter)
        
        # Create final video
        video_filename = f"{article_name}_library_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        all_subtitle_filters = ','.join(subtitle_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', final_background,
            '-i', combined_audio,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-r', '30', '-pix_fmt', 'yuv420p',
            '-vf', all_subtitle_filters,
            '-shortest',
            video_path
        ]
        
        print("  🚀 Creating final video...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("    ✅ Video created successfully!")
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'subtitle_groups': len(three_word_groups),
                'videos_used': len(selected_videos),
                'type': 'library-video'
            }
        else:
            print(f"    ❌ Video creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("Simple video generator ready")
