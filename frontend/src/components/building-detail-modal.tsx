import { useEffect, useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2, TrendingUp, DollarSign, Zap, AlertCircle } from 'lucide-react';
import { api } from '@/config/api';
import type { Building, EnergyReading, Insight } from '@/types';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

interface BuildingDetailModalProps {
  building: Building | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function BuildingDetailModal({
  building,
  open,
  onOpenChange,
}: BuildingDetailModalProps) {
  const [readings, setReadings] = useState<EnergyReading[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (building && open) {
      fetchBuildingData();
    }
  }, [building, open]);

  const fetchBuildingData = async () => {
    if (!building) return;

    setLoading(true);
    try {
      const [readingsResponse, insightsResponse] = await Promise.all([
        api.energy.getBuildingReadings(building.id),
        api.insights.getBuildingInsights(building.id),
      ]);

      setReadings(readingsResponse.readings);
      setInsights(insightsResponse.insights);
    } catch (error) {
      console.error('Error fetching building data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!building) return null;

  // Process readings for charts
  const monthlyData = readings.reduce((acc: any[], reading) => {
    const month = reading.reading_date.substring(0, 7); // YYYY-MM
    const existing = acc.find((item) => item.month === month);

    if (existing) {
      existing.usage += reading.usage;
      existing.cost += reading.cost;
    } else {
      acc.push({
        month,
        usage: reading.usage,
        cost: reading.cost,
      });
    }

    return acc;
  }, []);

  monthlyData.sort((a, b) => a.month.localeCompare(b.month));

  // Fuel type breakdown
  const fuelTypeData = readings.reduce((acc: any[], reading) => {
    const existing = acc.find((item) => item.fuel_type === reading.fuel_type);

    if (existing) {
      existing.usage += reading.usage;
      existing.cost += reading.cost;
    } else {
      acc.push({
        fuel_type: reading.fuel_type,
        usage: reading.usage,
        cost: reading.cost,
      });
    }

    return acc;
  }, []);

  const totalUsage = readings.reduce((sum, r) => sum + r.usage, 0);
  const totalCost = readings.reduce((sum, r) => sum + r.cost, 0);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-2xl">{building.name}</DialogTitle>
          <DialogDescription>
            {building.address}, {building.city} • {building.square_feet.toLocaleString()} sq ft
          </DialogDescription>
        </DialogHeader>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="energy">Energy Data</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
                    <Zap className="h-4 w-4 text-yellow-500" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {totalUsage.toLocaleString()} kWh
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Past {readings.length} readings
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                    <DollarSign className="h-4 w-4 text-green-500" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      ${totalCost.toLocaleString()}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      ${(totalCost / monthlyData.length).toFixed(2)} per month avg
                    </p>
                  </CardContent>
                </Card>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Building Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Category:</span>
                    <Badge>{building.category}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Year Built:</span>
                    <span className="font-medium">{building.year_built}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Square Feet:</span>
                    <span className="font-medium">
                      {building.square_feet.toLocaleString()} sq ft
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Location:</span>
                    <span className="font-medium">
                      {building.latitude.toFixed(4)}, {building.longitude.toFixed(4)}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="energy" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Monthly Energy Usage Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={monthlyData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="month" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <Tooltip />
                      <Legend />
                      <Line
                        yAxisId="left"
                        type="monotone"
                        dataKey="usage"
                        stroke="#3b82f6"
                        name="Usage (kWh)"
                      />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="cost"
                        stroke="#10b981"
                        name="Cost ($)"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Energy by Fuel Type</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={fuelTypeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="fuel_type" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="usage" fill="#3b82f6" name="Usage (kWh)" />
                      <Bar dataKey="cost" fill="#10b981" name="Cost ($)" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="insights" className="space-y-4">
              {insights.length === 0 ? (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center h-64">
                    <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No insights available for this building</p>
                  </CardContent>
                </Card>
              ) : (
                insights.map((insight) => (
                  <Card key={insight.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-lg">{insight.title}</CardTitle>
                          <div className="flex items-center gap-2">
                            <Badge
                              variant={
                                insight.priority === 'high' || insight.priority === 'critical'
                                  ? 'destructive'
                                  : 'secondary'
                              }
                            >
                              {insight.priority}
                            </Badge>
                            {insight.category && (
                              <Badge variant="outline">{insight.category}</Badge>
                            )}
                          </div>
                        </div>
                        {insight.confidence_score && (
                          <div className="text-right">
                            <div className="text-sm font-medium">
                              {insight.confidence_score.toFixed(0)}%
                            </div>
                            <div className="text-xs text-muted-foreground">Confidence</div>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-muted-foreground">{insight.description}</p>
                      {insight.potential_savings && (
                        <div className="flex items-center gap-2 text-sm">
                          <TrendingUp className="h-4 w-4 text-green-600" />
                          <span className="font-medium text-green-600">
                            Potential Savings: ${insight.potential_savings.toLocaleString()}
                          </span>
                        </div>
                      )}
                      {insight.data_sources && insight.data_sources.length > 0 && (
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="text-xs text-muted-foreground">Data sources:</span>
                          {insight.data_sources.map((source) => (
                            <Badge key={source} variant="outline" className="text-xs">
                              {source}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  );
}