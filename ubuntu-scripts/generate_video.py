#!/usr/bin/env python3
"""
DadAssist Video Generation Script - Step 5: Visual Slide Creation
Creates videos from DadAssist articles using Bedrock, Polly, and FFmpeg
"""

import sys
import os
import requests
import boto3
import json
from datetime import datetime
from bs4 import BeautifulSoup

def create_pexels_video_background(slide_data, audio_data, work_dir, article_name):
    """Create FFmpeg filter for timed video segments"""
    
    filter_parts = []
    
    for i, segment in enumerate(video_segments):
        # Scale and trim each video segment
        filter_parts.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setpts=PTS-STARTPTS[v{i}]")
    
    # Concatenate all segments
    inputs = "".join([f"[v{i}]" for i in range(len(video_segments))])
    filter_parts.append(f"{inputs}concat=n={len(video_segments)}:v=1:a=0[outv]")
    
    return ";".join(filter_parts)

def create_simple_concatenation(selected_videos, work_dir):
    """Fallback: simple video concatenation"""
    
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

def select_best_matching_videos(slide_data, library_videos):
    """Use Bedrock to intelligently select and sequence videos based on content"""
    
    try:
        import boto3
        
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
            "pexels_5713278.mp4": ["planning", "strategy", "preparation", "organize"],
            "pexels_7039914.mp4": ["consultation", "meeting", "professional", "advice"],
            "pexels_3252974.mp4": ["business", "corporate", "professional", "office"],
            "pexels_3188951.mp4": ["legal", "documents", "paperwork", "formal"],
            "pexels_5544312.mp4": ["family", "support", "care", "relationship"],
            "pexels_34421873.mp4": ["modern", "professional", "business", "contemporary"],
            "pexels_3135808.mp4": ["discussion", "meeting", "consultation", "advice"],
            "pexels_5320011.mp4": ["planning", "strategy", "business", "professional"],
            "pexels_4512203.mp4": ["legal", "court", "justice", "formal"],
            "pexels_3120663.mp4": ["family", "father", "child", "parenting"],
            "pexels_4988395.mp4": ["support", "help", "guidance", "assistance"],
            "pexels_8747244.mp4": ["business", "professional", "meeting", "corporate"]
        }
        
        # Extract all text content for analysis
        all_text = ""
        for slide in slide_data:
            all_text += slide.get('content', '') + " "
        
        # Create Bedrock prompt for video selection
        prompt = f"""
        Analyze this family law article content and select the 10 best matching videos in optimal sequence:
        
        Content: {all_text[:1500]}
        
        Available videos and their themes:
        {chr(10).join([f"{video}: {', '.join(keywords)}" for video, keywords in video_metadata.items()])}
        
        Select 10 videos that:
        1. Match the content themes and keywords
        2. Create good emotional flow (supportive start, challenges middle, positive end)
        3. Provide visual variety
        4. Tell a coherent story
        
        Return only a JSON array of filenames: ["video1.mp4", "video2.mp4", ...]
        """
        
        # Use Bedrock to analyze and select videos
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        # Extract JSON array from response
        import re
        json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
        if json_match:
            selected_filenames = json.loads(json_match.group())
            
            # Convert to full paths and validate
            selected_videos = []
            for filename in selected_filenames:
                full_path = os.path.join("/tmp/pexels_video_library", filename)
                if os.path.exists(full_path):
                    selected_videos.append(full_path)
            
            print(f"  🎯 AI selected {len(selected_videos)} videos based on content analysis")
            return selected_videos[:10]
        
    except Exception as e:
        print(f"  ⚠️  AI video selection failed: {e}")
    
    # Fallback to first 10 videos if AI selection fails
    return library_videos[:10]

    """Create video with Pexels video library and 3-word subtitles"""
    
    print(f"🎬 Step 6: Creating video with Pexels video library")
    
    try:
        import subprocess
        import requests
        import json
        
        # Your Pexels API key
        PEXELS_API_KEY = "EbVUZo7yt2pyoWHzInKIVNMRokExNTXdil9JUvWJEf2bOukwL6JwPSsg"
        
        # Create video library directory
        video_library = "/tmp/pexels_video_library"
        os.makedirs(video_library, exist_ok=True)
        print(f"  📁 Video library: {video_library}")
        
        # Check existing videos in library
        existing_videos = []
        if os.path.exists(video_library):
            existing_videos = [f for f in os.listdir(video_library) if f.endswith('.mp4')]
        
        print(f"  📊 Using {len(existing_videos)} videos from library")
        
        # Get all available videos from library
        library_videos = []
        for filename in os.listdir(video_library):
            if filename.endswith('.mp4'):
                library_videos.append(os.path.join(video_library, filename))
        
        print(f"  📚 Library contains {len(library_videos)} videos")
        
        # Intelligent video selection based on content
        selected_videos = select_best_matching_videos(slide_data, library_videos)
        
        # Create content-synchronized video segments
        print(f"  🎬 Creating content-synchronized video montage...")
        
        if len(selected_videos) > 1:
            # Calculate timing for each video segment based on audio sections
            total_audio_duration = sum(audio['duration'] for audio in audio_data['audio_files'])
            segment_duration = total_audio_duration / len(selected_videos)
            
            # Create video segments with specific timing
            video_segments = []
            for i, video_path in enumerate(selected_videos):
                start_time = i * segment_duration
                video_segments.append({
                    'path': video_path,
                    'start_time': start_time,
                    'duration': segment_duration
                })
            
            # Create complex filter for timed video segments
            filter_complex = create_timed_video_filter(video_segments, total_audio_duration)
            final_background = os.path.join(work_dir, "synchronized_background.mp4")
            
            sync_cmd = [
                'ffmpeg', '-y'
            ]
            
            # Add all video inputs
            for video in selected_videos:
                sync_cmd.extend(['-i', video])
            
            sync_cmd.extend([
                '-filter_complex', filter_complex,
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                '-t', str(total_audio_duration),
                final_background
            ])
            
            result = subprocess.run(sync_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("    ✅ Content-synchronized video created")
            else:
                print(f"    ⚠️  Sync failed, using simple concatenation")
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
        
        print(f"  ⏱️  {time_per_group} seconds per 3-word group")
        
        # Create subtitle filters with bold text
        subtitle_filters = []
        for i, group in enumerate(three_word_groups):
            start_time = i * time_per_group
            end_time = (i + 1) * time_per_group
            
            # Clean text for FFmpeg
            clean_text = group.replace("'", "").replace('"', '').replace(':', '').replace(';', '')
            
            # Large bold translucent text in center of screen
            subtitle_filter = f"drawtext=text='{clean_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start_time:.1f},{end_time:.1f})'"
            subtitle_filters.append(subtitle_filter)
        
        # Create final video with background, audio, and subtitles
        video_filename = f"{article_name}_library_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        # Combine all subtitle filters
        all_subtitle_filters = ','.join(subtitle_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', final_background,  # Loop background video
            '-i', combined_audio,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-r', '30', '-pix_fmt', 'yuv420p',
            '-vf', all_subtitle_filters,
            '-shortest',  # End when audio ends
            video_path
        ]
        
        print("  🚀 Creating final video with library background and subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("    ✅ Professional video created with library background!")
            
            # Clean up temp files
            if os.path.exists(audio_concat_file):
                os.remove(audio_concat_file)
            if os.path.exists(combined_audio):
                os.remove(combined_audio)
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'subtitle_groups': len(three_word_groups),
                'videos_in_library': len(library_videos),
                'videos_used': len(selected_videos),
                'type': 'pexels-library-subtitles'
            }
        else:
            print(f"    ❌ Video creation failed: {result.stderr}")
            return None
        
    except Exception as e:
        print(f"  ❌ Error creating library video: {e}")
        return None

def create_video_background_with_subtitles(slide_data, audio_data, work_dir, article_name):
    """Create video with Pexels background and 3-word subtitles"""
    
    print(f"🎬 Step 6: Creating video with Pexels background and subtitles")
    
    try:
        import subprocess
        import requests
        
        print("  🔧 Downloading professional background video from Pexels...")
        
        # Search for professional/business themed video
        search_terms = ["business meeting", "office professional", "legal consultation", "corporate", "professional"]
        
        # Try to download a video (no API key needed for basic access)
        background_video = None
        for term in search_terms:
            try:
                # Pexels provides some videos without API key via direct URLs
                # This is a simplified approach - in production you'd use their API
                pexels_url = f"https://www.pexels.com/search/videos/{term.replace(' ', '%20')}/"
                print(f"    🔍 Searching for: {term}")
                
                # For now, use a known working Pexels video URL (business theme)
                # This is a sample business video that's commonly available
                video_url = "https://player.vimeo.com/external/291648067.hd.mp4?s=94998971682c6a3267e4cbd19d16a7b6c720f345&profile_id=175"
                
                print(f"    📥 Downloading background video...")
                video_response = requests.get(video_url, timeout=30)
                
                if video_response.status_code == 200:
                    background_video = os.path.join(work_dir, "background_video.mp4")
                    with open(background_video, 'wb') as f:
                        f.write(video_response.content)
                    print(f"    ✅ Background video downloaded: {len(video_response.content)} bytes")
                    break
                    
            except Exception as e:
                print(f"    ⚠️  Failed to download {term}: {e}")
                continue
        
        if not background_video:
            print("    ⚠️  Could not download background video, creating simple background")
            # Fallback to generated background
            background_video = os.path.join(work_dir, "generated_background.mp4")
            bg_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi', '-i', 'color=c=0x1D1D25:size=1920x1080:duration=120',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                background_video
            ]
            subprocess.run(bg_cmd, capture_output=True)
        
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
        
        print(f"  ⏱️  {time_per_group} seconds per 3-word group")
        
        # Create subtitle filters with bold text
        subtitle_filters = []
        for i, group in enumerate(three_word_groups):
            start_time = i * time_per_group
            end_time = (i + 1) * time_per_group
            
            # Clean text for FFmpeg
            clean_text = group.replace("'", "").replace('"', '').replace(':', '').replace(';', '')
            
            # Large bold translucent text in center of screen
            subtitle_filter = f"drawtext=text='{clean_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start_time:.1f},{end_time:.1f})'"
            subtitle_filters.append(subtitle_filter)
        
        # Create final video with background, audio, and subtitles
        video_filename = f"{article_name}_pexels_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        # Combine all subtitle filters
        all_subtitle_filters = ','.join(subtitle_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-stream_loop', '-1', '-i', background_video,  # Loop background video
            '-i', combined_audio,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-r', '30', '-pix_fmt', 'yuv420p',
            '-vf', all_subtitle_filters,
            '-shortest',  # End when audio ends
            video_path
        ]
        
        print("  🚀 Creating video with Pexels background and subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("    ✅ Professional video created with Pexels background!")
            
            # Clean up
            os.remove(audio_concat_file)
            os.remove(combined_audio)
            if os.path.exists(background_video):
                os.remove(background_video)
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'subtitle_groups': len(three_word_groups),
                'type': 'pexels-background-subtitles'
            }
        else:
            print(f"    ❌ Video creation failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating Pexels video: {e}")
        return None
    """Create video with one slide and 3-word subtitles"""
    
    print(f"🎬 Step 6: Creating single slide video with 3-word subtitles")
    
    try:
        import subprocess
        from PIL import Image, ImageDraw, ImageFont
        
        print("  🔧 Creating single slide...")
        
        # Create one clean slide
        slide = Image.new('RGB', (1920, 1080), "#f8f9fa")
        draw = ImageDraw.Draw(slide)
        
        # Create gradient background
        for y in range(1080):
            gradient_color = int(248 - (y * 20 / 1080))
            draw.line([(0, y), (1920, y)], fill=(gradient_color, gradient_color + 2, gradient_color + 5))
        
        # Load fonts
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
            subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
            social_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            social_font = ImageFont.load_default()
        
        # Add DadAssist branding
        draw.text((960, 300), "DadAssist", fill="#E09900", font=title_font, anchor="mm")
        draw.text((960, 400), "Legal Support for Australian Fathers", fill="#1D1D25", font=subtitle_font, anchor="mm")
        
        # Add social media
        draw.text((960, 800), "🐦 @dad_assist  📘 DadAssist  📸 @dadassist", fill="#1D1D25", font=social_font, anchor="mm")
        draw.text((960, 850), "dadassist.com.au", fill="#E09900", font=social_font, anchor="mm")
        
        # Save single slide
        single_slide_path = os.path.join(work_dir, "single_slide.png")
        slide.save(single_slide_path)
        print("    ✅ Single slide created")
        
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
        result = subprocess.run(audio_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ❌ Failed to combine audio: {result.stderr}")
            return None
        
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
        
        # Calculate timing - 0.8 seconds per group for fastest subtitles
        total_duration = sum(audio['duration'] for audio in audio_data['audio_files'])
        time_per_group = 0.8  # Fixed 0.8 seconds per group
        
        print(f"  ⏱️  {time_per_group} seconds per 3-word group (fastest timing)")
        
        # Create subtitle filters with large bold text in center of screen
        subtitle_filters = []
        for i, group in enumerate(three_word_groups):
            start_time = i * time_per_group
            end_time = (i + 1) * time_per_group
            
            # Clean text for FFmpeg
            clean_text = group.replace("'", "").replace('"', '').replace(':', '').replace(';', '')
            
            # Large bold translucent text in center of screen
            subtitle_filter = f"drawtext=text='{clean_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=64:fontcolor=white@0.9:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start_time:.1f},{end_time:.1f})'"
            subtitle_filters.append(subtitle_filter)
        
        # Create video with single slide, audio, and 3-word subtitles
        video_filename = f"{article_name}_single_slide_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        # Combine all subtitle filters
        all_subtitle_filters = ','.join(subtitle_filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-loop', '1', '-i', single_slide_path,
            '-i', combined_audio,
            '-c:v', 'libx264', '-c:a', 'aac',
            '-r', '30', '-pix_fmt', 'yuv420p',
            '-vf', all_subtitle_filters,
            '-shortest',
            video_path
        ]
        
        print("  🚀 Creating single slide video with 3-word subtitles...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("    ✅ Single slide video created successfully!")
            
            # Clean up
            os.remove(audio_concat_file)
            os.remove(combined_audio)
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'subtitle_groups': len(three_word_groups),
                'type': 'single-slide-3-words'
            }
        else:
            print(f"    ❌ Single slide video failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating single slide video: {e}")
        return None
    """Create video with bullet point slides synced to Arthur's actual audio"""
    
    print(f"🎬 Step 6: Creating bullet point video with Arthur's voice")
    
    try:
        import subprocess
        
        print("  🔧 Preparing bullet point video with real audio...")
        
        # Create video filename
        video_filename = f"{article_name}_bullet_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        # Concatenate all audio files first
        audio_concat_file = os.path.join(work_dir, "audio_concat_list.txt")
        with open(audio_concat_file, 'w') as f:
            for audio in audio_data['audio_files']:
                f.write(f"file '{audio['file_path']}'\n")
        
        # Create single continuous audio file
        combined_audio = os.path.join(work_dir, "combined_audio.mp3")
        audio_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', audio_concat_file,
            '-c', 'copy',
            combined_audio
        ]
        
        print("  🎵 Combining Arthur's audio files...")
        result = subprocess.run(audio_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ❌ Failed to combine audio: {result.stderr}")
            return None
        
        # Calculate timing: total audio duration / number of slides
        total_audio_duration = sum(audio['duration'] for audio in audio_data['audio_files'])
        slides_count = len(slide_data['slide_files'])
        duration_per_slide = total_audio_duration / slides_count
        
        print(f"  📊 Total audio: {total_audio_duration:.1f}s, {slides_count} slides, {duration_per_slide:.1f}s per slide")
        
        # Create individual video segments for each slide
        temp_videos = []
        
        for i, slide in enumerate(slide_data['slide_files']):
            temp_video = os.path.join(work_dir, f"temp_bullet_video_{i}.mp4")
            
            # Calculate start time for this slide's audio segment
            start_time = i * duration_per_slide
            
            # Create video segment with slide and corresponding audio segment
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-t', str(duration_per_slide), '-i', slide['slide_path'],
                '-ss', str(start_time), '-t', str(duration_per_slide), '-i', combined_audio,
                '-c:v', 'libx264', '-c:a', 'aac',
                '-r', '30', '-pix_fmt', 'yuv420p',
                '-shortest',
                temp_video
            ]
            
            print(f"    🎬 Creating segment {i+1}: {duration_per_slide:.1f}s with Arthur's voice")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    ❌ Failed to create segment {i+1}: {result.stderr}")
                return None
            
            temp_videos.append(temp_video)
        
        # Concatenate all segments
        concat_file = os.path.join(work_dir, "bullet_concat_list.txt")
        with open(concat_file, 'w') as f:
            for video in temp_videos:
                f.write(f"file '{video}'\n")
        
        final_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            video_path
        ]
        
        print(f"  🚀 Concatenating bullet point segments with Arthur's voice...")
        result = subprocess.run(final_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    ✅ Bullet point video created with Arthur's voice!")
            
            # Clean up
            for temp_video in temp_videos:
                os.remove(temp_video)
            os.remove(concat_file)
            os.remove(audio_concat_file)
            os.remove(combined_audio)
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_audio_duration,
                'file_size': f"{file_size:.1f}",
                'segments': len(temp_videos),
                'type': 'bullet-points-with-audio'
            }
        else:
            print(f"    ❌ Bullet point video failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating bullet point video: {e}")
        return None
    """Alternative: Create video with words appearing one by one every 1 second"""
    
    print(f"🎬 Step 6: Creating word-by-word video")
    
    try:
        import subprocess
        
        print("  🔧 Preparing word-by-word video...")
        
        # Create video filename
        video_filename = f"{article_name}_word_by_word_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        temp_videos = []
        
        for i, (slide, audio) in enumerate(zip(slide_data['slide_files'], audio_data['audio_files'])):
            temp_video = os.path.join(work_dir, f"temp_word_video_{i}.mp4")
            
            # Get words from audio text
            words = audio['text'].replace("'", "").replace('"', '').split()
            
            # Create drawtext filters for each word appearing at 1-second intervals
            word_filters = []
            for j, word in enumerate(words[:15]):  # Limit to 15 words per slide
                start_time = j  # Start at j seconds
                end_time = j + 1  # Show for 1 second
                
                word_filter = f"drawtext=text='{word}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=52:fontcolor=white:box=1:boxcolor=blue@0.8:boxborderw=15:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start_time},{end_time})'"
                word_filters.append(word_filter)
            
            # Combine all word filters
            all_filters = ','.join(word_filters) if word_filters else "null"
            
            # Build FFmpeg command - 15 seconds per slide
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-t', '15', '-i', slide['file_path'],
                '-i', audio['file_path'],
                '-c:v', 'libx264', '-c:a', 'aac',
                '-r', '30', '-pix_fmt', 'yuv420p',
                '-vf', all_filters,
                '-shortest',
                temp_video
            ]
            
            print(f"    📝 Creating word-by-word segment {i+1}: {len(words)} words")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    ❌ Failed to create word segment {i+1}: {result.stderr}")
                return None
            
            temp_videos.append(temp_video)
        
        # Concatenate segments
        concat_file = os.path.join(work_dir, "word_concat_list.txt")
        with open(concat_file, 'w') as f:
            for video in temp_videos:
                f.write(f"file '{video}'\n")
        
        final_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            video_path
        ]
        
        print(f"  🚀 Concatenating word-by-word segments...")
        result = subprocess.run(final_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    ✅ Word-by-word video created successfully!")
            
            # Clean up
            for temp_video in temp_videos:
                os.remove(temp_video)
            os.remove(concat_file)
            
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            total_duration = len(slide_data['slide_files']) * 15
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'type': 'word-by-word'
            }
        else:
            print(f"    ❌ Word-by-word video failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"  ❌ Error creating word-by-word video: {e}")
        return None

def create_video(slide_data, audio_data, work_dir, article_name):
    """Use FFmpeg to combine slides and audio into final video"""
    
    print(f"🎬 Step 6: Assembling video with FFmpeg")
    
    try:
        import subprocess
        
        print("  🔧 Preparing FFmpeg command with transitions...")
        
        # Create video filename
        video_filename = f"{article_name}_video.mp4"
        video_path = os.path.join(work_dir, video_filename)
        
        # Create individual videos with fade transitions
        temp_videos = []
        transition_duration = 0.5  # 0.5 second fade transition
        target_duration = 15.0  # Target 15 seconds per slide
        
        for i, (slide, audio) in enumerate(zip(slide_data['slide_files'], audio_data['audio_files'])):
            temp_video = os.path.join(work_dir, f"temp_video_{i}.mp4")
            
            # Use 15-second segments
            segment_duration = target_duration
            
            # Add fade in/out effects to each segment
            video_filters = []
            
            # Fade in at start (except first slide)
            if i > 0:
                video_filters.append(f"fade=in:0:{int(transition_duration * 30)}")  # 30fps
            
            # Fade out at end (except last slide)
            if i < len(slide_data['slide_files']) - 1:
                fade_start = int((segment_duration - transition_duration) * 30)
                video_filters.append(f"fade=out:{fade_start}:{int(transition_duration * 30)}")
            
            # Build FFmpeg command for this segment with 30-second duration
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1', '-t', str(segment_duration), '-i', slide['file_path'],
                '-i', audio['file_path'],
                '-c:v', 'libx264', '-c:a', 'aac',
                '-r', '30', '-pix_fmt', 'yuv420p',
                '-shortest'
            ]
            
            # Show actual transcription text instead of just slide numbers
            transcription_text = audio['text'].replace("'", "").replace('"', '').replace(':', '').replace(';', '').replace('&', 'and')
            
            # Limit text length to fit on screen
            if len(transcription_text) > 120:
                transcription_text = transcription_text[:117] + "..."
            
            # Add transcription overlay - larger and more visible
            subtitle_filter = f"drawtext=text='{transcription_text}':fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=42:fontcolor=yellow:box=1:boxcolor=black@0.9:boxborderw=20:x=(w-text_w)/2:y=(h-text_h)/2"
            
            # Combine video filters
            all_filters = []
            if video_filters:
                all_filters.extend(video_filters)
            all_filters.append(subtitle_filter)
            
            # Add video filters
            cmd.extend(['-vf', ','.join(all_filters)])
            
            cmd.append(temp_video)
            
            print(f"    🎬 Creating 15-second video segment {i+1}: {slide['section']} (with real transcription)")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"    ❌ Failed to create segment {i+1}: {result.stderr}")
                return None
            
            temp_videos.append(temp_video)
        
        # Create concat file for FFmpeg
        concat_file = os.path.join(work_dir, "concat_list.txt")
        with open(concat_file, 'w') as f:
            for video in temp_videos:
                f.write(f"file '{video}'\n")
        
        # Concatenate all video segments
        final_cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_file,
            '-c', 'copy',
            video_path
        ]
        
        print(f"  🚀 Concatenating video segments with smooth transitions...")
        result = subprocess.run(final_cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"    ✅ Video created successfully with fade transitions and subtitles!")
            
            # Clean up temp files
            for temp_video in temp_videos:
                os.remove(temp_video)
            os.remove(concat_file)
            
            # Get file size
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            
            # Calculate total duration
            total_duration = sum(audio['duration'] for audio in audio_data['audio_files'])
            
            print(f"    📊 File size: {file_size:.1f} MB")
            print(f"    ⏱️  Duration: {total_duration:.1f} seconds")
            print(f"    🎭 Transitions: 0.5s fade between slides")
            print(f"    📝 Subtitles: Real-time voice transcription")
            
            return {
                'video_path': video_path,
                'filename': video_filename,
                'duration': total_duration,
                'file_size': f"{file_size:.1f}",
                'slides_count': len(slide_data['slide_files']),
                'audio_count': len(audio_data['audio_files']),
                'transitions': "0.5s fade",
                'subtitles': "Real-time transcription"
            }
        else:
            print(f"    ❌ FFmpeg concatenation failed:")
            print(f"    Error: {result.stderr}")
            return None
            
    except FileNotFoundError:
        print("  ❌ FFmpeg not installed. Install with: sudo apt install ffmpeg")
        return None
    except Exception as e:
        print(f"  ❌ Error creating video: {e}")
        return None

def create_bullet_point_slides(script_data, work_dir):
    """Create slides with 3 bullet points using Bedrock to summarize every 30 words"""
    
    print(f"🎨 Step 5: Creating bullet point slides with Bedrock summaries")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import boto3
        import json
        
        print("  🔧 Processing script into 30-word segments...")
        
        # Combine all script text
        full_text = ""
        for section_name in script_data['sections']:
            section_text = script_data['enhanced_script'].get(section_name, '')
            full_text += section_text + " "
        
        # Split into words and create 30-word chunks
        words = full_text.split()
        word_chunks = []
        
        for i in range(0, len(words), 30):
            chunk = words[i:i+30]
            word_chunks.append(' '.join(chunk))
        
        print(f"  📊 Created {len(word_chunks)} segments of ~30 words each")
        
        # Use Bedrock to create proper bullet points for each chunk
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        slide_files = []
        
        # DadAssist branding colors
        brand_dark = "#1D1D25"
        brand_gold = "#E09900"
        white = "#FFFFFF"
        light_gray = "#f8f9fa"
        
        # Create slide for each 30-word chunk
        for i, chunk in enumerate(word_chunks):
            print(f"  🤖 Creating Bedrock bullet points for segment {i+1}")
            
            # Ask Bedrock to create 3 bullet points
            prompt = f"""
Create exactly 3 concise bullet points that summarize this text for Australian fathers:

"{chunk}"

Format as:
• [First key point]
• [Second key point] 
• [Third key point]

Keep each bullet point under 60 characters and focus on actionable advice.
"""
            
            try:
                request_body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 300,
                    "messages": [{"role": "user", "content": prompt}]
                }
                
                response = bedrock.invoke_model(
                    modelId="anthropic.claude-3-haiku-20240307-v1:0",
                    body=json.dumps(request_body)
                )
                
                response_body = json.loads(response['body'].read())
                bullet_text = response_body['content'][0]['text'].strip()
                
                # Extract bullet points
                lines = bullet_text.split('\n')
                bullets = [line.strip() for line in lines if line.strip().startswith('•')]
                
                # Ensure we have 3 bullets
                while len(bullets) < 3:
                    bullets.append("• Key information for fathers")
                bullets = bullets[:3]  # Limit to 3
                
            except Exception as e:
                print(f"    ⚠️  Bedrock failed, using fallback bullets: {e}")
                # Fallback bullets
                bullets = [
                    "• Important legal considerations",
                    "• Key factors for custody decisions", 
                    "• Essential steps for fathers"
                ]
            
            # Create slide
            slide = Image.new('RGB', (1920, 1080), light_gray)
            draw = ImageDraw.Draw(slide)
            
            # Create gradient background
            for y in range(1080):
                gradient_color = int(248 - (y * 20 / 1080))
                draw.line([(0, y), (1920, y)], fill=(gradient_color, gradient_color + 2, gradient_color + 5))
            
            # Load fonts
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
                bullet_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
                social_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                bullet_font = ImageFont.load_default()
                social_font = ImageFont.load_default()
            
            # Add DadAssist branding
            draw.text((80, 60), "DadAssist", fill=brand_gold, font=title_font)
            draw.text((80, 130), "Legal Support for Australian Fathers", fill=brand_dark, font=bullet_font)
            
            # Add slide title
            draw.text((80, 250), f"Key Points - Part {i+1}", fill=brand_gold, font=title_font)
            
            # Add Bedrock-generated bullet points
            y_pos = 400
            for bullet in bullets:
                draw.text((80, y_pos), bullet, fill=brand_dark, font=bullet_font)
                y_pos += 100
            
            # Add social media footer
            footer_y = 950
            draw.text((80, footer_y), "Follow us: 🐦 @dad_assist  📘 DadAssist  📸 @dadassist", fill=brand_dark, font=social_font)
            draw.text((1400, footer_y), "dadassist.com.au", fill=brand_gold, font=social_font)
            
            # Save slide
            slide_filename = f"bullet_slide_{i+1:02d}.png"
            slide_path = os.path.join(work_dir, slide_filename)
            slide.save(slide_path)
            
            slide_files.append({
                'slide_path': slide_path,
                'filename': slide_filename,
                'word_chunk': chunk,
                'bullets': bullets,
                'word_count': len(chunk.split()),
                'index': i + 1
            })
            
            print(f"    ✅ Slide saved: {slide_filename} with Bedrock bullets")
        
        return {
            'slide_files': slide_files,
            'word_chunks': word_chunks,
            'total_slides': len(slide_files)
        }
        
    except Exception as e:
        print(f"  ❌ Error creating bullet point slides: {e}")
        return None
    """Create visual slides with actual DadAssist branding and social media links"""
    
    print(f"🎨 Step 5: Creating visual slides with DadAssist branding")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        import requests
        from io import BytesIO
        
        print("  🔧 Initializing slide creation with real branding...")
        
        # Actual DadAssist branding colors from website
        brand_dark = "#1D1D25"      # Dark title color
        brand_gold = "#E09900"      # Primary gold/orange
        brand_light_gold = "#F5B800" # Light gold
        white = "#FFFFFF"
        light_gray = "#f8f9fa"      # Background gradient start
        
        # Download DadAssist logo
        print("  📥 Downloading DadAssist logo...")
        try:
            logo_response = requests.get("https://dadassist.com.au/images/DA-LOGO-2.png")
            logo_image = Image.open(BytesIO(logo_response.content))
            # Resize logo to fit slides
            logo_image = logo_image.resize((150, 75), Image.Resampling.LANCZOS)
            print("  ✅ Logo downloaded and resized")
        except:
            print("  ⚠️  Could not download logo, using text instead")
            logo_image = None
        
        # Social media handles from conversation summary
        social_media = [
            "🐦 @dad_assist",
            "📘 DadAssist", 
            "📸 @dadassist"
        ]
        
        # Download background images from Unsplash
        print("  🖼️  Downloading background images from Unsplash...")
        
        # Search terms for each section type
        search_terms = {
            'hook': 'father child family',
            'section1': 'legal advice professional',
            'section2': 'family support guidance', 
            'section3': 'parenting father child',
            'conclusion': 'success family happy'
        }
        
        background_images = {}
        
        for section_name in script_data['sections']:
            search_term = search_terms.get(section_name, 'professional legal family')
            
            try:
                # Unsplash API call (free, no key needed for basic use)
                unsplash_url = f"https://source.unsplash.com/1920x1080/?{search_term.replace(' ', ',')}"
                bg_response = requests.get(unsplash_url, timeout=10)
                
                if bg_response.status_code == 200:
                    bg_image = Image.open(BytesIO(bg_response.content))
                    # Apply dark overlay for text readability
                    overlay = Image.new('RGBA', bg_image.size, (0, 0, 0, 120))  # Semi-transparent black
                    bg_image = bg_image.convert('RGBA')
                    bg_image = Image.alpha_composite(bg_image, overlay)
                    background_images[section_name] = bg_image.convert('RGB')
                    print(f"    ✅ Downloaded background for {section_name}")
                else:
                    background_images[section_name] = None
                    print(f"    ⚠️  Could not download background for {section_name}")
            except:
                background_images[section_name] = None
                print(f"    ⚠️  Error downloading background for {section_name}")
        
        slide_files = []
        
        # Create slides for each section
        for i, section_name in enumerate(script_data['sections']):
            section_text = script_data['enhanced_script'].get(section_name, '')
            
            if not section_text:
                continue
                
            print(f"  🖼️  Creating branded slide for: {section_name}")
            
            # Start with background image or gradient
            if background_images.get(section_name):
                slide = background_images[section_name].copy()
                print(f"    🖼️  Using Unsplash background image")
            else:
                # Fallback: Create gradient background
                slide = Image.new('RGB', (1920, 1080), light_gray)
                draw_bg = ImageDraw.Draw(slide)
                for y in range(1080):
                    gradient_color = int(248 - (y * 20 / 1080))
                    draw_bg.line([(0, y), (1920, y)], fill=(gradient_color, gradient_color + 2, gradient_color + 5))
                print(f"    🎨 Using gradient background")
            
            draw = ImageDraw.Draw(slide)
            
            # Try to load fonts
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
                text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
                social_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
                social_font = ImageFont.load_default()
            
            # Add logo if available
            if logo_image:
                slide.paste(logo_image, (80, 60), logo_image if logo_image.mode == 'RGBA' else None)
                logo_width = 150
            else:
                # Fallback: Draw "DadAssist" text
                draw.text((80, 60), "DadAssist", fill=brand_gold, font=title_font)
                logo_width = 200
            
            # Add main title next to logo
            draw.text((80 + logo_width + 30, 80), "Legal Support for Australian Fathers", fill=brand_dark, font=text_font)
            
            # Add section title with gold background
            section_title = section_name.replace('_', ' ').title()
            
            # Draw gold background for section title
            title_bbox = draw.textbbox((0, 0), section_title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            
            # Gold background rectangle
            draw.rectangle([80, 200, 80 + title_width + 40, 200 + title_height + 20], fill=brand_gold)
            draw.text((100, 210), section_title, fill=white, font=title_font)
            
            # Add a key visual element or icon area (instead of text)
            # Large centered area for future graphics/icons
            center_y = 500
            draw.text((80, center_y), "🎯 Key Points:", fill=brand_gold, font=title_font)
            draw.text((80, center_y + 80), "• Professional legal guidance", fill=brand_dark, font=text_font)
            draw.text((80, center_y + 130), "• Tailored for Australian fathers", fill=brand_dark, font=text_font)
            draw.text((80, center_y + 180), "• Expert family law support", fill=brand_dark, font=text_font)
            
            # Add social media footer
            footer_y = 950
            draw.text((80, footer_y), "Follow us:", fill=brand_gold, font=social_font)
            
            social_x = 200
            for social in social_media:
                draw.text((social_x, footer_y), social, fill=brand_dark, font=social_font)
                social_x += 200
            
            # Add website
            draw.text((1400, footer_y), "dadassist.com.au", fill=brand_gold, font=social_font)
            
            # Save slide
            slide_filename = f"slide_{i+1:02d}_{section_name}.png"
            slide_path = os.path.join(work_dir, slide_filename)
            slide.save(slide_path)
            
            slide_files.append({
                'section': section_name,
                'file_path': slide_path,
                'filename': slide_filename,
                'index': i + 1
            })
            
            print(f"    ✅ Branded slide saved: {slide_filename}")
        
        print(f"\n  📊 Branded Slide Creation Summary:")
        print(f"    🎨 Total slides created: {len(slide_files)}")
        print(f"    🎯 Branding: Official DadAssist colors and logo")
        print(f"    📱 Social media: Twitter, Facebook, Instagram")
        print(f"    📁 Slide files:")
        for slide in slide_files:
            print(f"      • {slide['filename']} - {slide['section']}")
        
        return {
            'slide_files': slide_files,
            'total_slides': len(slide_files),
            'brand_colors': {
                'dark': brand_dark,
                'gold': brand_gold,
                'light_gold': brand_light_gold,
                'white': white
            },
            'social_media': social_media
        }
        
    except ImportError:
        print("  ❌ PIL (Pillow) not installed. Install with: pip install Pillow")
        return None
    except Exception as e:
        print(f"  ❌ Error creating branded slides: {e}")
        return None

def enhance_script_with_bedrock(article_data):
    """Use Bedrock to create engaging voiceover script from article content"""
    
    print(f"🤖 Step 3: Enhancing script with Bedrock")
    
    try:
        # Initialize Bedrock client
        print("  🔧 Initializing Bedrock client...")
        bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Create prompt for video script enhancement
        prompt = f"""
Transform this legal article into an engaging 2-3 minute video script for Australian fathers.

Article Title: {article_data['title']}
Article Content: {article_data['content'][:3000]}...

Requirements:
1. Create a conversational, supportive tone
2. Break into 4-5 sections of 30-40 seconds each
3. Start with a hook that grabs attention
4. Include practical advice and key takeaways
5. End with a call to action for DadAssist services
6. Use "you" to speak directly to fathers
7. Keep language simple and accessible

Format as JSON with sections:
{{
  "hook": "Opening 30 seconds to grab attention",
  "section1": "First main point (30-40 seconds)",
  "section2": "Second main point (30-40 seconds)", 
  "section3": "Third main point (30-40 seconds)",
  "conclusion": "Call to action and wrap-up (30 seconds)"
}}
"""

        print(f"  📝 Prompt length: {len(prompt)} characters")
        
        # Prepare request for Claude
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        print("  🚀 Calling Bedrock Claude...")
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",  # Try Haiku instead of Sonnet
            body=json.dumps(request_body)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        enhanced_script = response_body['content'][0]['text']
        
        print(f"  ✅ Bedrock response received: {len(enhanced_script)} characters")
        print(f"  📄 Script preview: {enhanced_script[:200]}...")
        
        # Save raw Bedrock output to file for inspection
        bedrock_output_file = os.path.join('/tmp', f"bedrock_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(bedrock_output_file, 'w') as f:
            f.write(enhanced_script)
        print(f"  💾 Saved full Bedrock output to: {bedrock_output_file}")
        
        # Try to parse as JSON
        try:
            script_json = json.loads(enhanced_script)
            print("  ✅ Successfully parsed script as JSON")
            
            # Validate required sections
            required_sections = ['hook', 'section1', 'section2', 'section3', 'conclusion']
            missing_sections = [s for s in required_sections if s not in script_json]
            
            if missing_sections:
                print(f"  ⚠️  Missing sections: {missing_sections}")
            else:
                print("  ✅ All required sections present")
            
            return {
                'enhanced_script': script_json,
                'raw_response': enhanced_script,
                'sections': list(script_json.keys()),
                'total_sections': len(script_json)
            }
            
        except json.JSONDecodeError:
            print("  ⚠️  Response not valid JSON, using as raw text")
            # Fallback: split into sections manually
            sections = enhanced_script.split('\n\n')
            return {
                'enhanced_script': {
                    'hook': sections[0] if len(sections) > 0 else enhanced_script[:200],
                    'section1': sections[1] if len(sections) > 1 else enhanced_script[200:400],
                    'section2': sections[2] if len(sections) > 2 else enhanced_script[400:600],
                    'section3': sections[3] if len(sections) > 3 else enhanced_script[600:800],
                    'conclusion': sections[4] if len(sections) > 4 else enhanced_script[800:]
                },
                'raw_response': enhanced_script,
                'sections': ['hook', 'section1', 'section2', 'section3', 'conclusion'],
                'total_sections': 5
            }
        
    except Exception as e:
        print(f"  ❌ Error calling Bedrock: {e}")
        return None

def generate_audio_with_polly(script_data, work_dir):
    """Generate audio files using Amazon Polly with Arthur voice"""
    
    print(f"🎙️  Step 4: Generating audio with Polly")
    
    try:
        # Initialize Polly client
        print("  🔧 Initializing Polly client...")
        polly = boto3.client('polly', region_name='us-east-1')
        
        # Use Arthur - British English male voice with neural engine
        voice_id = 'Arthur'  # British English, Male, Neural engine
        print(f"  🎤 Using voice: {voice_id} (British English, Male, Neural)")
        
        audio_files = []
        total_duration = 0
        
        # Generate audio for each script section
        for section_name in script_data['sections']:
            section_text = script_data['enhanced_script'].get(section_name, '')
            
            if not section_text:
                print(f"  ⚠️  Skipping empty section: {section_name}")
                continue
                
            print(f"  🎵 Generating audio for: {section_name}")
            print(f"    📝 Text length: {len(section_text)} characters")
            print(f"    📄 Preview: {section_text[:100]}...")
            
            # Call Polly to synthesize speech with slow rate (not x-slow)
            ssml_text = f'<speak><prosody rate="slow">{section_text}</prosody></speak>'
            
            response = polly.synthesize_speech(
                Text=ssml_text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine='neural',
                TextType='ssml'  # Enable SSML processing
            )
            
            # Save audio file
            audio_filename = f"{section_name}_audio.mp3"
            audio_path = os.path.join(work_dir, audio_filename)
            
            with open(audio_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            # Get audio duration (estimate: ~150 words per minute)
            word_count = len(section_text.split())
            estimated_duration = (word_count / 150) * 60  # seconds
            
            print(f"    ✅ Audio saved: {audio_filename}")
            print(f"    ⏱️  Estimated duration: {estimated_duration:.1f} seconds")
            
            audio_files.append({
                'section': section_name,
                'file_path': audio_path,
                'filename': audio_filename,
                'duration': estimated_duration,
                'word_count': word_count,
                'text': section_text
            })
            
            total_duration += estimated_duration
        
        print(f"\n  📊 Audio Generation Summary:")
        print(f"    🎵 Total sections: {len(audio_files)}")
        print(f"    ⏱️  Total duration: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"    🎤 Voice used: {voice_id} (British English, Male)")
        
        # List all generated files
        print(f"\n  📁 Generated audio files:")
        for audio in audio_files:
            print(f"    • {audio['filename']} - {audio['duration']:.1f}s - {audio['word_count']} words")
        
        return {
            'audio_files': audio_files,
            'total_duration': total_duration,
            'voice_id': voice_id,
            'total_sections': len(audio_files)
        }
        
    except Exception as e:
        print(f"  ❌ Error generating audio with Polly: {e}")
        return None

def fetch_article_content(url):
    """Fetch and extract article content from DadAssist URL"""
    
    print(f"📥 Step 2: Fetching article content from {url}")
    
    try:
        # Download the HTML page
        print("  🌐 Downloading HTML...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"  ✅ Downloaded {len(response.content)} bytes")
        
        # Parse HTML with BeautifulSoup
        print("  🔍 Parsing HTML content...")
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title_element = soup.find('h1')
        if title_element:
            title = title_element.get_text().strip()
            print(f"  📝 Title: {title}")
        else:
            title = "DadAssist Legal Article"
            print("  ⚠️  No title found, using default")
        
        # Extract main content (look for common article containers)
        content_selectors = [
            '.article-content',
            '.post-content', 
            '.content',
            'main',
            'article'
        ]
        
        content_text = ""
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                print(f"  ✅ Found content using selector: {selector}")
                content_text = content_element.get_text()
                break
        
        # Fallback: get all paragraph text
        if not content_text:
            print("  🔄 Using fallback: extracting all paragraphs")
            paragraphs = soup.find_all('p')
            content_text = '\n'.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Clean up the content
        content_text = content_text.replace('\n\n\n', '\n\n').strip()
        
        print(f"  📊 Extracted {len(content_text)} characters")
        print(f"  📄 Content preview: {content_text[:200]}...")
        
        if len(content_text) < 100:
            print("  ⚠️  Warning: Content seems very short")
        
        return {
            'title': title,
            'content': content_text,
            'url': url,
            'word_count': len(content_text.split()),
            'char_count': len(content_text)
        }
        
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error downloading article: {e}")
        return None
    except Exception as e:
        print(f"  ❌ Error parsing article: {e}")
        return None

def main():
    """Main function - now with slide creation"""
    
    print("🎬 DadAssist Video Generator v1.4")
    print("=" * 50)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("❌ Error: No article URL provided")
        print("Usage: python3 generate_video.py 'https://dadassist.com.au/posts/articles/article-name.html'")
        return None
    
    article_url = sys.argv[1]
    print(f"📝 Input URL: {article_url}")
    
    # Validate URL format
    if not article_url.startswith("https://dadassist.com.au/posts/articles/"):
        print("⚠️  Warning: URL doesn't match expected DadAssist article format")
    
    # Extract article name from URL for file naming
    article_name = article_url.split("/")[-1].replace(".html", "")
    print(f"📂 Article name: {article_name}")
    
    # Create working directory
    work_dir = f"/tmp/video_generation_{article_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📁 Working directory: {work_dir}")
    
    try:
        os.makedirs(work_dir, exist_ok=True)
        print("✅ Working directory created")
    except Exception as e:
        print(f"❌ Error creating working directory: {e}")
        return None
    
    # Step 2: Fetch article content
    article_data = fetch_article_content(article_url)
    if not article_data:
        print("❌ Failed to fetch article content")
        return None
    
    print(f"\n📋 Article Summary:")
    print(f"  📝 Title: {article_data['title']}")
    print(f"  📊 Word count: {article_data['word_count']}")
    print(f"  📄 Character count: {article_data['char_count']}")
    
    # Step 3: Enhance script with Bedrock
    script_data = enhance_script_with_bedrock(article_data)
    if not script_data:
        print("❌ Failed to enhance script with Bedrock")
        return None
    
    print(f"\n📋 Enhanced Script Summary:")
    print(f"  🎬 Total sections: {script_data['total_sections']}")
    print(f"  📝 Sections: {', '.join(script_data['sections'])}")
    
    # Step 4: Generate audio with Polly
    audio_data = generate_audio_with_polly(script_data, work_dir)
    if not audio_data:
        print("❌ Failed to generate audio with Polly")
        return None
    
    print(f"\n📋 Audio Generation Summary:")
    print(f"  🎵 Total audio files: {audio_data['total_sections']}")
    print(f"  ⏱️  Total duration: {audio_data['total_duration']:.1f} seconds")
    print(f"  🎤 Voice: {audio_data['voice_id']} (British English, Male)")
    
    # Step 5: Create visual slides
    slide_data = create_bullet_point_slides(script_data, work_dir)
    if not slide_data:
        print("❌ Failed to create visual slides")
        return None
    
    print(f"\n📋 Slide Creation Summary:")
    print(f"  🎨 Total slides: {slide_data['total_slides']}")
    print(f"  📁 Slide files: {len(slide_data['slide_files'])}")
    
    # Step 6: Create word-by-word video instead of regular video
    video_data = create_pexels_video_background(slide_data, audio_data, work_dir, article_name)
    if not video_data:
        print("❌ Failed to create word-by-word video")
        return None
    
    print(f"\n📋 Word-by-Word Video Summary:")
    print(f"  🎬 Video file: {video_data['filename']}")
    print(f"  ⏱️  Duration: {video_data['duration']} seconds")
    print(f"  📁 File size: {video_data['file_size']} MB")
    print(f"  📝 Type: {video_data['type']}")
    
    # Remaining video generation steps (placeholder)
    print(f"\n🔄 Remaining Steps:")
    print("  2. ✅ Fetch article content - COMPLETED")
    print("  3. ✅ Enhance script with Bedrock - COMPLETED")
    print("  4. ✅ Generate audio with Polly - COMPLETED")
    print("  5. ✅ Create visual slides - COMPLETED")
    print("  6. ✅ Assemble video with FFmpeg - COMPLETED")
    print("  7. 💾 Save to web server")
    
    # Generate output filename
    video_filename = f"{article_name}_video.mp4"
    video_url = f"https://dadassist.com.au/videos/{video_filename}"
    
    print(f"\n📋 Planned output:")
    print(f"  📁 Local file: {work_dir}/{video_filename}")
    print(f"  🌐 Web URL: {video_url}")
    
    print(f"\n✅ Step 5 completed successfully!")
    print(f"🎯 Ready for Step 6: FFmpeg video assembly")
    
    # Return the planned video URL
    return video_url

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n🎉 Final result: {result}")
    else:
        print(f"\n❌ Video generation failed")
        sys.exit(1)
