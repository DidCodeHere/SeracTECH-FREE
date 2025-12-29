import asyncio
import logging
import os
import json
from datetime import datetime, timedelta
from scraper.idox import IdoxScraper
from scraper.northgate import NorthgateScraper
from scraper.planning_api import PlanningDataAPIScraper, COUNCIL_ORG_ENTITIES
from scraper.geocoder import Geocoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - can be overridden by environment variables
MOCK_MODE = os.environ.get('SCRAPER_MOCK_MODE', 'false').lower() == 'true'
OUTPUT_DIR = os.environ.get('SCRAPER_OUTPUT_DIR', 'frontend/public/data') # Default to frontend public dir
DAYS_TO_SCRAPE = int(os.environ.get('SCRAPER_DAYS', '30'))

# UK Councils to scrape
COUNCILS = [
    # --- API Accessible Councils ---
    {
        "name": "Doncaster",
        "type": "api",
        "enabled": True
    },
    
    # --- Major Cities (Idox) ---
    {
        "name": "Leeds",
        "type": "idox",
        "url": "https://publicaccess.leeds.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Manchester",
        "type": "idox",
        "url": "https://pa.manchester.gov.uk/online-applications",
        "enabled": True
    },
    # Westminster removed due to connection issues
    {
        "name": "Bristol",
        "type": "idox",
        "url": "https://planningonline.bristol.gov.uk/online-applications",
        "enabled": True
    },

    # --- London Boroughs (Idox) ---
    {
        "name": "Lambeth",
        "type": "idox",
        "url": "https://planning.lambeth.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Tower Hamlets",
        "type": "idox",
        "url": "https://development.towerhamlets.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Bromley",
        "type": "idox",
        "url": "https://searchapplications.bromley.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Croydon",
        "type": "idox",
        "url": "https://publicaccess3.croydon.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Ealing",
        "type": "idox",
        "url": "https://pam.ealing.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Greenwich",
        "type": "idox",
        "url": "https://planning.royalgreenwich.gov.uk/online-applications",
        "enabled": True
    },

    # --- Other Major Cities (Idox) ---
    {
        "name": "Nottingham",
        "type": "idox",
        "url": "https://publicaccess.nottinghamcity.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Glasgow",
        "type": "idox",
        "url": "https://publicaccess.glasgow.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Newcastle",
        "type": "idox",
        "url": "https://publicaccessapplications.newcastle.gov.uk/online-applications",
        "enabled": True
    },

    # --- Local Councils (Hampshire/South) ---
    {
        "name": "Portsmouth",
        "type": "idox",
        "url": "https://publicaccess.portsmouth.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Southampton", 
        "type": "idox",
        "url": "https://planningpublicaccess.southampton.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Fareham",
        "type": "northgate", 
        "url": "http://www.fareham.gov.uk/casetrackerplanning",
        "enabled": True
    },
    {
        "name": "Havant",
        "type": "idox",
        "url": "https://planningpublicaccess.havant.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Gosport",
        "type": "idox", 
        "url": "https://publicaccess.gosport.gov.uk/online-applications",
        "enabled": True
    },
    {
        "name": "Winchester",
        "type": "idox",
        "url": "https://planningapps.winchester.gov.uk/online-applications",
        "enabled": False
    },
    {
        "name": "Eastleigh",
        "type": "idox",
        "url": "https://planning.eastleigh.gov.uk/s/public-register", # Salesforce?
        "enabled": False
    },
    {
        "name": "Buckinghamshire",
        "type": "api",
        "enabled": False # Replaced by Doncaster
    },
]


def get_metadata_path() -> str:
    """Get path to the scraper metadata file."""
    return os.path.join(OUTPUT_DIR, '_metadata.json')


def load_metadata() -> dict:
    """Load scraper metadata (last run dates, etc.)."""
    path = get_metadata_path()
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}


def save_metadata(metadata: dict):
    """Save scraper metadata."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = get_metadata_path()
    with open(path, 'w') as f:
        json.dump(metadata, f, indent=2)


async def scrape_council(council: dict, geocoder: Geocoder, metadata: dict) -> int:
    """
    Scrape a single council and return number of applications found.
    """
    council_name = council["name"]
    council_key = council_name.lower().replace(" ", "_")
    
    # Determine date range
    last_scrape = metadata.get(council_key, {}).get('last_scrape')
    
    if last_scrape:
        # Incremental: start from last scrape date
        start_date = last_scrape
        logger.info(f"Incremental scrape for {council_name} from {start_date}")
    else:
        # Initial: scrape last N days
        start_date = (datetime.now() - timedelta(days=DAYS_TO_SCRAPE)).strftime('%Y-%m-%d')
        logger.info(f"Initial scrape for {council_name} from {start_date}")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create appropriate scraper
    if council["type"] == "api":
        scraper = PlanningDataAPIScraper(council_name, mock_mode=MOCK_MODE)
    elif council["type"] == "idox":
        scraper = IdoxScraper(council.get("url", ""), council_name, mock_mode=MOCK_MODE)
    elif council["type"] == "northgate":
        scraper = NorthgateScraper(council.get("url", ""), council_name, mock_mode=MOCK_MODE)
    else:
        logger.warning(f"Unknown scraper type: {council['type']}")
        return 0
    
    try:
        async with scraper:
            # Fetch applications
            applications = await scraper.fetch_applications(start_date, end_date)
            
            if not applications:
                logger.info(f"No applications found for {council_name}")
                return 0
            
            logger.info(f"Found {len(applications)} applications for {council_name}")
            
            # Geocode applications
            applications = await geocoder.enrich_applications(applications)
            
            # Save to sharded JSON files
            scraper.save_data(applications, OUTPUT_DIR)
            
            # Update metadata
            metadata[council_key] = {
                'last_scrape': end_date,
                'last_count': len(applications),
                'total_scraped': metadata.get(council_key, {}).get('total_scraped', 0) + len(applications)
            }
            
            return len(applications)
            
    except Exception as e:
        logger.error(f"Error scraping {council_name}: {e}")
        return 0


async def main():
    """
    Main orchestration script for scraping all enabled councils.
    """
    logger.info("=" * 60)
    logger.info("SeracTECH-FREE Scraper Starting")
    logger.info(f"Mock Mode: {MOCK_MODE}")
    logger.info(f"Output Directory: {OUTPUT_DIR}")
    logger.info(f"Days to Scrape: {DAYS_TO_SCRAPE}")
    logger.info("=" * 60)
    
    # Load metadata
    metadata = load_metadata()
    
    # Track stats
    total_applications = 0
    councils_scraped = 0
    
    # Create geocoder (shared across all scrapers)
    async with Geocoder() as geocoder:
        
        # Process each enabled council
        for council in COUNCILS:
            if not council.get("enabled", True):
                logger.info(f"Skipping disabled council: {council['name']}")
                continue
            
            logger.info(f"\n{'='*40}")
            logger.info(f"Processing: {council['name']}")
            logger.info(f"{'='*40}")
            
            count = await scrape_council(council, geocoder, metadata)
            total_applications += count
            
            if count > 0:
                councils_scraped += 1
            
            # Small delay between councils to be polite
            await asyncio.sleep(1)
    
    # Save updated metadata
    metadata['last_run'] = datetime.now().isoformat()
    metadata['last_run_total'] = total_applications
    save_metadata(metadata)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("SCRAPE COMPLETE")
    logger.info(f"Councils Scraped: {councils_scraped}")
    logger.info(f"Total Applications: {total_applications}")
    logger.info("=" * 60)
    
    return total_applications


if __name__ == "__main__":
    # Run the async main loop
    asyncio.run(main())
