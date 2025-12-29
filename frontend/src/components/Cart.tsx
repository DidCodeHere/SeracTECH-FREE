import React from 'react';
import { useCartStore } from '../store/cartStore';
import { ExportButton } from './ExportButton';

export const Cart: React.FC = () => {
  const { selectedLeads, removeLead, clearCart } = useCartStore();

  if (selectedLeads.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white border-t-2 border-blue-500 shadow-lg p-4 z-50">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <span className="bg-blue-600 text-white px-3 py-1 rounded-full font-bold">
              {selectedLeads.length}
            </span>
            <span className="font-medium text-gray-700">
              {selectedLeads.length === 1 ? 'Lead' : 'Leads'} Selected
            </span>
          </div>
          
          <div className="flex items-center gap-3">
            <ExportButton data={selectedLeads} />
            <button
              onClick={clearCart}
              className="px-3 py-1.5 text-sm text-gray-600 hover:text-red-600 transition-colors"
            >
              Clear All
            </button>
          </div>
        </div>
        
        {/* Mini preview of selected items */}
        <div className="mt-3 flex flex-wrap gap-2">
          {selectedLeads.slice(0, 5).map((lead) => (
            <span
              key={lead.id}
              className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full"
            >
              {lead.id}
              <button
                onClick={() => removeLead(lead.id)}
                className="hover:text-red-600 ml-1"
              >
                ×
              </button>
            </span>
          ))}
          {selectedLeads.length > 5 && (
            <span className="text-xs text-gray-500 px-2 py-1">
              +{selectedLeads.length - 5} more
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
