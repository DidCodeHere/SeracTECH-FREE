import React from 'react';
import { useCartStore } from '../store/cartStore';

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

interface ApplicationModalProps {
  application: PlanningApplication | null;
  onClose: () => void;
}

export const ApplicationModal: React.FC<ApplicationModalProps> = ({
  application,
  onClose,
}) => {
  const { toggleLead, selectedLeads } = useCartStore();

  if (!application) return null;

  const isSelected = selectedLeads.some((l) => l.id === application.id);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'refused':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-start">
          <div>
            <span
              className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                application.status
              )}`}
            >
              {application.status}
            </span>
            <h2 className="text-xl font-bold text-gray-900 mt-2">
              {application.id}
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-4 space-y-4">
          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">
              Description
            </h3>
            <p className="text-gray-900">{application.desc}</p>
          </div>

          {/* Address */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Address</h3>
            <p className="text-gray-900">{application.addr}</p>
            <p className="text-sm text-blue-600">{application.postcode}</p>
          </div>

          {/* Date */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">
              Date Received
            </h3>
            <p className="text-gray-900">
              {new Date(application.date_received).toLocaleDateString('en-GB', {
                day: 'numeric',
                month: 'long',
                year: 'numeric',
              })}
            </p>
          </div>

          {/* Coordinates */}
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-1">Location</h3>
            <p className="text-gray-600 text-sm font-mono">
              {application.lat.toFixed(6)}, {application.lng.toFixed(6)}
            </p>
          </div>

          {/* Mini Map Preview */}
          <div className="bg-gray-100 rounded-lg h-32 flex items-center justify-center">
            <a
              href={`https://www.google.com/maps?q=${application.lat},${application.lng}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
            >
              <span>📍</span>
              <span>View on Google Maps</span>
            </a>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex gap-3">
          <button
            onClick={() => toggleLead(application)}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
              isSelected
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {isSelected ? '✓ Added to Cart' : 'Add to Cart'}
          </button>
          <a
            href={application.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 py-2 px-4 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors text-center"
          >
            View on Council Site →
          </a>
        </div>
      </div>
    </div>
  );
};
