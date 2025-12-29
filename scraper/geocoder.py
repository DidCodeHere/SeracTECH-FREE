"""
Geocoding service using postcodes.io API.
Free, no API key required, rate limited to 100 req/s.
"""
import aiohttp
import asyncio
import logging
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)

class Geocoder:
    """
    Geocodes UK postcodes using postcodes.io API.
    Implements bulk lookup for efficiency.
    """
    
    BASE_URL = "https://api.postcodes.io"
    BULK_LIMIT = 100  # Max postcodes per bulk request
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self._session = session
        self._owns_session = session is None
        self._cache: Dict[str, Tuple[float, float]] = {}
    
    async def __aenter__(self):
        if self._owns_session:
            self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._owns_session and self._session:
            await self._session.close()
    
    async def lookup_single(self, postcode: str) -> Optional[Tuple[float, float]]:
        """
        Look up a single postcode. Returns (lat, lng) or None.
        """
        # Check cache first
        normalized = postcode.upper().replace(" ", "")
        if normalized in self._cache:
            return self._cache[normalized]
        
        if not self._session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        
        try:
            url = f"{self.BASE_URL}/postcodes/{postcode.replace(' ', '%20')}"
            async with self._session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 200 and data.get('result'):
                        lat = data['result']['latitude']
                        lng = data['result']['longitude']
                        self._cache[normalized] = (lat, lng)
                        return (lat, lng)
                elif response.status == 404:
                    logger.debug(f"Postcode not found: {postcode}")
                else:
                    logger.warning(f"Geocode error for {postcode}: {response.status}")
        except Exception as e:
            logger.error(f"Geocode exception for {postcode}: {e}")
        
        return None
    
    async def lookup_bulk(self, postcodes: List[str]) -> Dict[str, Tuple[float, float]]:
        """
        Look up multiple postcodes in bulk. Returns dict of postcode -> (lat, lng).
        More efficient than single lookups for large datasets.
        """
        if not self._session:
            raise RuntimeError("Session not initialized. Use 'async with' context manager.")
        
        results: Dict[str, Tuple[float, float]] = {}
        
        # Filter out cached postcodes
        uncached = []
        for pc in postcodes:
            normalized = pc.upper().replace(" ", "")
            if normalized in self._cache:
                results[pc] = self._cache[normalized]
            else:
                uncached.append(pc)
        
        if not uncached:
            return results
        
        # Process in batches of BULK_LIMIT
        for i in range(0, len(uncached), self.BULK_LIMIT):
            batch = uncached[i:i + self.BULK_LIMIT]
            
            try:
                url = f"{self.BASE_URL}/postcodes"
                payload = {"postcodes": batch}
                
                async with self._session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('status') == 200 and data.get('result'):
                            for item in data['result']:
                                query = item.get('query', '')
                                result = item.get('result')
                                
                                if result:
                                    lat = result['latitude']
                                    lng = result['longitude']
                                    normalized = query.upper().replace(" ", "")
                                    self._cache[normalized] = (lat, lng)
                                    results[query] = (lat, lng)
                    else:
                        logger.warning(f"Bulk geocode error: {response.status}")
                        
            except Exception as e:
                logger.error(f"Bulk geocode exception: {e}")
            
            # Small delay between batches to be polite
            if i + self.BULK_LIMIT < len(uncached):
                await asyncio.sleep(0.1)
        
        return results
    
    async def enrich_applications(self, applications: List[Dict]) -> List[Dict]:
        """
        Add lat/lng coordinates to a list of applications.
        Uses bulk lookup for efficiency.
        """
        # Collect postcodes that need geocoding
        postcodes_to_lookup = []
        for app in applications:
            if app.get('postcode') and (app.get('lat', 0) == 0 or app.get('lng', 0) == 0):
                postcodes_to_lookup.append(app['postcode'])
        
        if not postcodes_to_lookup:
            return applications
        
        # Deduplicate
        unique_postcodes = list(set(postcodes_to_lookup))
        logger.info(f"Geocoding {len(unique_postcodes)} unique postcodes...")
        
        # Bulk lookup
        coords = await self.lookup_bulk(unique_postcodes)
        
        # Apply coordinates to applications
        enriched = 0
        for app in applications:
            pc = app.get('postcode')
            if pc and pc in coords:
                app['lat'], app['lng'] = coords[pc]
                enriched += 1
        
        logger.info(f"Enriched {enriched} applications with coordinates")
        return applications
