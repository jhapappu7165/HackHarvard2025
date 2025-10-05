import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, TrendingUp, Lightbulb, Loader2 } from 'lucide-react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useEffect } from 'react';

const priorityColors = {
  high: 'bg-red-500',
  medium: 'bg-yellow-500',
  low: 'bg-blue-500',
};

const priorityIcons = {
  high: AlertCircle,
  medium: TrendingUp,
  low: Lightbulb,
};

export function AnalysisPanel() {
  const { aiSuggestions, loading, fetchAISuggestions } = useDashboardStore();

  useEffect(() => {
    if (aiSuggestions.length === 0) {
      fetchAISuggestions();
    }
  }, [aiSuggestions, fetchAISuggestions]);

  if (loading) {
    return (
      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>AI-Powered City Optimization Suggestions</CardTitle>
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
        {aiSuggestions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No insights available yet.</p>
            <p className="text-sm">Generate data to see AI-powered recommendations.</p>
          </div>
        ) : (
          aiSuggestions
            .sort((a, b) => {
              const priorityOrder = { high: 0, medium: 1, low: 2 };
              return priorityOrder[a.priority] - priorityOrder[b.priority];
            })
            .slice(0, 5).map((suggestion) => {
            const Icon = priorityIcons[suggestion.priority] || Lightbulb;
            return (
              <div
                key={suggestion.title}
                className="flex items-start space-x-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className={`p-2 rounded-full ${priorityColors[suggestion.priority] || 'bg-blue-500'}`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold">{suggestion.title}</h4>
                    <Badge variant={suggestion.priority === 'high' ? 'destructive' : 'secondary'}>
                      {suggestion.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{suggestion.why}</p>
                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Badge variant="outline" className="text-xs">
                        {suggestion.category}
                      </Badge>
                    </span>
                    <span className="font-medium text-green-600">
                      Impact: {suggestion.estimated_impact}
                    </span>
                    <span>
                      Timeline: {suggestion.implementation_timeline}
                    </span>
                    <span>
                      Cost: {suggestion.estimated_cost}
                    </span>
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