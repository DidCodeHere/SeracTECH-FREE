import { useMemo } from 'react';
import { haversineDistance } from '../utils/distance';

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

interface FilteredApplication extends PlanningApplication {
  distance: number; // Distance in km
}

/**
 * Hook to filter applications by radius from a center point.
 * Uses memoization to prevent recalculating distances on every render.
 */
export const useRadiusFilter = (
  applications: PlanningApplication[],
  centerLat: number | null,
  centerLng: number | null,
  radiusKm: number
): FilteredApplication[] => {
  return useMemo(() => {
    if (!centerLat || !centerLng || !applications.length) {
      // If no center point, return all applications with distance 0
      return applications.map(app => ({ ...app, distance: 0 }));
    }

    return applications
      .map((app) => {
        if (!app.lat || !app.lng) {
          return { ...app, distance: Infinity };
        }
        const distance = haversineDistance(centerLat, centerLng, app.lat, app.lng);
        return { ...app, distance };
      })
      .filter((app) => app.distance <= radiusKm)
      .sort((a, b) => a.distance - b.distance); // Sort by closest first
  }, [applications, centerLat, centerLng, radiusKm]);
};
