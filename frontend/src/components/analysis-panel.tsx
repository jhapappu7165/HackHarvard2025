import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, TrendingUp, Lightbulb, Loader2, ChevronRight } from 'lucide-react';
import { useDashboardStore } from '@/store/dashboardStore';
import { useEffect, useState } from 'react';
import { SuggestionDetailModal } from './suggestion-detail-modal';
import type { CitySuggestion } from '@/types';

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
  const [selectedSuggestion, setSelectedSuggestion] = useState<CitySuggestion | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    if (insights.length === 0) {
      fetchInsights();
    }
  }, [insights, fetchInsights]);

  const handleSuggestionClick = (suggestion: CitySuggestion) => {
    setSelectedSuggestion(suggestion);
    setModalOpen(true);
  };

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
        {insights.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Lightbulb className="h-12 w-12 mx-auto mb-2 opacity-50" />
            <p>No insights available yet.</p>
            <p className="text-sm">Generate data to see AI-powered recommendations.</p>
          </div>
        ) : (
          insights
            .sort((a, b) => {
              const priorityOrder = { high: 0, medium: 1, low: 2, critical: -1 };
              return (priorityOrder[a.priority] ?? 3) - (priorityOrder[b.priority] ?? 3);
            })
            .slice(0, 5).map((suggestion) => {
              const Icon = priorityIcons[suggestion.priority] || Lightbulb;
              return (
                <div
                  key={suggestion.title} // Using title as key since CitySuggestion doesn't have id
                  className="flex items-start space-x-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors cursor-pointer group"
                  onClick={() => handleSuggestionClick(suggestion)}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      handleSuggestionClick(suggestion);
                    }
                  }}
                >
                  <div className={`p-2 rounded-full ${priorityColors[suggestion.priority] || 'bg-gray-500'}`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-semibold group-hover:text-primary transition-colors">
                        {suggestion.title}
                      </h4>
                      <div className="flex items-center gap-2">
                        <Badge variant={suggestion.priority === 'high' ? 'destructive' : 'secondary'}>
                          {suggestion.priority}
                        </Badge>
                        <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground">{suggestion.why}</p>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      {suggestion.category && (
                        <span className="flex items-center gap-1">
                          <Badge variant="outline" className="text-xs">
                            {suggestion.category}
                          </Badge>
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        Timeline: {suggestion.implementation_timeline}
                      </span>
                      <span className="flex items-center gap-1">
                        Cost: {suggestion.estimated_cost}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
        )}

        <SuggestionDetailModal
          suggestion={selectedSuggestion}
          open={modalOpen}
          onOpenChange={setModalOpen}
        />
      </CardContent>
    </Card>
  );
}