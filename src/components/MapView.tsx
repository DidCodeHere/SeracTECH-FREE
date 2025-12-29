import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in React-Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

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

interface MapViewProps {
  applications: PlanningApplication[];
  onMarkerClick?: (app: PlanningApplication) => void;
}

export const MapView: React.FC<MapViewProps> = ({ applications, onMarkerClick }) => {
  // Calculate center from applications or default to Portsmouth
  const center = useMemo(() => {
    if (applications.length === 0) {
      return { lat: 50.8198, lng: -1.0880 }; // Portsmouth default
    }
    
    const validApps = applications.filter(app => app.lat && app.lng);
    if (validApps.length === 0) {
      return { lat: 50.8198, lng: -1.0880 };
    }
    
    const avgLat = validApps.reduce((sum, app) => sum + app.lat, 0) / validApps.length;
    const avgLng = validApps.reduce((sum, app) => sum + app.lng, 0) / validApps.length;
    
    return { lat: avgLat, lng: avgLng };
  }, [applications]);

  return (
    <div className="h-[400px] w-full rounded-lg overflow-hidden shadow-md border border-gray-200">
      <MapContainer
        center={[center.lat, center.lng]}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {applications
          .filter(app => app.lat && app.lng)
          .map((app) => (
            <Marker
              key={app.id}
              position={[app.lat, app.lng]}
              eventHandlers={{
                click: () => onMarkerClick?.(app),
              }}
            >
              <Popup>
                <div className="p-2">
                  <h3 className="font-bold text-blue-600">{app.id}</h3>
                  <p className="text-sm text-gray-700 mt-1">{app.desc}</p>
                  <p className="text-xs text-gray-500 mt-2">{app.addr}</p>
                  <a
                    href={app.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-xs text-blue-500 hover:underline mt-2 block"
                  >
                    View Details →
                  </a>
                </div>
              </Popup>
            </Marker>
          ))}
      </MapContainer>
    </div>
  );
};
