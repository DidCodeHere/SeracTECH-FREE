import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import re
import os
import urllib.parse
from .base import BaseScraper
from .rate_limiter import RateLimiter, RetryConfig

logger = logging.getLogger(__name__)

class IdoxScraper(BaseScraper):
    """
    Scraper for Idox Public Access systems.
    """
    
    def __init__(self, base_url: str, council_name: str, mock_mode: bool = False):
        super().__init__(base_url, council_name)
        self.mock_mode = mock_mode
        self.rate_limiter = RateLimiter(rate=0.5, burst=2)
        self.retry_config = RetryConfig(max_retries=3, base_delay=2.0)

    async def fetch_applications(self, start_date: str, end_date: str) -> List[Dict]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        if self.mock_mode:
            logger.warning("IdoxScraper is in MOCK mode.")
            return self.generate_mock_data(start_date)
        
        logger.info(f"Fetching {self.council_name} applications from {start_date} to {end_date}")
        
        # Try Advanced Search
        try:
            apps = await self._search_advanced(start_date, end_date)
            if apps:
                return apps
        except Exception as e:
            logger.error(f"Advanced search failed for {self.council_name}: {e}")
        
        # Fallback to Weekly List
        logger.info("Falling back to Weekly List search")
        try:
            return await self._search_weekly_list(start_date, end_date)
        except Exception as e:
            logger.error(f"Weekly list search failed for {self.council_name}: {e}")
            return []

    async def _search_advanced(self, start_date: str, end_date: str) -> List[Dict]:
        # 1. Get search page to establish session and get form token
        search_url = f"{self.base_url}/search.do?action=advanced"
        async with self.session.get(search_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to load search page: {response.status}")
            html = await response.text()
        
        # 2. Parse form
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form', {'name': 'searchCriteriaForm'}) or soup.find('form', {'id': 'searchCriteriaForm'})
        if not form:
            # Try finding any form with action containing search.do
            form = soup.find('form', action=re.compile(r'search\.do'))
        
        if not form:
            raise Exception("Could not find search form")
            
        action = form.get('action', '')
        if not action.startswith('http'):
            action = urllib.parse.urljoin(self.base_url, action)
            
        data = {}
        for input_tag in form.find_all(['input', 'select']):
            name = input_tag.get('name')
            if not name:
                continue
            value = input_tag.get('value', '')
            if input_tag.name == 'select':
                # For select, get the selected option or first option
                selected = input_tag.find('option', selected=True)
                value = selected.get('value') if selected else ''
            
            data[name] = value
            
        # 3. Update with our criteria
        s_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        e_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        
        data.update({
            'searchType': 'Application',
            'searchCriteria.caseType': 'Application',
            'date(applicationReceivedStart)': s_date,
            'date(applicationReceivedEnd)': e_date
        })
        
        logger.debug(f"Submitting form to {action} with data: {data}")

        # 4. Submit form
        headers = {
            'Referer': search_url,
            'Origin': self.base_url
        }
        async with self.session.post(action, data=data, headers=headers) as response:
            if response.status != 200:
                raise Exception(f"Search submission failed: {response.status}")
            results_html = await response.text()
            
        return await self._parse_all_pages(results_html)

    async def _search_weekly_list(self, start_date: str, end_date: str) -> List[Dict]:
        url = f"{self.base_url}/search.do?action=weeklyList"
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to load weekly list page: {response.status}")
            html = await response.text()
            
        soup = BeautifulSoup(html, 'html.parser')
        form = soup.find('form', {'name': 'weeklyListForm'}) or soup.find('form', {'id': 'weeklyListForm'})
        
        # If no form, maybe we are already on the results page for the current week?
        # Or maybe the form has a different name.
        if not form:
             # Try to find the select directly
             pass
             
        week_select = soup.find('select', {'name': 'week'})
        if not week_select:
            logger.warning("Could not find week select in weekly list page")
            return []
            
        target_weeks = []
        s_date = datetime.strptime(start_date, '%Y-%m-%d')
        e_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        for option in week_select.find_all('option'):
            val = option.get('value')
            text = option.get_text(strip=True)
            if not val: continue
            
            try:
                # Text format: "25 Sep 2023" or "Week beginning 25 Sep 2023"
                date_text = text.replace("Week beginning", "").strip()
                week_date = datetime.strptime(date_text, '%d %b %Y')
                
                week_end = week_date + timedelta(days=6)
                
                if (week_date <= e_date and week_end >= s_date):
                    target_weeks.append(val)
            except Exception as e:
                logger.debug(f"Failed to parse week date {text}: {e}")
                continue
        
        logger.info(f"Found {len(target_weeks)} weeks matching date range")
        
        all_apps = []
        if not form:
             # If no form, we can't submit. But maybe we can construct URL?
             # Usually it's a POST.
             return []

        action = form.get('action', '')
        if not action.startswith('http'):
            action = urllib.parse.urljoin(self.base_url, action)

        for week_val in target_weeks:
            data = {}
            for input_tag in form.find_all('input', type='hidden'):
                data[input_tag.get('name')] = input_tag.get('value', '')
            
            # Handle radio buttons (e.g. dateType)
            for input_tag in form.find_all('input', type='radio'):
                name = input_tag.get('name')
                if name:
                    if input_tag.get('checked'):
                        data[name] = input_tag.get('value')
                    elif name == 'dateType' and 'dateType' not in data:
                        # Prefer Validated over Decided
                        if input_tag.get('value') == 'DC_Validated':
                            data[name] = 'DC_Validated'
            
            # Default dateType if still missing
            if 'dateType' not in data:
                data['dateType'] = 'DC_Validated'

            data['week'] = week_val
            data['searchType'] = 'Application'
            
            # Headers for politeness/anti-bot
            headers = {
                'Referer': url,
                'Origin': self.base_url
            }
            
            async with self.session.post(action, data=data, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    apps = await self._parse_all_pages(html)
                    logger.info(f"Weekly list week {week_val}: found {len(apps)} apps")
                    all_apps.extend(apps)
                    
        return all_apps

    async def _parse_all_pages(self, first_page_html: str) -> List[Dict]:
        all_apps = []
        current_html = first_page_html
        page = 1
        
        while True:
            apps = self.parse_results(current_html)
            if not apps:
                break
            all_apps.extend(apps)
            
            # Find next link
            soup = BeautifulSoup(current_html, 'html.parser')
            next_link = soup.find('a', class_='next')
            if not next_link:
                break
                
            href = next_link.get('href')
            if not href:
                break
                
            url = urllib.parse.urljoin(self.base_url, href)
            await self.rate_limiter.acquire()
            async with self.session.get(url) as response:
                if response.status != 200:
                    break
                current_html = await response.text()
            
            page += 1
            if page > 20: # Safety limit
                break
                
        return all_apps

    def parse_results(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        items = soup.find_all('li', class_='searchresult')
        for item in items:
            try:
                link_tag = item.find('a')
                if not link_tag: continue
                
                link = link_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = urllib.parse.urljoin(self.base_url, link)
                
                ref = link_tag.get_text(strip=True)
                desc = item.find('p', class_='description').get_text(strip=True) if item.find('p', class_='description') else ""
                address = item.find('p', class_='address').get_text(strip=True) if item.find('p', class_='address') else ""
                
                # Extract postcode
                postcode = ""
                match = re.search(r'([A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})', address, re.IGNORECASE)
                if match:
                    postcode = match.group(1).upper()
                
                date_received = datetime.now().strftime('%Y-%m-%d')
                date_span = item.find('span', class_='date') # Sometimes it's just text
                if not date_span:
                    # Try to find text like "Received: DD/MM/YYYY"
                    text = item.get_text()
                    match = re.search(r'Received:?\s*(\d{2}/\d{2}/\d{4})', text)
                    if match:
                        try:
                            date_received = datetime.strptime(match.group(1), '%d/%m/%Y').strftime('%Y-%m-%d')
                        except: pass
                
                results.append({
                    'id': ref,
                    'desc': desc,
                    'addr': address,
                    'postcode': postcode,
                    'link': link,
                    'status': 'Unknown', # Hard to parse from list sometimes
                    'date_received': date_received,
                    'lat': 0.0,
                    'lng': 0.0
                })
            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue
                
        return results

    def generate_mock_data(self, date_str: str) -> List[Dict]:
        return []
