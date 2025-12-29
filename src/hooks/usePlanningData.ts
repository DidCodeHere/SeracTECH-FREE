import { useQuery } from '@tanstack/react-query';

interface PlanningApplication {
  id: string;
  desc: string;
  addr: string;
  postcode: string;
  lat: number;
  lng: number;
  date_received: string;
  status: string;
  link: string;
}

const fetchPlanningData = async (sector: string): Promise<PlanningApplication[]> => {
  if (!sector) return [];
  
  // Determine the area code (e.g., PO from PO1)
  const area = sector.substring(0, 2).replace(/\d/, '');
  
  // Construct the URL to the static JSON file
  // Use import.meta.env.BASE_URL for GitHub Pages compatibility
  const baseUrl = import.meta.env.BASE_URL || '/';
  const url = `${baseUrl}data/${area}/${sector}.json`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    if (response.status === 404) {
      return []; // No data for this sector yet
    }
    throw new Error('Network response was not ok');
  }
  
  return response.json();
};

// Fetch all applications from all areas
const fetchAllPlanningData = async (): Promise<PlanningApplication[]> => {
  const baseUrl = import.meta.env.BASE_URL || '/';
  // Fetch the metadata to find all available areas
  const metadataResponse = await fetch(`${baseUrl}data/_metadata.json`);
  if (!metadataResponse.ok) {
    return [];
  }
  
  // Get list of area folders by fetching index
  // We'll try common UK postcode area prefixes
  const areaPrefixes = ['BD', 'DN', 'E', 'EC', 'HA', 'LS', 'M', 'NW', 'PO', 'SE', 'SO', 'SW', 'UB', 'W', 'WF'];
  
  const allApplications: PlanningApplication[] = [];
  
  // Fetch data from each area in parallel
  const areaPromises = areaPrefixes.map(async (area) => {
    try {
      // Try to fetch the area's index or iterate through common sectors
      const sectorNumbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30'];
      
      const sectorPromises = sectorNumbers.map(async (num) => {
        const sector = `${area}${num}`;
        try {
          const response = await fetch(`${baseUrl}data/${area}/${sector}.json`);
          if (response.ok) {
            return await response.json() as PlanningApplication[];
          }
        } catch {
          // Sector doesn't exist, skip
        }
        return [];
      });
      
      const sectorResults = await Promise.all(sectorPromises);
      return sectorResults.flat();
    } catch {
      return [];
    }
  });
  
  const areaResults = await Promise.all(areaPromises);
  areaResults.forEach(apps => allApplications.push(...apps));
  
  return allApplications;
};

export const usePlanningData = (postcode: string) => {
  // Check if it's a "show all" request
  const isShowAll = postcode.toUpperCase() === 'ALL';
  
  // Extract sector from postcode (e.g., "PO1 2AB" -> "PO1")
  const sector = isShowAll ? 'ALL' : postcode.split(' ')[0].toUpperCase();

  return useQuery({
    queryKey: ['planningData', sector],
    queryFn: () => isShowAll ? fetchAllPlanningData() : fetchPlanningData(sector),
    enabled: !!sector, // Only run if we have a sector
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
    retry: 1,
  });
};
