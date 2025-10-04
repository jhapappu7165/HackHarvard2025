import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Zap, DollarSign, Leaf, Activity, Loader2 } from 'lucide-react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useEffect } from 'react';

export function StatsCards() {
  const { stats, loading, fetchStats } = useDashboardStore();

  useEffect(() => {
    if (!stats) {
      fetchStats();
    }
  }, [stats, fetchStats]);

  if (loading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="flex items-center justify-center h-32">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!stats) {
    return null;
  }

  const cards = [
    {
      title: 'Power Consumption',
      value: `${stats.energy.total_usage.toLocaleString()} ${stats.energy.unit}`,
      change: '+18% from last month',
      icon: Zap,
      iconColor: 'text-yellow-500',
    },
    {
      title: 'Energy Cost',
      value: `$${stats.energy.total_cost.toLocaleString()}`,
      change: `+$${(stats.energy.total_cost * 0.1).toLocaleString()} from budget`,
      icon: DollarSign,
      iconColor: 'text-green-500',
    },
    {
      title: 'Potential Savings',
      value: `$${stats.insights.potential_savings.toLocaleString()}`,
      change: `${stats.insights.high_priority} high priority insights`,
      icon: Leaf,
      iconColor: 'text-emerald-500',
    },
    {
      title: 'Active Insights',
      value: stats.insights.total.toString(),
      change: `Avg temp: ${stats.weather.avg_temperature.toFixed(1)}°F`,
      icon: Activity,
      iconColor: 'text-blue-500',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{card.title}</CardTitle>
            <card.icon className={`h-4 w-4 ${card.iconColor}`} />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <p className="text-xs text-muted-foreground">{card.change}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}