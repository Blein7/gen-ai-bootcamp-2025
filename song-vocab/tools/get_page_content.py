import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

def get_page_content(url: str) -> Dict[str, Optional[str]]:
    """
    Fetch and extract content from a webpage
    
    Args:
        url (str): URL to fetch content from
        
    Returns:
        Dict with content and any errors
    """
    try:
        print(f"[get_page_content] Fetching URL: {url}")
        # Send request with common headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',  # Prioritize Japanese
            'Connection': 'keep-alive',
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"[get_page_content] Response status: {response.status_code}")
        response.raise_for_status()
        
        # Parse HTML
        print("[get_page_content] Parsing HTML...")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Try to find lyrics content based on the website
        content = None
        print("[get_page_content] Looking for lyrics content...")
        
        if 'j-lyric.net' in url:
            print("[get_page_content] Processing j-lyric.net...")
            lyrics_div = soup.find('p', {'id': 'Lyrics'})
            if lyrics_div:
                content = lyrics_div.get_text(separator='\n')
                
        elif 'utaten.com' in url:
            print("[get_page_content] Processing utaten.com...")
            lyrics_div = soup.find('div', class_='hiragana')
            if lyrics_div:
                content = lyrics_div.get_text(separator='\n')
                
        elif 'uta-net.com' in url:
            print("[get_page_content] Processing uta-net.com...")
            lyrics_div = soup.find('div', id='kashi_area')
            if lyrics_div:
                content = lyrics_div.get_text(separator='\n')
                
        elif 'lyrical-nonsense.com' in url:
            print("[get_page_content] Processing lyrical-nonsense.com...")
            lyrics_div = soup.find('div', class_='lyrics-original')
            if lyrics_div:
                content = lyrics_div.get_text(separator='\n')
                
        elif 'genius.com' in url:
            print("[get_page_content] Processing Genius lyrics...")
            # Updated selectors for Genius format
            selectors = [
                'div[class*="Lyrics__Container"]',  # Main lyrics container
                'div[data-lyrics-container="true"]', # Alternative container
                'div[class*="lyrics"]',             # Generic lyrics class
                'div.SongPageGriddesktop',          # New desktop layout
                'div[class*="SongPage__Section"]',  # Section container
                'div[class*="SongPage__LyricsWrapper"]', # Lyrics wrapper
            ]
            
            # Try each selector
            for selector in selectors:
                print(f"[get_page_content] Trying selector: {selector}")
                elements = soup.select(selector)
                if elements:
                    print(f"[get_page_content] Found {len(elements)} elements with selector: {selector}")
                    # Combine text from all matching elements
                    texts = []
                    for elem in elements:
                        # Remove unwanted elements
                        for unwanted in elem.find_all(['script', 'style', 'button', 'input']):
                            unwanted.decompose()
                        # Remove [Verse], [Chorus] etc. labels
                        for label in elem.find_all(class_=lambda x: x and any(word in x.lower() for word in ['label', 'tag', 'header', 'title'])):
                            label.decompose()
                        # Get text and clean it
                        text = elem.get_text(separator='\n').strip()
                        if text and not text.startswith(('About', 'Lyrics', 'Contributors')):
                            texts.append(text)
                    
                    if texts:
                        content = '\n\n'.join(text for text in texts if text)
                        # If we found actual lyrics (more than just headers), break
                        if len(content.split('\n')) > 3:
                            break
                    
        # If no specific container found, try common patterns
        if not content:
            print("[get_page_content] No specific lyrics container found, trying common patterns...")
            # Look for elements with "lyrics" in class or id
            lyrics_elements = soup.find_all(class_=lambda x: x and ('lyric' in x.lower() or '歌詞' in x))
            lyrics_elements.extend(soup.find_all(id=lambda x: x and ('lyric' in x.lower() or '歌詞' in x)))
            
            if lyrics_elements:
                print(f"[get_page_content] Found {len(lyrics_elements)} elements with lyrics")
                texts = []
                for elem in lyrics_elements:
                    text = elem.get_text(separator='\n').strip()
                    if text and not text.startswith(('About', 'Lyrics', 'Contributors')):
                        texts.append(text)
                if texts:
                    content = '\n\n'.join(texts)
            else:
                print("[get_page_content] No lyrics elements found, trying main content")
                # Try to find main content area
                main = soup.find('main') or soup.find(id='main') or soup.find(class_='main')
                if main:
                    text = main.get_text(separator='\n')
                    lines = [line.strip() for line in text.split('\n')]
                    content = '\n'.join(line for line in lines if line and not line.startswith(('About', 'Lyrics', 'Contributors')))
        
        if not content:
            print("[get_page_content] No content found")
            return {
                'content': None,
                'error': 'No lyrics content found',
                'url': url
            }
            
        # Clean up content
        print("[get_page_content] Cleaning content...")
        lines = []
        seen = set()  # Track unique lines to avoid duplicates
        for line in content.split('\n'):
            line = line.strip()
            # Keep empty lines for verse separation but remove duplicate empty lines
            # Also remove duplicate content lines
            if line:
                if line not in seen:
                    lines.append(line)
                    seen.add(line)
            elif lines and lines[-1]:  # Add empty line only if previous line wasn't empty
                lines.append(line)
        
        # Remove empty lines from start and end
        while lines and not lines[0]: lines.pop(0)
        while lines and not lines[-1]: lines.pop()
        
        cleaned_content = '\n'.join(lines)
        print(f"[get_page_content] Content length: {len(cleaned_content)} chars")
        
        # Validate content length
        if len(cleaned_content) < 50:
            print("[get_page_content] Content too short")
            return {
                'content': None,
                'error': 'Content too short to be lyrics',
                'url': url
            }
            
        print("[get_page_content] Successfully extracted lyrics")
        return {
            'content': cleaned_content,
            'error': None,
            'url': url
        }
        
    except Exception as e:
        print(f"[get_page_content] Error: {str(e)}")
        return {
            'content': None,
            'error': str(e),
            'url': url
        }