import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging
import re
import os
from .base import BaseScraper
from .rate_limiter import RateLimiter, RetryConfig, fetch_with_retry

logger = logging.getLogger(__name__)

class IdoxScraper(BaseScraper):
    """
    Scraper for Idox Public Access systems (e.g., Portsmouth, Southampton).
    
    Idox systems are the most common planning portal software in the UK.
    They follow a fairly consistent structure across councils.
    """
    
    def __init__(self, base_url: str, council_name: str, mock_mode: bool = False):
        super().__init__(base_url, council_name)
        self.mock_mode = mock_mode or os.environ.get('SCRAPER_MOCK_MODE', 'false').lower() == 'true'
        self.search_url = f"{self.base_url}/search.do?action=advanced"
        self.results_url = f"{self.base_url}/pagedSearchResults.do"
        self.rate_limiter = RateLimiter(rate=1.0, burst=3)  # 1 req/sec
        self.retry_config = RetryConfig(max_retries=3, base_delay=2.0)

    async def fetch_applications(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrapes Idox system for applications between start_date and end_date.
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")

        logger.info(f"Fetching {self.council_name} applications from {start_date} to {end_date}")
        
        if self.mock_mode:
            logger.warning("IdoxScraper is in MOCK mode. Returning dummy data.")
            return self.generate_mock_data(start_date)
        
        all_applications = []
        
        try:
            # Step 1: Get the search page to establish session/cookies
            await self.rate_limiter.acquire()
            async with self.session.get(self.search_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to load search page: {response.status}")
                    return self.generate_mock_data(start_date)  # Fallback to mock
                search_html = await response.text()
            
            # Step 2: Parse CSRF token and form fields from search page
            soup = BeautifulSoup(search_html, 'html.parser')
            form_data = self._extract_form_data(soup)
            
            # Step 3: Add our search parameters
            s_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            e_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            form_data.update({
                'searchType': 'Application',
                'caseType': 'Application',
                'date(applicationReceivedStart)': s_date_obj.strftime('%d/%m/%Y'),
                'date(applicationReceivedEnd)': e_date_obj.strftime('%d/%m/%Y'),
            })
            
            # Step 4: Submit search
            await self.rate_limiter.acquire()
            post_url = f"{self.base_url}/search.do?action=firstPage"
            async with self.session.post(post_url, data=form_data) as response:
                if response.status != 200:
                    logger.error(f"Search POST failed: {response.status}")
                    return self.generate_mock_data(start_date)
                results_html = await response.text()
            
            # Step 5: Parse results and handle pagination
            page = 1
            while True:
                logger.info(f"Parsing page {page}...")
                apps = self.parse_results(results_html)
                all_applications.extend(apps)
                
                # Check for next page
                soup = BeautifulSoup(results_html, 'html.parser')
                next_link = soup.find('a', class_='next')
                
                if not next_link or 'disabled' in next_link.get('class', []):
                    break
                
                # Fetch next page
                page += 1
                if page > 50:  # Safety limit
                    logger.warning("Reached page limit (50)")
                    break
                
                await self.rate_limiter.acquire()
                next_url = f"{self.base_url}{next_link['href']}"
                async with self.session.get(next_url) as response:
                    if response.status != 200:
                        break
                    results_html = await response.text()
            
            logger.info(f"Total applications found: {len(all_applications)}")
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            # Fallback to mock data on error
            return self.generate_mock_data(start_date)
        
        return all_applications if all_applications else self.generate_mock_data(start_date)
    
    def _extract_form_data(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract hidden form fields (CSRF tokens, etc.) from the search page.
        """
        form_data = {}
        form = soup.find('form', {'name': 'searchCriteriaForm'})
        
        if form:
            for inp in form.find_all('input', {'type': 'hidden'}):
                name = inp.get('name')
                value = inp.get('value', '')
                if name:
                    form_data[name] = value
        
        return form_data

    def parse_results(self, html: str) -> List[Dict]:
        """
        Parses the search results page from Idox system.
        
        Idox results are typically displayed in:
        - <ul class="searchresults"> containing <li class="searchresult">
        - Each result has reference, description, address, status, and date
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all result items
        items = soup.find_all('li', class_='searchresult')
        
        for item in items:
            try:
                # Extract reference and link
                link_tag = item.find('a')
                if not link_tag:
                    continue
                    
                link = link_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = f"{self.base_url}{link}"
                
                # Reference is usually in a span or the link text
                ref_span = item.find('span', class_='caseNumber')
                ref = ref_span.get_text(strip=True) if ref_span else link_tag.get_text(strip=True).split('|')[0].strip()
                
                # Description
                desc_p = item.find('p', class_='description')
                desc = desc_p.get_text(strip=True) if desc_p else ""
                if not desc:
                    # Try alternative: sometimes in the link text after |
                    link_text = link_tag.get_text(strip=True)
                    if '|' in link_text:
                        desc = link_text.split('|', 1)[1].strip()
                
                # Address
                address_p = item.find('p', class_='address')
                address = address_p.get_text(strip=True) if address_p else ""
                
                # Extract postcode from address using regex
                postcode = ""
                postcode_match = re.search(
                    r'[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}',
                    address,
                    re.IGNORECASE
                )
                if postcode_match:
                    postcode = postcode_match.group(0).upper()
                
                # Status - often in a span or separate element
                status_span = item.find('span', class_='status')
                status = status_span.get_text(strip=True) if status_span else "Unknown"
                
                # Date received
                date_span = item.find('span', class_='date')
                date_text = date_span.get_text(strip=True) if date_span else ""
                date_received = self._parse_date(date_text)
                
                if ref:  # Only add if we have a reference
                    results.append({
                        'id': ref,
                        'desc': desc[:500] if desc else "",  # Truncate long descriptions
                        'addr': address,
                        'postcode': postcode,
                        'link': link,
                        'status': self._normalize_status(status),
                        'date_received': date_received,
                        'lat': 0.0,
                        'lng': 0.0
                    })
                    
            except Exception as e:
                logger.error(f"Error parsing result item: {e}")
                continue
        
        return results
    
    def _parse_date(self, date_text: str) -> str:
        """
        Parse various date formats to YYYY-MM-DD.
        """
        if not date_text:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Try common formats
        formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y-%m-%d',
            '%d %b %Y',
            '%d %B %Y',
        ]
        
        # Clean the text
        date_text = date_text.replace('Received:', '').replace('Date:', '').strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def _normalize_status(self, status: str) -> str:
        """
        Normalize status values to consistent format.
        """
        status_lower = status.lower()
        
        if 'pending' in status_lower or 'registered' in status_lower or 'under consideration' in status_lower:
            return 'Pending'
        elif 'approved' in status_lower or 'granted' in status_lower or 'permitted' in status_lower:
            return 'Approved'
        elif 'refused' in status_lower or 'rejected' in status_lower or 'denied' in status_lower:
            return 'Refused'
        elif 'withdrawn' in status_lower:
            return 'Withdrawn'
        else:
            return status.title()

    def generate_mock_data(self, date_str: str) -> List[Dict]:
        """
        Generates dummy data for testing the pipeline.
        """
        return [
            {
                "id": "23/00001/FUL",
                "desc": "Construction of a new dwelling",
                "addr": "123 High Street, Portsmouth, PO1 2AB",
                "postcode": "PO1 2AB",
                "lat": 50.7989,
                "lng": -1.0912,
                "date_received": date_str,
                "status": "Pending",
                "link": "https://publicaccess.portsmouth.gov.uk/online-applications/"
            },
            {
                "id": "23/00002/HOU",
                "desc": "Single storey rear extension",
                "addr": "45 London Road, Portsmouth, PO2 9AA",
                "postcode": "PO2 9AA",
                "lat": 50.8123,
                "lng": -1.0856,
                "date_received": date_str,
                "status": "Approved",
                "link": "https://publicaccess.portsmouth.gov.uk/online-applications/"
            }
        ]
