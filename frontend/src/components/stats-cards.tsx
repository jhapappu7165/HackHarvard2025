import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardStore } from '@/store/dashboardStore';
import {
  DollarSign,
  Activity,
  Zap,
  Leaf,
  Gauge,
  Car,
  Truck,
  AlertTriangle,
  Thermometer,
  Wind,
  CloudRain,
  Sun,
} from 'lucide-react';

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  'dollar-sign': DollarSign,
  activity: Activity,
  zap: Zap,
  leaf: Leaf,
  gauge: Gauge,
  car: Car,
  truck: Truck,
  'alert-triangle': AlertTriangle,
  thermometer: Thermometer,
  wind: Wind,
  'cloud-rain': CloudRain,
  sun: Sun,
};

export function StatsCards() {
  const { activeStudyCase, stats } = useDashboardStore();

  const defaultStats = [
    {
      title: 'Total Revenue',
      value: '$45,231.89',
      change: '+20.1% from last month',
      icon: 'dollar-sign',
    },
    {
      title: 'Subscriptions',
      value: '+2350',
      change: '+180.1% from last month',
      icon: 'activity',
    },
    {
      title: 'Sales',
      value: '+12,234',
      change: '+19% from last month',
      icon: 'zap',
    },
    {
      title: 'Active Now',
      value: '+573',
      change: '+201 since last hour',
      icon: 'activity',
    },
  ];

  const displayStats = activeStudyCase ? stats[activeStudyCase] : defaultStats;

  return (
    <>
      {displayStats.map((stat, index) => {
        const IconComponent = iconMap[stat.icon] || Activity;
        
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <IconComponent className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-muted-foreground text-xs">{stat.change}</p>
            </CardContent>
          </Card>
        );
      })}
    </>
  );
}