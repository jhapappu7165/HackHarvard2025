import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useDashboardStore } from '@/store/dashboardStore';
import { AlertCircle, TrendingUp, Lightbulb } from 'lucide-react';

export function AnalysisPanel() {
  const { activeStudyCase, suggestions } = useDashboardStore();

  if (!activeStudyCase) {
    return (
      <Card className="col-span-1 lg:col-span-3">
        <CardHeader>
          <CardTitle>Recent Sales</CardTitle>
          <CardDescription>You made 265 sales this month.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Select a study case pinpoint on the map to view AI-powered analysis and recommendations.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const currentSuggestions = suggestions[activeStudyCase];

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

  return (
    <Card className="col-span-1 lg:col-span-3">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span className="capitalize">{activeStudyCase}</span> Analysis
        </CardTitle>
        <CardDescription>
          AI-powered insights and recommendations based on current data
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-[520px] overflow-y-auto pr-2">
          {currentSuggestions.map((suggestion) => {
            const PriorityIcon = priorityIcons[suggestion.priority];
            
            return (
              <div
                key={suggestion.id}
                className="flex gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
              >
                <div className="flex-shrink-0 mt-1">
                  <div
                    className={`w-8 h-8 rounded-full ${priorityColors[suggestion.priority]} flex items-center justify-center`}
                  >
                    <PriorityIcon className="h-4 w-4 text-white" />
                  </div>
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-semibold text-sm leading-tight">
                      {suggestion.title}
                    </h4>
                    <Badge
                      variant="outline"
                      className="text-xs flex-shrink-0"
                    >
                      {suggestion.category}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {suggestion.description}
                  </p>
                  <div className="flex gap-2">
                    <Badge
                      variant="secondary"
                      className={`text-xs ${
                        suggestion.priority === 'high'
                          ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                          : suggestion.priority === 'medium'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-950 dark:text-yellow-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300'
                      }`}
                    >
                      {suggestion.priority.toUpperCase()} PRIORITY
                    </Badge>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}