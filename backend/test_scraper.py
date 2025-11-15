"""Test scraper functionality."""
from app.services.scraper import scraper

# Test with Wikipedia article
url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
result = scraper.scrape_url(url)

print(f'Title: {result["title"]}')
print(f'Word count: {result["word_count"]}')
print(f'Sections: {len(result["sections"])}')
print(f'Is Wikipedia: {result["is_wikipedia"]}')
print(f'\nFirst 200 chars: {result["full_text"][:200]}...')
