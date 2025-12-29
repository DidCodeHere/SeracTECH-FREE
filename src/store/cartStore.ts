import { create } from 'zustand';

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

interface CartState {
  selectedLeads: PlanningApplication[];
  addLead: (lead: PlanningApplication) => void;
  removeLead: (id: string) => void;
  clearCart: () => void;
  isSelected: (id: string) => boolean;
  toggleLead: (lead: PlanningApplication) => void;
  selectAll: (leads: PlanningApplication[]) => void;
  deselectAll: () => void;
}

export const useCartStore = create<CartState>((set, get) => ({
  selectedLeads: [],
  
  addLead: (lead) => set((state) => ({
    selectedLeads: state.selectedLeads.some(l => l.id === lead.id)
      ? state.selectedLeads
      : [...state.selectedLeads, lead]
  })),
  
  removeLead: (id) => set((state) => ({
    selectedLeads: state.selectedLeads.filter(l => l.id !== id)
  })),
  
  clearCart: () => set({ selectedLeads: [] }),
  
  isSelected: (id) => get().selectedLeads.some(l => l.id === id),
  
  toggleLead: (lead) => {
    const isCurrentlySelected = get().isSelected(lead.id);
    if (isCurrentlySelected) {
      get().removeLead(lead.id);
    } else {
      get().addLead(lead);
    }
  },
  
  selectAll: (leads) => set((state) => {
    const existingIds = new Set(state.selectedLeads.map(l => l.id));
    const newLeads = leads.filter(l => !existingIds.has(l.id));
    return { selectedLeads: [...state.selectedLeads, ...newLeads] };
  }),
  
  deselectAll: () => set({ selectedLeads: [] })
}));
