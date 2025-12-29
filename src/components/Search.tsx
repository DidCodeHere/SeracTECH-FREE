import React, { useState } from 'react';

interface SearchProps {
  onSearch: (postcode: string, radius: number) => void;
}

export const Search: React.FC<SearchProps> = ({ onSearch }) => {
  const [input, setInput] = useState('');
  const [radius, setRadius] = useState(5); // Default 5km radius

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim().length >= 2) {
      onSearch(input.trim(), radius);
    }
  };

  const handleShowAll = () => {
    setInput('ALL');
    onSearch('ALL', 9999); // Large radius to include everything
  };

  return (
    <div className="w-full max-w-lg mx-auto p-4">
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter Postcode (e.g. PO1 2AB)"
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Search
          </button>
        </div>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">Search Radius:</label>
          <input
            type="range"
            min="1"
            max="25"
            value={radius}
            onChange={(e) => setRadius(Number(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            disabled={input.toUpperCase() === 'ALL'}
          />
          <span className="text-sm font-medium text-blue-600 min-w-[50px]">
            {input.toUpperCase() === 'ALL' ? '∞' : `${radius} km`}
          </span>
        </div>
        <div className="flex justify-center">
          <button
            type="button"
            onClick={handleShowAll}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium text-sm"
          >
            🌍 Show All Applications
          </button>
        </div>
      </form>
    </div>
  );
};
