#!/usr/bin/env python3
import sys
import re
import argparse
import os
from datetime import datetime
import boto3
import json

class ArticleGenerator:
    def __init__(self):
        """Initialize the article generator with AWS Bedrock client"""
        try:
            self.bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-2')
            self.model_id = 'anthropic.claude-3-haiku-20240307-v1:0'
        except Exception as e:
            print(f"Warning: Could not initialize Bedrock client: {e}")
            self.bedrock = None

    def generate_article_content(self, scraped_content, title, category):
        prompt = f'''Create a comprehensive DadAssist article for Australian fathers.

Use this source content: {scraped_content}

CRITICAL: Generate ONLY the HTML content that goes inside the article div. Use proper HTML tags:
- <p> for paragraphs
- <h2> for main section headings
- <h3> for subsection headings  
- <ul> and <li> for bullet points
- <div class="highlight-box"><strong>Important:</strong> text</div> for key notes

Focus on fathers' rights, practical advice, and Australian family law. Make it supportive and informative for fathers going through separation/divorce.

Title: {title}
Category: {category}

Generate comprehensive, father-focused content with proper HTML formatting.'''

        if self.bedrock:
            try:
                response = self.bedrock.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': 4000,
                        'messages': [
                            {
                                'role': 'user',
                                'content': prompt
                            }
                        ]
                    })
                )
                
                response_body = json.loads(response['body'].read())
                return response_body['content'][0]['text']
                
            except Exception as e:
                print(f"Error calling Bedrock: {e}")
                return self.format_scraped_content(scraped_content)
        else:
            return self.format_scraped_content(scraped_content)

    def format_scraped_content(self, content):
        """Fallback content formatting if Bedrock fails"""
        paragraphs = content.split('\n\n')
        formatted = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if len(para) < 100 and para.count(' ') < 10:
                formatted.append(f'<h3>{para}</h3>')
            else:
                formatted.append(f'<p>{para}</p>')
        
        return '\n'.join(formatted)

    def create_article_html(self, title, content, category):
        """Create HTML with exact reference formatting"""
        current_date = datetime.now().strftime("%B %Y")
        
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | DadAssist Information Hub</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Open Sans', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; }}
        
        .post-header {{
            background: linear-gradient(135deg, #1D1D25 0%, #2a2a35 100%);
            color: white;
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .post-header .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        
        .post-logo {{
            font-size: 24px;
            font-weight: bold;
            color: #E09900;
        }}
        
        .post-main {{
            max-width: 800px;
            margin: 40px auto;
            padding: 0 20px;
        }}
        
        .post-container {{
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .post-header-content {{
            border-bottom: 3px solid #E09900;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .post-title {{
            color: #1D1D25;
            font-size: 2.5rem;
            margin-bottom: 10px;
            line-height: 1.2;
        }}
        
        .post-meta {{ color: #666; font-size: 14px; }}
        .post-content h2 {{ color: #E09900; margin: 30px 0 15px 0; font-size: 1.5rem; }}
        .post-content h3 {{ color: #1D1D25; margin: 25px 0 10px 0; font-size: 1.2rem; }}
        .post-content p {{ margin-bottom: 15px; }}
        .post-content ul {{ margin: 15px 0 15px 30px; }}
        .post-content li {{ margin-bottom: 8px; }}
        .highlight-box {{ background: #f8f9fa; border-left: 4px solid #E09900; padding: 20px; margin: 20px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <header class="post-header">
        <div class="container">
            <span class="post-logo">Information Hub</span>
            <nav class="post-nav" style="display: flex; gap: 25px; align-items: center;">
                <a href="../../../index.html" style="color: #E09900; text-decoration: none; font-weight: bold; font-size: 16px; transition: color 0.2s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.color='#FFB84D'" onmouseout="this.style.color='#E09900'">🏠 Home</a>
                <a href="../index.html" style="color: #E09900; text-decoration: none; font-weight: bold; transition: color 0.2s;" onmouseover="this.style.color='#FFB84D'" onmouseout="this.style.color='#E09900'">📚 All Articles</a>
                <a href="../../../SubmitForm.html" style="background: #E09900; color: white; padding: 8px 16px; border-radius: 20px; text-decoration: none; font-weight: bold; font-size: 14px; transition: background 0.2s; display: flex; align-items: center; gap: 5px;" onmouseover="this.style.background='#FFB84D'" onmouseout="this.style.background='#E09900'">📝 Get Help</a>
            </nav>
        </div>
    </header>
    
    <main class="post-main">
        <article class="post-container">
            <header class="post-header-content">
                <h1 class="post-title">{title}</h1>
                <div class="post-meta">
                    Category: {category} | Reading time: 5 minutes | Last updated: {current_date}
                </div>
            </header>
            
            <div class="post-content">
                {content}
                
                <h2>Expert Family Lawyers Across Australia</h2>
                
                <h3>🏛️ DadAssist Melbourne Family Lawyers</h3>
                <p>Serving: Melbourne, Victoria</p>
                <ul>
                    <li><strong>Federal Circuit Court Melbourne:</strong> 305 William Street, Melbourne VIC 3000</li>
                    <li><strong>Family Court of Australia Melbourne:</strong> 305 William Street, Melbourne VIC 3000</li>
                </ul>
                
                <h3>⚖️ DadAssist Sydney Mens Divorce Lawyers</h3>
                <p>Serving: Sydney, New South Wales</p>
                <ul>
                    <li><strong>Federal Circuit Court Sydney:</strong> Law Courts Building, Queens Square, Sydney NSW 2000</li>
                    <li><strong>Family Court of Australia Sydney:</strong> Law Courts Building, Queens Square, Sydney NSW 2000</li>
                </ul>
                
                <h3>🏛️ DadAssist Brisbane Family Law Specialists</h3>
                <p>Serving: Brisbane, Queensland</p>
                <ul>
                    <li><strong>Federal Circuit Court Brisbane:</strong> 119 North Quay, Brisbane QLD 4000</li>
                    <li><strong>Family Court of Australia Brisbane:</strong> 119 North Quay, Brisbane QLD 4000</li>
                </ul>
                
                <h3>⚖️ DadAssist Perth Fathers Rights Lawyers</h3>
                <p>Serving: Perth, Western Australia</p>
                <ul>
                    <li><strong>Federal Circuit Court Perth:</strong> 1 Victoria Avenue, Perth WA 6000</li>
                    <li><strong>Family Court of Western Australia:</strong> 150 Terrace Road, Perth WA 6000</li>
                </ul>
                
                <h3>🏛️ DadAssist Adelaide Family Court Lawyers</h3>
                <p>Serving: Adelaide, South Australia</p>
                <ul>
                    <li><strong>Federal Circuit Court Adelaide:</strong> 3 Angas Street, Adelaide SA 5000</li>
                    <li><strong>Family Court of Australia Adelaide:</strong> 3 Angas Street, Adelaide SA 5000</li>
                </ul>
            </div>

            <div class="social-share" style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 30px; border-radius: 12px; margin: 40px 0; text-align: center; border: 1px solid #dee2e6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h4 style="color: #1D1D25; margin-bottom: 15px; font-size: 1.3rem;">📱 Stay Connected with DadAssist</h4>
                <p style="color: #666; margin-bottom: 25px; font-size: 1rem;">Follow us for the latest legal resources, tips, and support for Australian fathers</p>
                <div class="social-links" style="display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
                    <a href="https://www.facebook.com/dadassist" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 30px; text-decoration: none; font-weight: bold; background: #1877f2; color: white; transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        <span style="font-size: 1.2rem;">👥</span> Facebook
                    </a>
                    <a href="https://x.com/dad_assist" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 30px; text-decoration: none; font-weight: bold; background: #000000; color: white; transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        <span style="font-size: 1.2rem;">𝕏</span> Twitter
                    </a>
                    <a href="https://www.instagram.com/dadassist" target="_blank" style="display: inline-flex; align-items: center; gap: 8px; padding: 12px 24px; border-radius: 30px; text-decoration: none; font-weight: bold; background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%); color: white; transition: transform 0.2s; box-shadow: 0 2px 4px rgba(0,0,0,0.1);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                        <span style="font-size: 1.2rem;">📸</span> Instagram
                    </a>
                </div>
            </div>
            
            <div class="post-cta" style="background: linear-gradient(135deg, #E09900, #FF7F00); color: white; padding: 40px; text-align: center; border-radius: 12px; margin-top: 40px; box-shadow: 0 6px 12px rgba(224, 153, 0, 0.3);">
                <h3 style="margin-bottom: 15px; font-size: 1.5rem;">Need Expert Legal Guidance?</h3>
                <p style="margin-bottom: 25px; font-size: 1.1rem; opacity: 0.95;">Navigate family law proceedings with confidence. Connect with experienced solicitors who understand your situation.</p>
                <a href="../../../SubmitForm.html" style="background: white; color: #E09900; padding: 15px 35px; border: none; border-radius: 30px; text-decoration: none; font-weight: bold; display: inline-block; font-size: 1.1rem; transition: transform 0.2s; box-shadow: 0 4px 8px rgba(0,0,0,0.2);" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">Get Professional Help</a>
            </div>
        </article>
    </main>

    <footer style="background: linear-gradient(135deg, #1D1D25 0%, #2a2a35 100%); color: white; text-align: center; padding: 50px 20px; margin-top: 60px; border-top: 4px solid #E09900;">
        <div style="max-width: 800px; margin: 0 auto;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 15px; margin-bottom: 25px; flex-wrap: wrap;">
                <img src="https://dadassist.com.au/images/DA-LOGO-2.png" alt="DadAssist Logo" style="height: 60px; width: auto;">
                <div>
                    <h3 style="color: #E09900; margin: 0; font-size: 1.8rem;">DadAssist</h3>
                    <p style="margin: 5px 0 0 0; color: #ccc; font-size: 1rem;">Supporting Australian Fathers</p>
                </div>
            </div>
            
            <div style="background: rgba(224, 153, 0, 0.1); padding: 20px; border-radius: 8px; margin-bottom: 25px;">
                <p style="margin: 0; font-size: 1rem; line-height: 1.6;">
                    <strong style="color: #E09900;">Information Hub:</strong> Comprehensive legal resources and guidance for fathers navigating Australian family law. 
                    <br>Get the support you need during challenging times.
                </p>
            </div>
            
            <div style="display: flex; justify-content: center; gap: 30px; margin-bottom: 25px; flex-wrap: wrap;">
                <a href="../../../index.html" style="color: #E09900; text-decoration: none; font-weight: bold; transition: color 0.2s;" onmouseover="this.style.color='#FFB84D'" onmouseout="this.style.color='#E09900'">🏠 Home</a>
                <a href="../index.html" style="color: #E09900; text-decoration: none; font-weight: bold; transition: color 0.2s;" onmouseover="this.style.color='#FFB84D'" onmouseout="this.style.color='#E09900'">📚 All Articles</a>
                <a href="../../../SubmitForm.html" style="color: #E09900; text-decoration: none; font-weight: bold; transition: color 0.2s;" onmouseover="this.style.color='#FFB84D'" onmouseout="this.style.color='#E09900'">📝 Get Help</a>
            </div>
            
            <div style="border-top: 1px solid #444; padding-top: 20px;">
                <p style="margin: 0; color: #999; font-size: 0.9rem;">
                    &copy; 2024 DadAssist. Supporting fathers through family law challenges.
                    <br>
                    <span style="color: #E09900;">Information Hub</span> - Your trusted resource for Australian family law guidance.
                </p>
            </div>
        </div>
    </footer>
</body>
</html>'''
        return html_template

    def update_index(self, title, filename, category, description):
        """Update the articles index with new article"""
        try:
            import html
            
            # Validate inputs
            if not title or not filename:
                print(f'❌ Invalid title or filename: title={title}, filename={filename}')
                return False
            
            # Escape HTML characters in title and description
            title_escaped = html.escape(title)
            description_escaped = html.escape(description)
            
            category_mapping = {
                'Child Support': 'childsupport',
                'Parenting & Custody': 'parenting', 
                'Legal Procedures': 'procedure',
                'Property Settlement': 'property',
                'Family Violence': 'familyviolence',
                'Conflict Resolution': 'conflict'
            }
            
            category_attr = category_mapping.get(category, 'procedure')
            index_path = '/var/www/dadassist/posts/index.html'
            
            # Read current index
            with open(index_path, 'r') as f:
                index_content = f.read()
            
            # Check if article already exists in index
            if f'href="articles/{filename}"' in index_content:
                print(f'⚠️ Article already in index: {filename}')
                return True
            
            # Create new article entry with escaped content
            new_entry = f'<li class="resource-item"><a href="articles/{filename}">{title_escaped}</a><div class="resource-description">{description_escaped}</div></li>\n                        '
            
            print(f'📝 Adding to index: {title_escaped[:50]}...')
            print(f'📄 Filename: {filename}')
            
            # Find the category section and add entry
            pattern = f'data-category="{category_attr}"'
            if pattern in index_content:
                start_pos = index_content.find(pattern)
                ul_end = index_content.find('</ul>', start_pos)
                if ul_end > 0:
                    index_content = index_content[:ul_end] + new_entry + index_content[ul_end:]
                    
                    # Write to temp file
                    with open('/tmp/index_temp.html', 'w') as f:
                        f.write(index_content)
                    
                    # Copy with sudo
                    os.system('sudo cp /tmp/index_temp.html /var/www/dadassist/posts/index.html')
                    os.system('sudo chown www-data:www-data /var/www/dadassist/posts/index.html')
                    os.system('sudo chmod 644 /var/www/dadassist/posts/index.html')
                    
                    print(f'✅ Updated index with article in {category} section')
                    return True
            
            print(f'❌ Could not find {category} section')
            return False
            
        except Exception as e:
            print(f'❌ Error updating index: {e}')
            return False

    def generate_complete_article(self, scraped_content, title, category, filename=None):
        """Generate complete article with Bedrock processing"""
        print(f'🤖 Generating article: {title}')
        print(f'📂 Category: {category}')
        if filename:
            print(f'📄 Using provided filename: {filename}')
        
        # Process content with Bedrock/Claude
        article_content = self.generate_article_content(scraped_content, title, category)
        if not article_content:
            return None, None
        
        # Use provided filename or generate from title
        if filename:
            if not filename.endswith('.html'):
                filename += '.html'
        else:
            # Generate filename from title (STANDARDIZED - matches workflow)
            filename = re.sub(r'[^a-zA-Z0-9\s]', '', title.lower())  # Remove non-alphanumeric except spaces
            filename = re.sub(r'\s+', '-', filename)  # Replace spaces with hyphens
            filename = filename.strip('-')  # Remove leading/trailing hyphens
            if not filename.endswith('.html'):
                filename += '.html'
        
        # Create HTML with exact reference formatting
        html_content = self.create_article_html(title, article_content, category)
        
        # Deploy article
        output_path = f"/var/www/dadassist/posts/articles/{filename}"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            article_url = f"https://dadassist.com.au/posts/articles/{filename}"
            print(f'✅ Article deployed to: {output_path}')
        except Exception as e:
            print(f'❌ Error deploying article: {e}')
            return None, None
        
        # Update index with contextual description
        # Generate description based on category
        category_descriptions = {
            'Child Support': 'child support obligations and calculations',
            'Parenting & Custody': 'parenting arrangements and custody matters',
            'Legal Procedures': 'family court procedures and legal processes',
            'Property Settlement': 'property division and financial settlements',
            'Family Violence': 'family violence orders and protection',
            'Conflict Resolution': 'mediation and dispute resolution',
            'Mental Health': 'mental health and wellbeing support'
        }
        
        context = category_descriptions.get(category, 'family law matters')
        description = f'Comprehensive guide to {context} for Australian fathers'
        
        index_updated = self.update_index(title, filename, category, description)
        
        if index_updated:
            print(f'🎉 Article generation complete!')
            print(f'🌐 Live URL: {article_url}')
            return article_url, filename
        else:
            print(f'⚠️ Article deployed but index update failed')
            return article_url, filename

def main():
    parser = argparse.ArgumentParser(description='Generate DadAssist article from scraped content')
    parser.add_argument('--content', required=True, help='Scraped legal content')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--category', required=True, help='Article category')
    parser.add_argument('--filename', required=False, help='Filename to use (optional)')
    
    args = parser.parse_args()
    
    generator = ArticleGenerator()
    
    # Pass filename to generator if provided
    if args.filename:
        result = generator.generate_complete_article(args.content, args.title, args.category, args.filename)
    else:
        result = generator.generate_complete_article(args.content, args.title, args.category)
    
    if result and result[0]:
        print(f"SUCCESS: {result[0]}")
    else:
        print("ERROR: Article generation failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
