"""
Blockspace Newsletter Scraper
Finds all articles by Charlie Spears and saves them to articles.json
"""

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_blockspace_articles():
    """Scrape the Blockspace newsletter for articles by Charlie Spears"""
    
    url = "https://newsletter.blockspacemedia.com/"
    articles = []
    
    print(f"🔍 Scraping {url}...")
    
    # Headers to look like a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all article links - Beehiiv uses various structures
        # Look for links that go to /p/ (post URLs)
        all_links = soup.find_all('a', href=re.compile(r'/p/'))
        
        print(f"📰 Found {len(all_links)} article links")
        
        seen_urls = set()
        
        for link in all_links:
            href = link.get('href', '')
            
            # Skip duplicates
            if href in seen_urls:
                continue
            
            # Get the parent container to check for author and title
            # Look up the DOM tree for the article container
            container = link
            for _ in range(10):  # Go up max 10 levels
                parent = container.parent
                if parent is None:
                    break
                container = parent
                
                # Check if this container has Charlie Spears mentioned
                container_text = container.get_text()
                if 'Charlie Spears' in container_text:
                    # Found a container with Charlie's name
                    # Now extract title and date
                    
                    # Try to find the title (usually in a heading or the link text)
                    title = None
                    
                    # Look for headings in the link
                    heading = link.find(['h1', 'h2', 'h3', 'h4'])
                    if heading:
                        title = heading.get_text(strip=True)
                    else:
                        # Use the link text itself
                        title = link.get_text(strip=True)
                    
                    # Clean up the title
                    if title:
                        # Remove "Charlie Spears" from title if it got included
                        title = title.replace('Charlie Spears', '').strip()
                        # Remove date patterns from title
                        title = re.sub(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}', '', title).strip()
                        
                        # Skip if title is too short or empty
                        if len(title) < 5:
                            continue
                    
                    # Look for dates
                    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}', container_text)
                    date = date_match.group() if date_match else None
                    
                    if title and href not in seen_urls:
                        seen_urls.add(href)
                        
                        # Normalize URL
                        if href.startswith('/'):
                            href = f"https://newsletter.blockspacemedia.com{href}"
                        
                        articles.append({
                            'title': title,
                            'url': href,
                            'date': date,
                            'author': 'Charlie Spears'
                        })
                        print(f"  ✓ Found: {title[:50]}...")
                    break
        
        # Remove duplicates based on URL
        unique_articles = []
        seen = set()
        for article in articles:
            if article['url'] not in seen:
                seen.add(article['url'])
                unique_articles.append(article)
        
        print(f"\n📝 Found {len(unique_articles)} articles by Charlie Spears")
        return unique_articles
        
    except requests.RequestException as e:
        print(f"❌ Error fetching page: {e}")
        return []
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def save_articles(articles):
    """Save articles to JSON file"""
    
    output = {
        'last_updated': datetime.now().isoformat(),
        'count': len(articles),
        'articles': articles
    }
    
    with open('articles.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"💾 Saved to articles.json")

if __name__ == '__main__':
    articles = scrape_blockspace_articles()
    save_articles(articles)
    print("✅ Done!")
