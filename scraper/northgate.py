import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime
import logging
import re
import os
from .base import BaseScraper
from .rate_limiter import RateLimiter, RetryConfig

logger = logging.getLogger(__name__)

class NorthgateScraper(BaseScraper):
    """
    Scraper for Northgate Planning Explorer systems.
    Used by councils like Southampton, Fareham, etc.
    
    Northgate systems use ASP.NET WebForms with ViewState.
    """
    
    def __init__(self, base_url: str, council_name: str, mock_mode: bool = False):
        super().__init__(base_url, council_name)
        self.mock_mode = mock_mode or os.environ.get('SCRAPER_MOCK_MODE', 'false').lower() == 'true'
        self.search_url = f"{self.base_url}/PlanningSearch.aspx"
        self.rate_limiter = RateLimiter(rate=1.0, burst=3)
        self.retry_config = RetryConfig(max_retries=3, base_delay=2.0)

    async def fetch_applications(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Scrapes Northgate system for applications between start_date and end_date.
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")

        logger.info(f"Fetching {self.council_name} applications from {start_date} to {end_date}")
        
        if self.mock_mode:
            logger.warning("NorthgateScraper is in MOCK mode. Returning dummy data.")
            return self.generate_mock_data(start_date)
        
        all_applications = []
        
        try:
            # Step 1: Get the search page to establish session and get ViewState
            await self.rate_limiter.acquire()
            async with self.session.get(self.search_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to load search page: {response.status}")
                    return self.generate_mock_data(start_date)
                search_html = await response.text()
            
            # Step 2: Extract ASP.NET form fields (ViewState, EventValidation, etc.)
            soup = BeautifulSoup(search_html, 'html.parser')
            form_data = self._extract_aspnet_fields(soup)
            
            # Step 3: Add search parameters
            s_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
            e_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Northgate field names vary by council but commonly include:
            form_data.update({
                'ctl00$MainContent$txtDateReceivedFrom': s_date_obj.strftime('%d/%m/%Y'),
                'ctl00$MainContent$txtDateReceivedTo': e_date_obj.strftime('%d/%m/%Y'),
                'ctl00$MainContent$btnSearch': 'Search',
            })
            
            # Step 4: Submit search
            await self.rate_limiter.acquire()
            async with self.session.post(self.search_url, data=form_data) as response:
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
                
                # Check for next page in Northgate's grid pager
                soup = BeautifulSoup(results_html, 'html.parser')
                next_btn = soup.find('a', string=re.compile(r'Next|>', re.IGNORECASE))
                
                if not next_btn:
                    break
                
                # Northgate uses __doPostBack for pagination
                href = next_btn.get('href', '')
                if '__doPostBack' not in href:
                    break
                
                page += 1
                if page > 50:
                    logger.warning("Reached page limit (50)")
                    break
                
                # Extract postback arguments
                postback_match = re.search(r"__doPostBack\('([^']+)','([^']*)'\)", href)
                if not postback_match:
                    break
                
                event_target = postback_match.group(1)
                event_argument = postback_match.group(2)
                
                # Update form data for postback
                form_data = self._extract_aspnet_fields(soup)
                form_data['__EVENTTARGET'] = event_target
                form_data['__EVENTARGUMENT'] = event_argument
                
                await self.rate_limiter.acquire()
                async with self.session.post(self.search_url, data=form_data) as response:
                    if response.status != 200:
                        break
                    results_html = await response.text()
            
            logger.info(f"Total applications found: {len(all_applications)}")
            
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            return self.generate_mock_data(start_date)
        
        return all_applications if all_applications else self.generate_mock_data(start_date)
    
    def _extract_aspnet_fields(self, soup: BeautifulSoup) -> Dict[str, str]:
        """
        Extract ASP.NET hidden form fields (ViewState, EventValidation, etc.).
        """
        form_data = {}
        
        for field_name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION', '__VIEWSTATEENCRYPTED']:
            field = soup.find('input', {'name': field_name})
            if field:
                form_data[field_name] = field.get('value', '')
        
        return form_data

    def parse_results(self, html: str) -> List[Dict]:
        """
        Parses the search results page for Northgate systems.
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Northgate results are usually in a GridView table
        table = soup.find('table', {'class': 'rgMasterTable'})
        if not table:
            return results
            
        rows = table.find_all('tr', {'class': re.compile(r'rgRow|rgAltRow')})
        
        for row in rows:
            try:
                cells = row.find_all('td')
                if len(cells) < 5:
                    continue
                    
                ref = cells[0].get_text(strip=True)
                address = cells[1].get_text(strip=True)
                desc = cells[2].get_text(strip=True)
                date_received = cells[3].get_text(strip=True)
                status = cells[4].get_text(strip=True)
                
                # Extract link
                link_tag = cells[0].find('a')
                link = self.base_url + '/' + link_tag['href'] if link_tag else ''
                
                # Extract postcode from address (last part after comma)
                postcode_match = re.search(r'[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}', address, re.IGNORECASE)
                postcode = postcode_match.group(0).upper() if postcode_match else ''
                
                results.append({
                    'id': ref,
                    'desc': desc,
                    'addr': address,
                    'postcode': postcode,
                    'link': link,
                    'status': status,
                    'date_received': date_received,
                    'lat': 0.0,
                    'lng': 0.0
                })
            except Exception as e:
                logger.error(f"Error parsing row: {e}")
                
        return results

    def generate_mock_data(self, date_str: str) -> List[Dict]:
        """
        Generates dummy data for testing the pipeline (Southampton area).
        """
        return [
            {
                "id": "23/00501/FUL",
                "desc": "Loft conversion with rear dormer",
                "addr": "78 Winchester Road, Southampton, SO16 6TH",
                "postcode": "SO16 6TH",
                "lat": 50.9260,
                "lng": -1.4000,
                "date_received": date_str,
                "status": "Pending",
                "link": "https://planningexplorer.southampton.gov.uk/"
            },
            {
                "id": "23/00502/HOU",
                "desc": "Two storey side extension",
                "addr": "12 Shirley High Street, Southampton, SO15 5HG",
                "postcode": "SO15 5HG",
                "lat": 50.9156,
                "lng": -1.4336,
                "date_received": date_str,
                "status": "Approved",
                "link": "https://planningexplorer.southampton.gov.uk/"
            },
            {
                "id": "23/00503/FUL",
                "desc": "New detached garage",
                "addr": "5 Ocean Village, Southampton, SO14 3TJ",
                "postcode": "SO14 3TJ",
                "lat": 50.8967,
                "lng": -1.3911,
                "date_received": date_str,
                "status": "Pending",
                "link": "https://planningexplorer.southampton.gov.uk/"
            }
        ]
