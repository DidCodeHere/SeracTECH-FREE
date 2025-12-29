import aiohttp
import asyncio
import json
import os
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """
    Abstract base class for planning application scrapers.
    Implements the Strategy Pattern and handles async requests.
    """

    def __init__(self, base_url: str, council_name: str):
        self.base_url = base_url
        self.council_name = council_name
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def fetch_applications(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Fetch planning applications for a given date range.
        Must be implemented by concrete classes (Idox, Northgate, etc.).
        """
        pass

    async def get_existing_data(self, filepath: str) -> List[Dict]:
        """
        Load existing JSON data to support incremental scraping.
        """
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.warning(f"Corrupt JSON found at {filepath}. Starting fresh.")
                return []
        return []

    def get_latest_date(self, data: List[Dict]) -> Optional[str]:
        """
        Find the most recent 'date_received' in the existing dataset.
        Assumes date format YYYY-MM-DD.
        """
        if not data:
            return None
        
        dates = [item.get('date_received') for item in data if item.get('date_received')]
        if not dates:
            return None
            
        return max(dates)

    def save_data(self, data: List[Dict], output_dir: str = "data"):
        """
        Save data to minified JSON files, sharded by Postcode Sector.
        """
        # Group by Postcode Sector (e.g., PO1, PO2)
        shards = {}
        
        for app in data:
            postcode = app.get('postcode')
            if not postcode:
                continue
            
            # Extract sector: "PO1 2AB" -> "PO1"
            # Simple logic: Split by space, take first part. 
            # Better logic might be needed for complex UK postcodes, but this works for standard ones.
            sector = postcode.split(' ')[0]
            
            # Create area folder (e.g., PO)
            area = sector[:2] # "PO"
            if area.isdigit(): # Handle cases like "W1" -> "W"
                 area = sector[:1]

            if sector not in shards:
                shards[sector] = []
            shards[sector].append(app)

        # Write shards to disk
        for sector, apps in shards.items():
            area = sector[:2]
            if area[1].isdigit():
                area = area[0]
                
            sector_dir = os.path.join(output_dir, area)
            os.makedirs(sector_dir, exist_ok=True)
            
            filepath = os.path.join(sector_dir, f"{sector}.json")
            
            # Merge with existing data if file exists (to avoid overwriting history)
            existing_apps = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    try:
                        existing_apps = json.load(f)
                    except:
                        pass
            
            # Deduplicate based on ID
            existing_ids = {app['id'] for app in existing_apps}
            new_apps = [app for app in apps if app['id'] not in existing_ids]
            
            combined_apps = existing_apps + new_apps
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(combined_apps, f, separators=(',', ':')) # Minified
            
            logger.info(f"Saved {len(new_apps)} new applications to {filepath}")

    async def run(self):
        """
        Main execution method.
        """
        # This is a simplified run logic. In a real scenario, you'd iterate over known sectors 
        # or have a master list of areas to scrape.
        # For the MVP, we might just scrape a specific date range.
        
        logger.info(f"Starting scrape for {self.council_name}")
        
        # Example: Scrape last 30 days
        # In a real implementation, we would check existing data first
        # latest_date = self.get_latest_date(existing_data)
        # start_date = latest_date if latest_date else (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # For now, let's assume the concrete class handles the date logic or we pass it in.
        # This method is a placeholder for the orchestration logic.
        pass
