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
  // In production (GitHub Pages), this will be relative to the base URL
  const url = `/data/${area}/${sector}.json`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    if (response.status === 404) {
      return []; // No data for this sector yet
    }
    throw new Error('Network response was not ok');
  }
  
  return response.json();
};

export const usePlanningData = (postcode: string) => {
  // Extract sector from postcode (e.g., "PO1 2AB" -> "PO1")
  const sector = postcode.split(' ')[0].toUpperCase();

  return useQuery({
    queryKey: ['planningData', sector],
    queryFn: () => fetchPlanningData(sector),
    enabled: !!sector, // Only run if we have a sector
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
    retry: 1,
  });
};
