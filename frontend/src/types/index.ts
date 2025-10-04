// Building types
export interface Building {
  id: number;
  name: string;
  address: string;
  city: string;
  latitude: number;
  longitude: number;
  square_feet: number;
  category: string;
  year_built: number;
  created_at?: string;
}

export interface EnergyReading {
  id: number;
  building_id: number;
  reading_date: string;
  fuel_type: string;
  usage: number;
  cost: number;
  created_at?: string;
}

// Weather types
export interface WeatherStation {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  created_at?: string;
}

export interface WeatherData {
  id: number;
  station_id: number;
  reading_date: string;
  temp_avg: number;
  temp_min: number;
  temp_max: number;
  heating_degree_days: number;
  cooling_degree_days: number;
  precipitation: number;
  wind_speed: number;
  humidity: number;
  created_at?: string;
}

// Traffic types
export interface TrafficIntersection {
  id: number;
  name: string;
  latitude: number;
  longitude: number;
  streets: string[];
  created_at?: string;
}

export interface TrafficData {
  id: number;
  intersection_id: number;
  reading_timestamp: string;
  time_period: string;
  total_vehicle_count: number;
  average_speed: number;
  congestion_level: string;
  created_at?: string;
}

// Insight types
export interface Insight {
  id: number;
  insight_type: 'energy' | 'weather' | 'traffic' | 'cross_domain';
  entity_id: number | null;
  entity_type: 'building' | 'intersection' | 'station' | 'city' | 'system';
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  category: string | null;
  potential_savings: number | null;
  confidence_score: number | null;
  data_sources: string[] | null;
  metadata: Record<string, any> | null;
  created_at?: string;
}

// Dashboard types
export interface DashboardStats {
  energy: {
    total_usage: number;
    total_cost: number;
    unit: string;
  };
  weather: {
    avg_temperature: number;
    heating_degree_days: number;
    cooling_degree_days: number;
  };
  traffic: {
    total_vehicles: number;
    avg_speed: number;
  };
  insights: {
    total: number;
    high_priority: number;
    potential_savings: number;
  };
}

export interface MapData {
  buildings: Building[];
  weather_stations: WeatherStation[];
  intersections: TrafficIntersection[];
}

export interface DashboardOverview {
  counts: {
    buildings: number;
    weather_stations: number;
    traffic_intersections: number;
    total_insights: number;
  };
  energy_summary: {
    total_usage: number;
    total_cost: number;
    avg_usage_per_building: number;
  };
  high_priority_insights: Insight[];
}