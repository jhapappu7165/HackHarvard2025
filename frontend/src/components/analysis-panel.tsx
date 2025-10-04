import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, TrendingUp, Lightbulb, Loader2 } from 'lucide-react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useEffect } from 'react';
import type { Insight } from '@/types';

const priorityColors = {
  critical: 'bg-red-500',
  high: 'bg-orange-500',
  medium: 'bg-yellow-500',
  low: 'bg-blue-500',
};

const priorityIcons = {
  critical: AlertCircle,
  high: TrendingUp,
  medium: Lightbulb,
  low: Lightbulb,
};

export function AnalysisPanel() {
  const { insights, loading, fetchInsights } = useDashboardStore();

  useEffect(() => {
    if (insights.length === 0) {
      fetchInsights({ priority: 'high' });
    }
  }, [insights, fetchInsights]);

  if (loading) {
    return (
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>AI-Powered Insights</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </CardContent>
        </Card>
      );
  }

  return (
    <Card className="col-span-4">
      <CardHeader>
        <CardTitle>AI-Powered City Optimization Suggestions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {insights.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No insights available yet.</p>
            <p className="text-sm">Generate data to see AI-powered recommendations.</p>
          </div>
        ) : (
          insights
            .sort((a: Insight, b: Insight) => {
              const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
              return priorityOrder[a.priority] - priorityOrder[b.priority];
            })
            .slice(0, 5).map((insight: Insight) => {
            const Icon = priorityIcons[insight.priority];
            return (
              <div
                key={insight.id}
                className="flex items-start space-x-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className={`p-2 rounded-full ${priorityColors[insight.priority]}`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold">{insight.title}</h4>
                    <Badge variant={insight.priority === 'high' || insight.priority === 'critical' ? 'destructive' : 'secondary'}>
                      {insight.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{insight.description}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {insight.category && (
                      <span className="flex items-center gap-1">
                        <Badge variant="outline" className="text-xs">
                          {insight.category}
                        </Badge>
                      </span>
                    )}
                    {insight.potential_savings && (
                      <span className="font-medium text-green-600">
                        Potential Savings: ${insight.potential_savings.toLocaleString()}
                      </span>
                    )}
                    {insight.confidence_score && (
                      <span>
                        Confidence: {insight.confidence_score.toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
