import React from 'react';

interface DateFilterProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
}

export const DateFilter: React.FC<DateFilterProps> = ({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
}) => {
  // Calculate quick date presets
  const today = new Date();
  const presets = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 90 days', days: 90 },
    { label: 'Last Year', days: 365 },
  ];

  const setPreset = (days: number) => {
    const end = today.toISOString().split('T')[0];
    const start = new Date(today.getTime() - days * 24 * 60 * 60 * 1000)
      .toISOString()
      .split('T')[0];
    onStartDateChange(start);
    onEndDateChange(end);
  };

  const clearDates = () => {
    onStartDateChange('');
    onEndDateChange('');
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-gray-700">📅 Date Filter</span>
        {(startDate || endDate) && (
          <button
            onClick={clearDates}
            className="text-xs text-red-500 hover:text-red-700"
          >
            Clear
          </button>
        )}
      </div>
      
      {/* Quick presets */}
      <div className="flex flex-wrap gap-1">
        {presets.map((preset) => (
          <button
            key={preset.days}
            onClick={() => setPreset(preset.days)}
            className="px-2 py-1 text-xs bg-white border border-gray-300 rounded hover:bg-blue-50 hover:border-blue-300 transition-colors"
          >
            {preset.label}
          </button>
        ))}
      </div>

      {/* Custom date inputs */}
      <div className="flex gap-2 items-center">
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">From</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
        <span className="text-gray-400 pt-4">→</span>
        <div className="flex-1">
          <label className="block text-xs text-gray-500 mb-1">To</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 focus:outline-none"
          />
        </div>
      </div>
    </div>
  );
};
