import { create } from 'zustand';

export type StudyCase = 'traffic' | 'weather' | 'energy';

export interface PinpointLocation {
  id: string;
  name: string;
  coordinates: [number, number]; // [lng, lat]
  type: StudyCase;
}

export interface StatCard {
  title: string;
  value: string;
  change: string;
  icon: string;
}

export interface AnalysisSuggestion {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
}

interface DashboardState {
  activeStudyCase: StudyCase | null;
  pinpoints: PinpointLocation[];
  stats: Record<StudyCase, StatCard[]>;
  suggestions: Record<StudyCase, AnalysisSuggestion[]>;
  setActiveStudyCase: (studyCase: StudyCase | null) => void;
}

const trafficStats: StatCard[] = [
  {
    title: 'Average Speed',
    value: '28 mph',
    change: '-12% from last week',
    icon: 'gauge',
  },
  {
    title: 'Congestion Index',
    value: '67/100',
    change: '+8% from last week',
    icon: 'car',
  },
  {
    title: 'Active Vehicles',
    value: '12,847',
    change: '+203 since last hour',
    icon: 'truck',
  },
  {
    title: 'Incidents Today',
    value: '23',
    change: '+5 from yesterday',
    icon: 'alert-triangle',
  },
];

const weatherStats: StatCard[] = [
  {
    title: 'Temperature',
    value: '72°F',
    change: '+3° from yesterday',
    icon: 'thermometer',
  },
  {
    title: 'Air Quality Index',
    value: '45 Good',
    change: '-12 from last week',
    icon: 'wind',
  },
  {
    title: 'Precipitation',
    value: '0.3 in',
    change: '+0.1 in from average',
    icon: 'cloud-rain',
  },
  {
    title: 'UV Index',
    value: '6 High',
    change: 'Peak at 2 PM',
    icon: 'sun',
  },
];

const energyStats: StatCard[] = [
  {
    title: 'Power Consumption',
    value: '847 MWh',
    change: '+18% from last month',
    icon: 'zap',
  },
  {
    title: 'Supply Cost',
    value: '$124,589',
    change: '+$12,450 from budget',
    icon: 'dollar-sign',
  },
  {
    title: 'Carbon Emissions',
    value: '342 tons CO₂',
    change: '-8% from last month',
    icon: 'leaf',
  },
  {
    title: 'Grid Efficiency',
    value: '94.2%',
    change: '+2.1% from average',
    icon: 'activity',
  },
];

const trafficSuggestions: AnalysisSuggestion[] = [
  {
    id: 't1',
    title: 'Optimize Traffic Signals',
    description:
      'Analysis shows 23% reduction in congestion possible by adjusting signal timing on Massachusetts Ave during peak hours (7-9 AM).',
    priority: 'high',
    category: 'Infrastructure',
  },
  {
    id: 't2',
    title: 'Alternative Route Promotion',
    description:
      'Memorial Drive shows 40% lower congestion. Consider dynamic signage to redirect traffic during rush hours.',
    priority: 'medium',
    category: 'Traffic Management',
  },
  {
    id: 't3',
    title: 'Public Transit Integration',
    description:
      'Increasing MBTA frequency on Red Line could reduce vehicle count by estimated 8-12% based on historical patterns.',
    priority: 'high',
    category: 'Public Transport',
  },
  {
    id: 't4',
    title: 'Incident Response',
    description:
      'Average incident clearance time is 47 minutes. Deploy additional rapid response units to reduce by 30%.',
    priority: 'medium',
    category: 'Emergency Services',
  },
];

const weatherSuggestions: AnalysisSuggestion[] = [
  {
    id: 'w1',
    title: 'Heat Warning Advisory',
    description:
      'Temperature expected to reach 89°F tomorrow. Issue public advisory for vulnerable populations and cooling center activation.',
    priority: 'high',
    category: 'Public Health',
  },
  {
    id: 'w2',
    title: 'Air Quality Monitoring',
    description:
      'AQI trending upward. Recommend limiting outdoor activities for sensitive groups. Monitor industrial emissions.',
    priority: 'medium',
    category: 'Environmental',
  },
  {
    id: 'w3',
    title: 'Storm Preparation',
    description:
      '60% precipitation probability this weekend. Pre-deploy storm drains maintenance and emergency response teams.',
    priority: 'high',
    category: 'Emergency Preparedness',
  },
  {
    id: 'w4',
    title: 'UV Protection Campaign',
    description:
      'High UV index persisting. Launch public awareness campaign about sun safety measures and sunscreen availability.',
    priority: 'low',
    category: 'Public Health',
  },
];

const energySuggestions: AnalysisSuggestion[] = [
  {
    id: 'e1',
    title: 'Peak Demand Reduction',
    description:
      'Energy consumption spikes 34% between 6-8 PM. Implement demand response program offering incentives for off-peak usage.',
    priority: 'high',
    category: 'Energy Management',
  },
  {
    id: 'e2',
    title: 'Solar Integration Opportunity',
    description:
      'Municipal buildings show 45% daytime consumption. Installing 2.5 MW solar could offset $180K annually.',
    priority: 'high',
    category: 'Renewable Energy',
  },
  {
    id: 'e3',
    title: 'Building Efficiency Audit',
    description:
      '12 public facilities exceed benchmark efficiency by 28%. Priority audit and HVAC upgrades could save 420 MWh/year.',
    priority: 'medium',
    category: 'Infrastructure',
  },
  {
    id: 'e4',
    title: 'Grid Modernization',
    description:
      'Current grid efficiency at 94.2%. Smart grid implementation could improve to 97%, reducing losses by $87K annually.',
    priority: 'medium',
    category: 'Infrastructure',
  },
  {
    id: 'e5',
    title: 'Carbon Reduction Initiative',
    description:
      'Emissions down 8% this month. Accelerate renewable adoption to meet 2030 carbon neutrality goal 2 years early.',
    priority: 'low',
    category: 'Sustainability',
  },
];

export const useDashboardStore = create<DashboardState>((set) => ({
  activeStudyCase: null,
  pinpoints: [
    {
      id: 'traffic-1',
      name: 'Harvard Square Traffic Analysis',
      coordinates: [-71.1189, 42.3736],
      type: 'traffic',
    },
    {
      id: 'weather-1',
      name: 'MIT Weather Station',
      coordinates: [-71.0942, 42.3601],
      type: 'weather',
    },
    {
      id: 'energy-1',
      name: 'Cambridge Power Grid Central',
      coordinates: [-71.0789, 42.3656],
      type: 'energy',
    },
  ],
  stats: {
    traffic: trafficStats,
    weather: weatherStats,
    energy: energyStats,
  },
  suggestions: {
    traffic: trafficSuggestions,
    weather: weatherSuggestions,
    energy: energySuggestions,
  },
  setActiveStudyCase: (studyCase) => set({ activeStudyCase: studyCase }),
}));