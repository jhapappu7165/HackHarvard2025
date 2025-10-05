// API Configuration for Flask Backend
import type {
  DashboardStats,
  MapData,
  Insight,
  CitySuggestion,
  Building,
  EnergyReading,
  WeatherStation,
  WeatherData,
  TrafficIntersection,
  TrafficData
} from '@/types';

// API Response Types
interface EnergyDashboardData {
  total_usage: number;
  total_cost: number;
  avg_usage_per_building: number;
  buildings_count: number;
  fuel_types: string[];
}

interface WeatherSummary {
  avg_temperature: number;
  total_precipitation: number;
  avg_humidity: number;
  avg_wind_speed: number;
  heating_degree_days: number;
  cooling_degree_days: number;
  stations_count: number;
}

interface TrafficSummary {
  total_vehicles: number;
  avg_speed: number;
  peak_congestion_time: string;
  intersections_count: number;
  congestion_levels: Record<string, number>;
}

interface InsightsSummary {
  total_insights: number;
  by_priority: Record<string, number>;
  by_type: Record<string, number>;
  potential_total_savings: number;
  avg_confidence_score: number;
}

interface DashboardOverview {
  energy_summary: EnergyDashboardData;
  weather_summary: WeatherSummary;
  traffic_summary: TrafficSummary;
  insights_summary: InsightsSummary;
}

interface GenerationResults {
  energy: { generated: number; message: string };
  weather: { generated: number; message: string };
  traffic: { generated: number; message: string };
  insights: { generated: number; message: string };
  total_time: number;
}

export const API_CONFIG = {
  // Updated to match backend port 5001
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5001',
  ENDPOINTS: {
    // Energy endpoints
    BUILDINGS: '/api/energy/buildings',
    BUILDING_DETAIL: (id: number) => `/api/energy/buildings/${id}`,
    BUILDING_READINGS: (id: number) => `/api/energy/buildings/${id}/readings`,
    ENERGY_DASHBOARD: '/api/energy/dashboard-data',
    GENERATE_ENERGY: '/api/energy/generate-data',

    // Weather endpoints
    WEATHER_STATIONS: '/api/weather/stations',
    WEATHER_DATA: '/api/weather/data',
    WEATHER_SUMMARY: '/api/weather/summary',
    GENERATE_WEATHER: '/api/weather/generate-data',

    // Traffic endpoints
    TRAFFIC_INTERSECTIONS: '/api/traffic/intersections',
    TRAFFIC_DATA: '/api/traffic/data',
    TRAFFIC_SUMMARY: '/api/traffic/summary',
    GENERATE_TRAFFIC: '/api/traffic/generate-data',

    // Insights endpoints
    INSIGHTS: '/api/insights',
    GENERATE_INSIGHTS: '/api/insights/generate-insights',
    BUILDING_INSIGHTS: (id: number) => `/api/insights/building/${id}`,
    INSIGHTS_SUMMARY: '/api/insights/summary',

    // NEW: AI-Powered Suggestions (Gemini) endpoint
    CITY_SUGGESTIONS: '/api/insights/suggestions',

    // Dashboard endpoints
    DASHBOARD_OVERVIEW: '/api/dashboard/overview',
    DASHBOARD_STATS: '/api/dashboard/stats',
    DASHBOARD_MAP_DATA: '/api/dashboard/map-data',
    GENERATE_ALL_DATA: '/api/dashboard/generate-all-data',
    GENERATE_FAST: '/api/dashboard/generate-fast',
    HEALTH: '/health',
  },
  TIMEOUT: 30000,
};

// Helper function for API calls
export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;

  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
}

// Typed API methods
export const api = {
  // Energy APIs
  energy: {
    getBuildings: () =>
      fetchAPI<{ success: boolean; buildings: Building[] }>(API_CONFIG.ENDPOINTS.BUILDINGS),

    getBuilding: (id: number) =>
      fetchAPI<{ success: boolean; building: Building }>(API_CONFIG.ENDPOINTS.BUILDING_DETAIL(id)),

    getBuildingReadings: (id: number, params?: { start_date?: string; end_date?: string; fuel_type?: string }) => {
      const queryString = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
      return fetchAPI<{ success: boolean; readings: EnergyReading[] }>(
        API_CONFIG.ENDPOINTS.BUILDING_READINGS(id) + queryString
      );
    },

    getDashboardData: () =>
      fetchAPI<{ success: boolean; data: EnergyDashboardData }>(API_CONFIG.ENDPOINTS.ENERGY_DASHBOARD),

    generateData: () =>
      fetchAPI<{ success: boolean; message: string }>(
        API_CONFIG.ENDPOINTS.GENERATE_ENERGY,
        { method: 'POST' }
      ),
  },

  // Weather APIs
  weather: {
    getStations: () =>
      fetchAPI<{ success: boolean; stations: WeatherStation[] }>(API_CONFIG.ENDPOINTS.WEATHER_STATIONS),

    getData: (params?: { station_id?: number; start_date?: string; end_date?: string }) => {
      const queryString = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
      return fetchAPI<{ success: boolean; data: WeatherData[] }>(
        API_CONFIG.ENDPOINTS.WEATHER_DATA + queryString
      );
    },

    getSummary: (params?: { start_date?: string; end_date?: string }) => {
      const queryString = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
      return fetchAPI<{ success: boolean; summary: WeatherSummary }>(
        API_CONFIG.ENDPOINTS.WEATHER_SUMMARY + queryString
      );
    },

    generateData: () =>
      fetchAPI<{ success: boolean; message: string }>(
        API_CONFIG.ENDPOINTS.GENERATE_WEATHER,
        { method: 'POST' }
      ),
  },

  // Traffic APIs
  traffic: {
    getIntersections: () =>
      fetchAPI<{ success: boolean; intersections: TrafficIntersection[] }>(API_CONFIG.ENDPOINTS.TRAFFIC_INTERSECTIONS),

    getData: (params?: { intersection_id?: number; start_time?: string; end_time?: string }) => {
      const queryString = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
      return fetchAPI<{ success: boolean; data: TrafficData[] }>(
        API_CONFIG.ENDPOINTS.TRAFFIC_DATA + queryString
      );
    },

    getSummary: () =>
      fetchAPI<{ success: boolean; summary: TrafficSummary }>(API_CONFIG.ENDPOINTS.TRAFFIC_SUMMARY),

    generateData: () =>
      fetchAPI<{ success: boolean; message: string }>(
        API_CONFIG.ENDPOINTS.GENERATE_TRAFFIC,
        { method: 'POST' }
      ),
  },

  // Insights APIs
  insights: {
    getAll: (params?: { type?: string; priority?: string; entity_type?: string }) => {
      const queryString = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
      return fetchAPI<{ success: boolean; insights: Insight[] }>(
        API_CONFIG.ENDPOINTS.INSIGHTS + queryString
      );
    },

    getBuildingInsights: (buildingId: number) =>
      fetchAPI<{ success: boolean; insights: Insight[] }>(
        API_CONFIG.ENDPOINTS.BUILDING_INSIGHTS(buildingId)
      ),

    generate: (buildingId?: number) =>
      fetchAPI<{ success: boolean; insights: Insight[]; message: string }>(
        API_CONFIG.ENDPOINTS.GENERATE_INSIGHTS,
        {
          method: 'POST',
          body: buildingId ? JSON.stringify({ building_id: buildingId }) : undefined,
        }
      ),

    getSummary: () =>
      fetchAPI<{ success: boolean; summary: InsightsSummary }>(API_CONFIG.ENDPOINTS.INSIGHTS_SUMMARY),

    // NEW: AI-Powered City Suggestions (Gemini)
    getCitySuggestions: () =>
      fetchAPI<{ success: boolean; suggestions: CitySuggestion[]; message: string; data_summary: Record<string, unknown> }>(
        API_CONFIG.ENDPOINTS.CITY_SUGGESTIONS,
        { method: 'POST' }
      ),
  },

  // Dashboard APIs
  dashboard: {
    getOverview: () =>
      fetchAPI<{ success: boolean; overview: DashboardOverview }>(API_CONFIG.ENDPOINTS.DASHBOARD_OVERVIEW),

    getStats: () =>
      fetchAPI<{ success: boolean; stats: DashboardStats }>(API_CONFIG.ENDPOINTS.DASHBOARD_STATS),

    getMapData: () =>
      fetchAPI<{ success: boolean; map_data: MapData }>(API_CONFIG.ENDPOINTS.DASHBOARD_MAP_DATA),

    generateAllData: () =>
      fetchAPI<{ success: boolean; results: GenerationResults }>(
        API_CONFIG.ENDPOINTS.GENERATE_ALL_DATA,
        { method: 'POST' }
      ),

    generateFast: () =>
      fetchAPI<{ success: boolean; message: string }>(
        API_CONFIG.ENDPOINTS.GENERATE_FAST,
        { method: 'POST' }
      ),
  },

  // Health check
  health: () =>
    fetchAPI<{ status: string; service: string }>(API_CONFIG.ENDPOINTS.HEALTH),
};