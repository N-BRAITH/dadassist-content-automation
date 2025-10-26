import boto3
import json
from datetime import datetime

# Scraped content
scraped_content = '''Child support in Australia is governed by the Child Support (Assessment) Act 1989 and administered by Services Australia. Both parents have a legal obligation to financially support their children, regardless of their relationship status or living arrangements. The Child Support Agency uses a formula to calculate payments based on several factors including the income of both parents, the number of children, the ages of the children, and the care arrangements in place.

Parents can choose to make private arrangements for child support or have it assessed and collected by the government through the Child Support Agency. Private arrangements offer more flexibility but must meet certain legal requirements. If parents cannot agree, the Child Support Agency will make an assessment based on the legislated formula.

The assessment takes into account each parent's adjusted taxable income, which includes salary, wages, business income, investment income, and certain government payments. The formula also considers the costs of raising children and aims to ensure children receive adequate financial support from both parents according to their capacity to pay.

Changes in circumstances such as income variations, changes in care arrangements, or the birth of additional children can affect child support assessments. Parents can apply to have their assessment reviewed if their circumstances change significantly.'''

print('📄 SCRAPED CONTENT:')
print('=' * 60)
print(scraped_content)
print('=' * 60)
print()

# Generate article
bedrock = boto3.client('bedrock-runtime', region_name='ap-southeast-2')
prompt = f'Create a professional DadAssist article for Australian fathers about child support obligations. Use this content: {scraped_content}. Make it well-structured with headings, professional tone, and include practical advice.'

response = bedrock.invoke_model(
    modelId='anthropic.claude-3-haiku-20240307-v1:0',
    body=json.dumps({
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 3000,
        'messages': [{'role': 'user', 'content': prompt}]
    })
)

result = json.loads(response['body'].read())
article_content = result['content'][0]['text']

# Create HTML
title = 'Understanding Child Support Obligations in Australia'
filename = 'understanding-child-support-obligations-in-australia.html'
current_date = datetime.now().strftime('%B %d, %Y')

html_start = '''<!DOCTYPE html>
<html lang=en>
<head>
    <meta charset=UTF-8>
    <meta name=viewport content=width=device-width, initial-scale=1.0>
    <title>Understanding Child Support Obligations in Australia - DadAssist</title>
    <meta name=description content=Comprehensive guide to child support obligations for Australian fathers. Learn about assessments, payments, and your legal rights.>
    <link rel=stylesheet href=../../css/article-styles.css>
</head>
<body>
    <div class=article-container>
        <header class=article-header>
            <h1>Understanding Child Support Obligations in Australia</h1>
            <div class=article-meta>
                <span class=date>''' + current_date + '''</span>
                <span class=category>Child Support</span>
            </div>
        </header>
        
        <main class=article-content>'''

html_end = '''        </main>
        
        <div class=cta-section>
            <h3>Need Personalized Legal Guidance?</h3>
            <p>Every family situation is unique. Get expert advice tailored to your specific circumstances.</p>
            <a href=../../SubmitForm.html class=cta-button>Get Free Consultation</a>
        </div>
        
        <footer class=article-footer>
            <div class=disclaimer>
                <p><strong>Disclaimer:</strong> This information is for educational purposes only and does not constitute legal advice. Consult with a qualified family law solicitor for advice specific to your situation.</p>
            </div>
        </footer>
    </div>
</body>
</html>'''

html_article = html_start + article_content + html_end

# Save to temp file
with open('/tmp/' + filename, 'w', encoding='utf-8') as f:
    f.write(html_article)

print('✅ Article generated successfully!')
print(f'📊 Length: {len(html_article)} characters')
print(f'📁 Temp file: /tmp/{filename}')
