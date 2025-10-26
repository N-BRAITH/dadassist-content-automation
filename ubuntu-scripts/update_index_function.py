import re

def update_posts_index(article_title, filename, category, description):
    index_path = '/var/www/dadassist/posts/index.html'
    
    # Category mapping to match existing sections
    category_mapping = {
        'Child Support': 'childsupport',
        'Parenting & Custody': 'parenting', 
        'Legal Procedures': 'procedure',
        'Property Settlement': 'property',
        'Family Violence': 'familyviolence',
        'Conflict Resolution': 'conflict'
    }
    
    # Get category data attribute
    category_attr = category_mapping.get(category, 'procedure')  # default to procedure
    
    # Read current index
    with open(index_path, 'r') as f:
        content = f.read()
    
    # Create new article entry in proper format
    new_entry = f'''                        <li class="resource-item">
                            <a href="articles/{filename}">{article_title}</a>
                            <div class="resource-description">{description}</div>
                        </li>'''
    
    # Find the correct category section and add before closing </ul>
    pattern = f'<div class="category-section" data-category="{category_attr}".*?</ul>'
    
    def replace_category(match):
        section = match.group(0)
        # Add new entry before closing </ul>
        return section.replace('</ul>', new_entry + '\n                    </ul>')
    
    # Update the content
    content = re.sub(pattern, replace_category, content, flags=re.DOTALL)
    
    # Write back
    with open(index_path, 'w') as f:
        f.write(content)
    
    print(f'✅ Added "{article_title}" to {category} section in index')

# Test the function
if __name__ == '__main__':
    # Test with our existing articles
    update_posts_index(
        'Understanding Child Support Obligations in Australia',
        'understanding-child-support-obligations-in-australia.html',
        'Child Support',
        'Comprehensive guide to child support obligations, assessments, and your rights as a father'
    )
    
    update_posts_index(
        'Independent Children\'s Lawyers in Australia', 
        'independent-childrens-lawyers-australia.html',
        'Parenting & Custody',
        'Everything fathers need to know about independent children\'s lawyers and their role'
    )
    
    update_posts_index(
        'Legal Financial Assistance for Disbursements',
        'legal-financial-assistance-disbursements-australia.html', 
        'Legal Procedures',
        'Guide to getting financial assistance for legal costs and disbursements'
    )
