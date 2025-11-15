"""
Web scraping service for extracting content from URLs.
Handles various website formats with special support for Wikipedia.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import re
from urllib.parse import urlparse
from ..config import settings


class ScraperError(Exception):
    """Custom exception for scraping errors."""
    pass


class WebScraper:
    """Web scraper for extracting article content from URLs."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.timeout = settings.REQUEST_TIMEOUT
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format and security.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If URL is invalid or blocked
        """
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        parsed = urlparse(url)
        
        # Prevent SSRF attacks - block internal networks
        blocked_hosts = [
            'localhost', '127.0.0.1', '0.0.0.0',
            '10.', '172.16.', '192.168.',
            'metadata.google.internal'
        ]
        
        for blocked in blocked_hosts:
            if parsed.netloc.startswith(blocked):
                raise ValueError("Access to internal networks is not allowed")
        
        return True
    
    def scrape_url(self, url: str) -> Dict:
        """
        Scrape content from a URL.
        
        Args:
            url: URL of the article to scrape
            
        Returns:
            Dictionary containing:
                - title: Article title
                - full_text: Complete article text
                - sections: List of section dictionaries with heading and content
                - word_count: Number of words in the article
                - is_wikipedia: Boolean indicating if source is Wikipedia
                
        Raises:
            ScraperError: If scraping fails
        """
        try:
            # Validate URL
            self.validate_url(url)
            
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            print(f"DEBUG: Fetched page, status: {response.status_code}, content length: {len(response.content)}")
            
            # Debug: Save a snippet of the HTML to see what we got
            html_preview = response.text[:2000]
            print(f"DEBUG: HTML preview (first 500 chars): {html_preview[:500]}")
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check if it's Wikipedia
            is_wikipedia = 'wikipedia.org' in url.lower()
            
            if is_wikipedia:
                return self._scrape_wikipedia(soup, url)
            else:
                return self._scrape_generic(soup, url)
                
        except requests.exceptions.Timeout:
            raise ScraperError("Request timed out. The page may be too large or slow to respond.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise ScraperError("Page not found (404). Please check the URL.")
            elif e.response.status_code == 403:
                raise ScraperError("Access forbidden (403). The website may be blocking automated requests.")
            else:
                raise ScraperError(f"HTTP error {e.response.status_code}: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise ScraperError(f"Failed to fetch the page: {str(e)}")
        except Exception as e:
            raise ScraperError(f"Unexpected error during scraping: {str(e)}")
    
    def _scrape_wikipedia(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Scrape Wikipedia articles with special handling.
        
        Args:
            soup: BeautifulSoup object
            url: Original URL
            
        Returns:
            Scraped content dictionary
        """
        # Extract title
        title_elem = soup.find('h1', {'class': 'firstHeading'}) or soup.find('h1')
        title = title_elem.text.strip() if title_elem else "Untitled Article"
        
        # Get main content – some pages render multiple mw-parser-output blocks.
        content_div = None
        candidate_divs = soup.find_all('div', {'class': 'mw-parser-output'})
        for candidate in candidate_divs:
            paragraph_count = len(candidate.find_all('p'))
            if paragraph_count >= 3:
                content_div = candidate
                break
        if not content_div and candidate_divs:
            # Fall back to the first candidate if none met the threshold
            content_div = candidate_divs[0]
        
        if not content_div:
            # Try legacy selectors
            legacy = soup.find('div', {'id': 'mw-content-text'})
            if legacy:
                content_div = legacy.find('div', {'class': 'mw-parser-output'}) or legacy
        
        if not content_div:
            raise ScraperError("Could not find main content area in Wikipedia article")        # First, let's check paragraph count BEFORE any removal
        paras_before_removal = content_div.find_all('p')
        print(f"DEBUG: Paragraphs before removal: {len(paras_before_removal)}")
        
        # Remove unwanted elements FIRST before extracting text
        for tag_name in ['script', 'style', 'nav', 'footer', 'aside']:
            for elem in content_div.find_all(tag_name):
                elem.decompose()
        
        # Remove reference links and edit sections
        for span in content_div.find_all('span', {'class': ['mw-editsection', 'reference']}):
            span.decompose()
        
        # Remove infoboxes and navboxes, but keep other tables
        tables_to_remove = []
        for table in content_div.find_all('table'):
            table_classes = table.get('class', [])
            if any(cls in ['infobox', 'navbox', 'vertical-navbox', 'sidebar'] for cls in table_classes):
                tables_to_remove.append(table)

        # Remove the tables
        for table in tables_to_remove:
            table.decompose()
        
        # Remove superscript references
        for sup in content_div.find_all('sup', {'class': 'reference'}):
            sup.decompose()
        
        # Extract all paragraphs
        paragraphs = content_div.find_all('p')
        full_text_parts = []
        
        print(f"DEBUG: Found {len(paragraphs)} paragraphs in total")  # Debug
        
        for p in paragraphs:
            text = self._clean_text(p.get_text())
            if text and len(text) > 10:  # Filter very short paragraphs (reduced threshold)
                full_text_parts.append(text)
        
        print(f"DEBUG: {len(full_text_parts)} paragraphs passed filter")  # Debug
        
        # Extract sections with headings
        sections = []
        headings = content_div.find_all(['h2', 'h3'])
        
        # Add introduction
        if full_text_parts:
            intro = ' '.join(full_text_parts[:3])  # First 3 paragraphs
            sections.append({
                'heading': 'Introduction',
                'content': intro
            })
        
        # Extract other sections
        for i, heading in enumerate(headings[:10]):  # Limit to first 10 sections
            heading_text = self._clean_text(heading.get_text())
            
            # Skip certain sections
            if heading_text.lower() in ['references', 'external links', 'see also', 
                                        'notes', 'further reading', 'bibliography']:
                continue
            
            # Get content paragraphs after this heading
            section_paras = []
            current = heading.find_next_sibling()
            
            while current and current.name not in ['h2', 'h3']:
                if current.name == 'p':
                    text = self._clean_text(current.get_text())
                    if text and len(text) > 10:  # Reduced threshold
                        section_paras.append(text)
                current = current.find_next_sibling()
                
                # Limit section length
                if len(section_paras) >= 3:
                    break
            
            if section_paras:
                sections.append({
                    'heading': heading_text,
                    'content': ' '.join(section_paras)
                })
        
        # Combine all text
        full_text = ' '.join(full_text_parts)
        word_count = len(full_text.split())
        
        print(f"DEBUG: Total word count: {word_count}, Min required: {settings.MIN_CONTENT_WORDS}")  # Debug
        
        # Add debug info if scraping fails
        if word_count < settings.MIN_CONTENT_WORDS:
            # Log what we found for debugging
            debug_info = f"Found {len(paragraphs)} paragraphs, {len(full_text_parts)} passed filter"
            raise ScraperError(
                f"Article is too short ({word_count} words). "
                f"Minimum required: {settings.MIN_CONTENT_WORDS} words. "
                f"Debug: {debug_info}"
            )
        
        return {
            'title': title,
            'full_text': full_text,
            'sections': sections,
            'word_count': word_count,
            'is_wikipedia': True
        }
        
        # Validate minimum content
        if word_count < settings.MIN_CONTENT_WORDS:
            raise ScraperError(
                f"Article is too short ({word_count} words). "
                f"Minimum required: {settings.MIN_CONTENT_WORDS} words."
            )
        
        return {
            'title': title,
            'full_text': full_text,
            'sections': sections,
            'word_count': word_count,
            'is_wikipedia': True
        }
    
    def _scrape_generic(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Scrape generic websites.
        
        Args:
            soup: BeautifulSoup object
            url: Original URL
            
        Returns:
            Scraped content dictionary
        """
        # Extract title
        title_elem = (soup.find('h1') or 
                     soup.find('title') or 
                     soup.find('meta', {'property': 'og:title'}))
        
        if title_elem:
            if title_elem.name == 'meta':
                title = title_elem.get('content', 'Untitled Article')
            else:
                title = title_elem.text.strip()
        else:
            title = "Untitled Article"
        
        # Try to find main content area
        content_area = (soup.find('article') or 
                       soup.find('main') or 
                       soup.find('div', {'class': re.compile(r'content|article|post', re.I)}) or
                       soup.find('body'))
        
        if not content_area:
            raise ScraperError("Could not identify main content area")
        
        # Remove unwanted elements
        for unwanted in content_area.find_all(['script', 'style', 'nav', 'footer', 
                                               'aside', 'header', 'form']):
            unwanted.decompose()
        
        # Extract text from paragraphs
        paragraphs = content_area.find_all(['p', 'h1', 'h2', 'h3', 'h4'])
        
        sections = []
        current_section = {'heading': 'Main Content', 'content': ''}
        text_parts = []
        
        for elem in paragraphs:
            if elem.name in ['h1', 'h2', 'h3', 'h4']:
                # Save previous section
                if current_section['content']:
                    sections.append(current_section.copy())
                # Start new section
                current_section = {
                    'heading': self._clean_text(elem.text),
                    'content': ''
                }
            elif elem.name == 'p':
                text = self._clean_text(elem.text)
                if text:
                    current_section['content'] += ' ' + text
                    text_parts.append(text)
        
        # Add last section
        if current_section['content']:
            sections.append(current_section)
        
        full_text = ' '.join(text_parts)
        word_count = len(full_text.split())
        
        # Validate minimum content
        if word_count < settings.MIN_CONTENT_WORDS:
            raise ScraperError(
                f"Article is too short ({word_count} words). "
                f"Minimum required: {settings.MIN_CONTENT_WORDS} words."
            )
        
        return {
            'title': title,
            'full_text': full_text,
            'sections': sections,
            'word_count': word_count,
            'is_wikipedia': False
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove citation brackets
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[edit\]', '', text)
        text = re.sub(r'\[citation needed\]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip and return
        return text.strip()


# Create singleton instance
scraper = WebScraper()
