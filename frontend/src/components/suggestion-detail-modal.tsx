import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  AlertCircle,
  TrendingUp,
  Lightbulb,
  Target,
  Bot,
  CheckCircle,
} from 'lucide-react';
import type { CitySuggestion } from '@/types';

interface SuggestionDetailModalProps {
  suggestion: CitySuggestion | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

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



const costColors = {
  'Low': 'bg-green-100 text-green-800',
  'Medium': 'bg-yellow-100 text-yellow-800',
  'High': 'bg-red-100 text-red-800',
  'TBD': 'bg-gray-100 text-gray-800',
};

export function SuggestionDetailModal({
  suggestion,
  open,
  onOpenChange,
}: SuggestionDetailModalProps) {
  if (!suggestion) return null;

  const Icon = priorityIcons[suggestion.priority];

  // Use actual AI-generated course of actions or fallback to concise mock data  
  const courseOfActions = suggestion.courseOfActions || [
    {
      id: 1,
      title: "Deploy Smart Traffic Signals",
      description: "Install AI-powered signals at key intersections",
      impact: "High",
      responsible: "Traffic Management",
      expectedOutcomes: [
        "Traffic delays: 25% reduction",
        "Fuel savings: $50K/month",
        "Implementation: 3-month rollout"
      ]
    },
    {
      id: 2,
      title: "Increase Peak Hour Transit",
      description: "Add express bus routes during rush hours",
      impact: "Medium-High",
      responsible: "Public Transit Authority",
      expectedOutcomes: [
        "Ridership: 20% increase",
        "Road congestion: 15% reduction",
        "Emissions: 500 tons CO2 saved/year"
      ]
    },
    {
      id: 3,
      title: "Implement Dynamic Pricing",
      description: "Time-based tolling on major corridors",
      impact: "High",
      responsible: "Revenue Department",
      expectedOutcomes: [
        "Peak traffic: 25% reduction",
        "Revenue: $2M annually",
        "Travel time: 18% improvement"
      ]
    }
  ];



  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3 flex-1">
              <div className={`p-2 rounded-full ${priorityColors[suggestion.priority]}`}>
                <Icon className="h-5 w-5 text-white" />
              </div>
              <div className="flex-1">
                <DialogTitle className="text-xl leading-tight mb-2">
                  {suggestion.title}
                </DialogTitle>
                <DialogDescription className="text-base">
                  {suggestion.why}
                </DialogDescription>
              </div>
            </div>
            {/* Small Priority and Cost badges in top right */}
            <div className="flex flex-col gap-1 ml-4">
              <Badge
                variant={suggestion.priority === 'high' ? 'destructive' : 'secondary'}
                className="text-xs px-2 py-1"
              >
                {suggestion.priority} priority
              </Badge>
              <Badge
                variant="outline"
                className={`text-xs px-2 py-1 ${costColors[suggestion.estimated_cost]}`}
              >
                {suggestion.estimated_cost} cost
              </Badge>
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6">
          {/* Main Focus: Course of Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-lg">
                <Target className="h-6 w-6 text-blue-600" />
                Possible Course of Actions
                <Badge variant="outline" className="ml-2">
                  <Bot className="h-3 w-3 mr-1" />
                  AI-Generated
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {courseOfActions.map((action, index) => (
                  <div key={action.id} className="border rounded-lg p-5 hover:bg-muted/20 transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold flex-shrink-0">
                        {index + 1}
                      </div>
                      <div className="flex-1 space-y-4">
                        <div>
                          <h4 className="font-semibold text-base mb-2">{action.title}</h4>
                          <p className="text-muted-foreground mb-3">{action.description}</p>
                          <div className="flex items-center gap-4 text-sm">
                            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                              Impact: {action.impact}
                            </Badge>
                            <span className="text-muted-foreground">
                              Led by: {action.responsible}
                            </span>
                          </div>
                        </div>

                        {/* Possible Impact Section */}
                        <div className="bg-slate-50 p-3 rounded-md border-l-3 border-l-blue-500">
                          <h5 className="font-medium text-sm text-slate-700 mb-2">Possible Impact:</h5>
                          <ul className="space-y-1">
                            {action.expectedOutcomes.map((outcome, outcomeIndex) => (
                              <li key={outcomeIndex} className="flex items-start gap-2">
                                <CheckCircle className="h-3 w-3 text-green-600 mt-1 flex-shrink-0" />
                                <span className="text-xs text-slate-600">{outcome}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

        </div>

        <div className="flex justify-end pt-6">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
