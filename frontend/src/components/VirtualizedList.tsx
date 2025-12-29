import React, { useRef } from 'react';
import { useVirtualizer } from '@tanstack/react-virtual';
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

interface VirtualizedListProps {
  applications: PlanningApplication[];
  onItemClick?: (app: PlanningApplication) => void;
}

export const VirtualizedList: React.FC<VirtualizedListProps> = ({ applications, onItemClick }) => {
  const parentRef = useRef<HTMLDivElement>(null);
  const { toggleLead, isSelected } = useCartStore();

  const virtualizer = useVirtualizer({
    count: applications.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 120, // Estimated row height
    overscan: 5, // Render 5 extra items outside viewport
  });

  const items = virtualizer.getVirtualItems();

  return (
    <div
      ref={parentRef}
      className="h-[600px] overflow-auto"
      style={{ contain: 'strict' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {items.map((virtualItem) => {
          const app = applications[virtualItem.index];
          const selected = isSelected(app.id);
          
          return (
            <div
              key={virtualItem.key}
              style={{
                position: 'absolute',
                top: 0,
                left: 0,
                width: '100%',
                height: `${virtualItem.size}px`,
                transform: `translateY(${virtualItem.start}px)`,
              }}
              className="p-1"
            >
              <div
                className={`h-full bg-white p-4 rounded-lg shadow-sm border-2 hover:shadow-md transition-all cursor-pointer ${
                  selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                }`}
                onClick={() => onItemClick?.(app)}
              >
                <div className="flex justify-between items-start h-full">
                  <div className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => toggleLead(app)}
                      className="mt-1.5 h-4 w-4 text-blue-600 rounded"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <div>
                      <h3 className="font-semibold text-lg text-blue-600">
                        <a
                          href={app.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {app.id}
                        </a>
                      </h3>
                      <p className="text-gray-700 mt-1 line-clamp-2">{app.desc}</p>
                      <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                        <span>📍 {app.addr}</span>
                      </p>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span
                      className={`inline-block px-2 py-1 text-xs font-semibold rounded-full ${
                        app.status === 'Approved'
                          ? 'bg-green-100 text-green-800'
                          : app.status === 'Pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {app.status}
                    </span>
                    <p className="text-xs text-gray-400 mt-2">{app.date_received}</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
