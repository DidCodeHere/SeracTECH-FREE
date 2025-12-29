import React, { useState, useMemo } from 'react';
import { usePlanningData } from '../hooks/usePlanningData';
import { usePostcodeLookup } from '../hooks/usePostcodeLookup';
import { useRadiusFilter } from '../hooks/useRadiusFilter';
import { ExportButton } from './ExportButton';
import { useCartStore } from '../store/cartStore';
import { MapView } from './MapView';
import { VirtualizedList } from './VirtualizedList';
import { DateFilter } from './DateFilter';
import { ApplicationModal } from './ApplicationModal';

interface ResultsListProps {
  postcode: string;
  radiusKm: number;
}

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

export const ResultsList: React.FC<ResultsListProps> = ({ postcode, radiusKm }) => {
  const { data, isLoading, error } = usePlanningData(postcode);
  const { data: postcodeData } = usePostcodeLookup(postcode);
  const { toggleLead, selectAll, selectedLeads } = useCartStore();
  const [showMap, setShowMap] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [selectedApp, setSelectedApp] = useState<PlanningApplication | null>(null);

  // Check if it's a "show all" request
  const isShowAll = postcode.toUpperCase() === 'ALL';

  // Filter applications by radius from the searched postcode (skip for "show all")
  const radiusFilteredData = useRadiusFilter(
    data || [],
    isShowAll ? null : (postcodeData?.latitude || null),
    isShowAll ? null : (postcodeData?.longitude || null),
    isShowAll ? 99999 : radiusKm
  );
  
  // Apply status filter
  const filteredData = useMemo(() => {
    let result = radiusFilteredData;
    
    // Status filter
    if (statusFilter !== 'all') {
      result = result.filter(app => app.status.toLowerCase() === statusFilter.toLowerCase());
    }
    
    // Date filter
    if (startDate) {
      result = result.filter(app => app.date_received >= startDate);
    }
    if (endDate) {
      result = result.filter(app => app.date_received <= endDate);
    }
    
    return result;
  }, [radiusFilteredData, statusFilter, startDate, endDate]);
  
  // Count active filters
  const activeFilterCount = [
    statusFilter !== 'all',
    startDate || endDate,
  ].filter(Boolean).length;
  
  // Check if all visible items are selected
  const allSelected = filteredData.length > 0 && filteredData.every(app => 
    selectedLeads.some(l => l.id === app.id)
  );

  if (!postcode) return null;

  if (isLoading) {
    return (
      <div className="text-center p-8 text-gray-500">
        {isShowAll 
          ? 'Loading all planning applications...' 
          : `Loading planning applications for ${postcode}...`}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8 text-red-500">
        Error loading data. Please try again later.
      </div>
    );
  }

  if (!filteredData || filteredData.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        {isShowAll 
          ? 'No planning applications found in the database.' 
          : `No planning applications found within ${radiusKm}km of ${postcode}.`}
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
        <div>
          <h2 className="text-xl font-bold text-gray-800">
            Found {filteredData.length} Applications
          </h2>
          <p className="text-sm text-gray-500">
            {isShowAll 
              ? 'Showing all applications nationwide' 
              : `Within ${radiusKm}km of ${postcode}${postcodeData ? ` (${postcodeData.admin_district})` : ''}`}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              showFilters || activeFilterCount > 0
                ? 'bg-purple-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🔍 Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
          </button>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-2 py-1.5 text-sm border border-gray-300 rounded bg-white"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="refused">Refused</option>
          </select>
          <button
            onClick={() => selectAll(filteredData)}
            disabled={allSelected}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              allSelected
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 text-white hover:bg-green-700'
            }`}
          >
            Select All ({filteredData.length})
          </button>
          <button
            onClick={() => setShowMap(!showMap)}
            className={`px-3 py-1.5 text-sm rounded transition-colors ${
              showMap 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {showMap ? '📍 Hide Map' : '📍 Show Map'}
          </button>
          <ExportButton data={filteredData} />
        </div>
      </div>
      
      {/* Date Filter Panel */}
      {showFilters && (
        <div className="mb-4">
          <DateFilter
            startDate={startDate}
            endDate={endDate}
            onStartDateChange={setStartDate}
            onEndDateChange={setEndDate}
          />
        </div>
      )}
      
      {showMap && (
        <div className="mb-6">
          <MapView applications={filteredData} onMarkerClick={toggleLead} />
        </div>
      )}
      
      {/* Use virtualized list for performance with large datasets */}
      <VirtualizedList applications={filteredData} onItemClick={setSelectedApp} />
      
      {/* Application Detail Modal */}
      <ApplicationModal application={selectedApp} onClose={() => setSelectedApp(null)} />
    </div>
  );
};
