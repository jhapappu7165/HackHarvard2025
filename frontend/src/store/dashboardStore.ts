import { create } from 'zustand';
import { api } from '@/config/api';
import type { Building, Insight, DashboardStats, MapData } from '@/types';

export type StudyCase = 'traffic' | 'weather' | 'energy';

export interface PinpointLocation {
  id: string;
  name: string;
  coordinates: [number, number]; // [lng, lat]
  type: StudyCase;
  data?: any; // Additional data for the location
}

export interface StatCard {
  title: string;
  value: string;
  change: string;
  icon: string;
}

interface DashboardState {
  // UI State
  activeStudyCase: StudyCase | null;
  loading: boolean;
  error: string | null;
  
  // Data
  buildings: Building[];
  insights: Insight[];
  stats: DashboardStats | null;
  mapData: MapData | null;
  pinpoints: PinpointLocation[];
  
  // Actions
  setActiveStudyCase: (studyCase: StudyCase | null) => void;
  fetchBuildings: () => Promise<void>;
  fetchInsights: (params?: { priority?: string }) => Promise<void>;
  fetchStats: () => Promise<void>;
  fetchMapData: () => Promise<void>;
  generateAllData: () => Promise<void>;
  initializeDashboard: () => Promise<void>;
}
export const useDashboardStore = create<DashboardState>((set, get) => ({
  // Initial state
  activeStudyCase: 'energy',
  loading: false,
  error: null,
  buildings: [],
  insights: [],
  stats: null,
  mapData: null,
  pinpoints: [],

  // Actions
  setActiveStudyCase: (studyCase) => set({ activeStudyCase: studyCase }),

  fetchBuildings: async () => {
    try {
      set({ loading: true, error: null });
      const response = await api.energy.getBuildings();
      set({ buildings: response.buildings, loading: false });
    } catch (error) {
      console.error('Error fetching buildings:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  fetchInsights: async (params?: { priority?: string }) => {
    try {
      set({ loading: true, error: null });
      const response = await api.insights.getAll(params);
      set({ insights: response.insights, loading: false });
    } catch (error) {
      console.error('Error fetching insights:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  fetchStats: async () => {
    try {
      set({ loading: true, error: null });
      const response = await api.dashboard.getStats();
      set({ stats: response.stats, loading: false });
    } catch (error) {
      console.error('Error fetching stats:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  fetchMapData: async () => {
    try {
      set({ loading: true, error: null });
      const response = await api.dashboard.getMapData();
      set({ mapData: response.map_data, loading: false });
    } catch (error) {
      console.error('Error fetching map data:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  generateAllData: async () => {
    try {
      set({ loading: true, error: null });
      await api.dashboard.generateFast();
      
      // Refresh all data after generation
      await get().initializeDashboard();
      
      set({ loading: false });
    } catch (error) {
      console.error('Error generating data:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },

  initializeDashboard: async () => {
    try {
      set({ loading: true, error: null });
      
      // Fetch all data in parallel
      await Promise.all([
        get().fetchBuildings(),
        get().fetchInsights({ priority: 'high' }),
        get().fetchStats(),
        get().fetchMapData(),
      ]);
      
      set({ loading: false });
    } catch (error) {
      console.error('Error initializing dashboard:', error);
      set({ error: (error as Error).message, loading: false });
    }
  },
}));