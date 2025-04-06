from datetime import datetime
from pathlib import Path
import chevron

def generate_html(articles, digest):
    template_path = Path(__file__).parent / 'templates' / 'digest.html.mustache'
    
    context = {
        'date': datetime.now().strftime('%d.%m.%Y'),
        'digest': digest,
        'articles': [
            {
                'title': article.title,
                'source_name': article.source_name,
                'source_url': article.source_url,
                'text': article.summary
            }
            for article in articles
        ]
    }
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    html = chevron.render(template, context)
    return html