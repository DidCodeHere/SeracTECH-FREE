import { useQuery } from '@tanstack/react-query';

interface PostcodeResult {
  postcode: string;
  latitude: number;
  longitude: number;
  region: string;
  admin_district: string;
}

const fetchPostcodeData = async (postcode: string): Promise<PostcodeResult | null> => {
  if (!postcode || postcode.length < 3) return null;
  
  // Clean the postcode
  const cleanPostcode = postcode.trim().toUpperCase().replace(/\s+/g, '');
  
  const response = await fetch(`https://api.postcodes.io/postcodes/${cleanPostcode}`);
  
  if (!response.ok) {
    if (response.status === 404) {
      return null; // Invalid postcode
    }
    throw new Error('Failed to fetch postcode data');
  }
  
  const data = await response.json();
  
  if (data.status !== 200 || !data.result) {
    return null;
  }
  
  return {
    postcode: data.result.postcode,
    latitude: data.result.latitude,
    longitude: data.result.longitude,
    region: data.result.region,
    admin_district: data.result.admin_district,
  };
};

export const usePostcodeLookup = (postcode: string) => {
  return useQuery({
    queryKey: ['postcode', postcode],
    queryFn: () => fetchPostcodeData(postcode),
    enabled: !!postcode && postcode.length >= 3,
    staleTime: 1000 * 60 * 60 * 24, // Cache for 24 hours (postcodes don't change)
    retry: 1,
  });
};
