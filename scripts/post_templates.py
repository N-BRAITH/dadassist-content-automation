#!/usr/bin/env python3
"""
DadAssist Social Media - Post Templates
Generates platform-specific content from DadAssist knowledge base articles
Updated: Phase 1 - SubmitForm.html integration and mandatory hashtags
"""

import re
from urllib.parse import quote

def clean_title(title):
    """Clean article title for social media"""
    return re.sub(r'\s+', ' ', title.strip())

def get_mandatory_hashtags():
    """Return comprehensive hashtags for all DadAssist posts"""
    return {
        'aspirational': ['#UnbrokenDad', '#Fatherhood', '#PresentFather', '#ForTheKids', '#CycleBreakers', '#DivorceRecovery'],
        'legal': ['#ChildCustody', '#FamilyCourt', '#ParentalRights', '#CoParenting', '#FathersRights', '#FamilyLawyer'],
        'divorce': ['#Divorce', '#Divorced', '#DivorcedLife', '#DivorceSupport', '#DivorceHelp', '#DivorceSurvivor'],
        'custody': ['#JointCustody', '#SoleCustody', '#VisitationRights', '#ParentingPlan', '#ParentingTime', '#LegalCustody'],
        'support': ['#ChildSupport', '#Alimony', '#Mediation', '#DivorceCoach', '#DivorceCommunity', '#DivorceAttorney']
    }

def get_dadassist_urls():
    """Return standard DadAssist URLs for all posts"""
    return {
        'website': 'https://dadassist.com.au',
        'form': 'https://dadassist.com.au/SubmitForm.html',
        'base': 'dadassist.com.au'
    }

def generate_twitter_post(article):
    """Generate Twitter/X post (280 characters max) for DadAssist articles"""
    title = clean_title(article['title'])
    urls = get_dadassist_urls()
    hashtags = get_mandatory_hashtags()
    
    # Twitter-optimized hashtags (3 max for best engagement)
    twitter_tags = f"{hashtags['aspirational'][0]} {hashtags['legal'][4]} {hashtags['divorce'][0]}"  # #UnbrokenDad #FathersRights #Divorce
    
    # Create post with SubmitForm.html reference
    post = f"""⚖️ {title}

Get personalized legal guidance for your situation.

🔗 Get help: {urls['form']}
📖 Read guide: {article.get('url', f"{urls['website']}/posts/articles/")}

{twitter_tags}"""
    
    # Ensure under 280 characters
    if len(post) > 280:
        # Truncate title if needed
        max_title_length = 180 - len(twitter_tags) - 80  # Leave room for URLs and text
        if len(title) > max_title_length:
            title = title[:max_title_length-3] + "..."
        
        post = f"""⚖️ {title}

Get personalized legal guidance.

🔗 Get help: {urls['form']}

{twitter_tags}"""
    
    return {
        'platform': 'twitter',
        'content': post,
        'character_count': len(post),
        'hashtags': [hashtags['aspirational'][0], hashtags['legal'][4], hashtags['divorce'][0]],
        'links': [urls['form'], article.get('url', f"{urls['website']}/posts/articles/")]
    }

def generate_facebook_post(article):
    """Generate Facebook post for DadAssist articles"""
    title = clean_title(article['title'])
    description = article.get('description', 'Expert legal guidance for Australian fathers.')
    urls = get_dadassist_urls()
    hashtags = get_mandatory_hashtags()
    
    # Facebook hashtags (5-6 for better reach)
    fb_tags = f"{hashtags['aspirational'][0]} {hashtags['legal'][4]} {hashtags['divorce'][0]} {hashtags['custody'][0]} {hashtags['legal'][1]}"  # #UnbrokenDad #FathersRights #Divorce #JointCustody #FamilyCourt
    
    post = f"""📚 New Legal Resource: {title}

{description}

Going through separation or divorce? You don't have to navigate family law alone. Our expert guides provide father-focused legal advice to help you understand your rights and protect your relationship with your children.

🔗 Get personalized legal guidance: {urls['form']}

📖 Read the complete guide: {article.get('url', f"{urls['website']}/posts/articles/")}

At DadAssist, we empower Australian fathers with expert legal support and practical resources.

{fb_tags}"""
    
    return {
        'platform': 'facebook',
        'content': post,
        'character_count': len(post),
        'hashtags': [hashtags['aspirational'][0], hashtags['legal'][4], hashtags['divorce'][0], hashtags['custody'][0], hashtags['legal'][1]],
        'links': [urls['form'], article.get('url', f"{urls['website']}/posts/articles/")]
    }

def generate_instagram_post(article):
    """Generate Instagram post for DadAssist articles"""
    title = clean_title(article['title'])
    description = article.get('description', 'Expert legal guidance for Australian fathers.')[:80] + "..."
    urls = get_dadassist_urls()
    hashtags = get_mandatory_hashtags()
    
    # Instagram hashtags (15+ optimal for engagement)
    all_hashtags = (hashtags['aspirational'][:3] + hashtags['legal'][:4] + 
                   hashtags['divorce'][:3] + hashtags['custody'][:3] + hashtags['support'][:2])
    ig_tags = ' '.join(all_hashtags)
    
    caption = f"""📖 New Guide for Fathers: {title}

{description}

Navigating family law challenges? Get expert guidance tailored to your situation.

🔗 Link in bio: {urls['base']}
📋 Get personalized help: SubmitForm.html

{ig_tags}"""
    
    return {
        'platform': 'instagram',
        'content': caption,
        'character_count': len(caption),
        'image_suggestion': f"Professional image with title: '{title}' and DadAssist branding",
        'hashtags': all_hashtags,
        'links': [urls['website'], urls['form']]
    }

def generate_tiktok_post(article):
    """Generate TikTok post for DadAssist articles"""
    title = clean_title(article['title'])
    urls = get_dadassist_urls()
    hashtags = get_mandatory_hashtags()
    
    # TikTok hashtags (casual + brand)
    tiktok_tags = f"{hashtags['core'][2]} {hashtags['brand'][0]} #DadTok #LegalAdvice"  # #Parenting #FathersRights #DadTok #LegalAdvice
    
    caption = f"""📚 {title}

Going through separation? You're not alone 💪

Get expert legal guidance at {urls['base']}

Check bio for SubmitForm link 👆

{tiktok_tags}"""
    
    return {
        'platform': 'tiktok',
        'content': caption,
        'character_count': len(caption),
        'video_suggestion': f"Text overlay video with key points from: '{title}' + DadAssist branding",
        'hashtags': ['#Parenting', '#FathersRights', '#DadTok', '#LegalAdvice'],
        'links': [urls['website'], urls['form']]
    }

def generate_all_posts(article):
    """Generate posts for all platforms with DadAssist branding and SubmitForm references"""
    return {
        'article': {
            'title': article['title'],
            'filename': article.get('filename', 'unknown'),
            'url': article.get('url', f"https://dadassist.com.au/posts/articles/{article.get('filename', '')}")
        },
        'dadassist_urls': get_dadassist_urls(),
        'mandatory_hashtags': get_mandatory_hashtags(),
        'posts': {
            'twitter': generate_twitter_post(article),
            'facebook': generate_facebook_post(article),
            'instagram': generate_instagram_post(article),
            'tiktok': generate_tiktok_post(article)
        }
    }

def preview_all_posts(article):
    """Generate and display preview of all posts for review"""
    all_posts = generate_all_posts(article)
    
    print("=" * 80)
    print(f"📋 DadAssist Social Media Posts Preview")
    print(f"Article: {article['title']}")
    print("=" * 80)
    
    for platform, post_data in all_posts['posts'].items():
        print(f"\n🔸 {platform.upper()} ({post_data['character_count']} chars)")
        print("-" * 40)
        print(post_data['content'])
        print(f"Hashtags: {', '.join(post_data['hashtags'])}")
        print(f"Links: {', '.join(post_data['links'])}")
    
    print("\n" + "=" * 80)
    return all_posts

# Test function for development
if __name__ == "__main__":
    # Test with sample DadAssist article
    sample_article = {
        'title': 'Best Interests of Children in Family Law',
        'description': 'Understanding how Australian family courts determine the best interests of children in custody and parenting arrangements.',
        'filename': 'best-interests-of-children.html',
        'url': 'https://dadassist.com.au/posts/articles/best-interests-of-children.html'
    }
    
    preview_all_posts(sample_article)
