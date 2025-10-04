import { useEffect, useState } from 'react';
import Map from '@/components/Map';
import { StatsCards } from '@/components/stats-cards';
import { AnalysisPanel } from '@/components/analysis-panel';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useDashboardStore } from '@/store/dashboardStore';
import { BuildingDetailModal } from '@/components/building-detail-modal';
import { Database, Loader2, RefreshCw } from 'lucide-react';
import type { Building } from '@/types';
import { Badge } from '@/components/ui/badge';

export function Dashboard() {
  const {
    buildings,
    loading,
    error,
    initializeDashboard,
    generateAllData,
  } = useDashboardStore();

  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    initializeDashboard();
  }, [initializeDashboard]);

  const handleGenerateData = async () => {
    setIsGenerating(true);
    try {
      await generateAllData();
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBuildingClick = (building: Building) => {
    setSelectedBuilding(building);
    setIsModalOpen(true);
  };

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Dashboard</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button
              onClick={() => initializeDashboard()}
              className="mt-4"
              variant="outline"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Database className="h-6 w-6" />
            <h1 className="text-xl font-bold">Boston Energy Insights</h1>
          </div>
          <div className="flex items-center gap-2">
            {buildings.length === 0 && !loading && (
              <Button
                onClick={handleGenerateData}
                disabled={isGenerating}
                variant="default"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Generate Sample Data
                  </>
                )}
              </Button>
            )}
            {buildings.length > 0 && (
              <Button
                onClick={() => initializeDashboard()}
                disabled={loading}
                variant="outline"
                size="sm"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Tabs defaultValue="overview" className="h-full flex flex-col">
          <div className="border-b">
            <div className="container">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="buildings">Buildings</TabsTrigger>
                <TabsTrigger value="map">Map View</TabsTrigger>
              </TabsList>
            </div>
          </div>

          <div className="flex-1 overflow-auto">
            <div className="container py-6 space-y-6">
              <TabsContent value="overview" className="m-0 space-y-6">
                <StatsCards />
                <div className="grid gap-6 md:grid-cols-7">
                  <Card className="col-span-4 h-[400px]">
                    <CardHeader>
                      <CardTitle>Energy Map</CardTitle>
                    </CardHeader>
                    <CardContent className="h-[calc(100%-80px)]">
                      <Map />
                    </CardContent>
                  </Card>
                  <div className="col-span-3">
                    <AnalysisPanel />
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="buildings" className="m-0">
                <Card>
                  <CardHeader>
                    <CardTitle>All Buildings</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {loading ? (
                      <div className="flex items-center justify-center h-64">
                        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                      </div>
                    ) : buildings.length === 0 ? (
                      <div className="text-center py-12">
                        <Database className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <h3 className="text-lg font-semibold mb-2">No Buildings Yet</h3>
                        <p className="text-muted-foreground mb-4">
                          Generate sample data to see buildings and insights
                        </p>
                        <Button onClick={handleGenerateData} disabled={isGenerating}>
                          {isGenerating ? (
                            <>
                              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                              Generating...
                            </>
                          ) : (
                            <>
                              <Database className="h-4 w-4 mr-2" />
                              Generate Sample Data
                            </>
                          )}
                        </Button>
                      </div>
                    ) : (
                      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                        {buildings.map((building) => (
                          <Card
                            key={building.id}
                            className="cursor-pointer hover:shadow-lg transition-shadow"
                            onClick={() => handleBuildingClick(building)}
                          >
                            <CardHeader>
                              <div className="flex items-start justify-between">
                                <CardTitle className="text-base">{building.name}</CardTitle>
                                <Badge>{building.category}</Badge>
                              </div>
                            </CardHeader>
                            <CardContent className="space-y-2">
                              <p className="text-sm text-muted-foreground">{building.address}</p>
                              <div className="flex justify-between text-sm">
                                <span className="text-muted-foreground">Size:</span>
                                <span className="font-medium">
                                  {building.square_feet.toLocaleString()} sq ft
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span className="text-muted-foreground">Built:</span>
                                <span className="font-medium">{building.year_built}</span>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="map" className="m-0">
                <Card className="h-[calc(100vh-200px)]">
                  <CardContent className="h-full p-0">
                    <Map />
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </div>
        </Tabs>
      </div>

      {/* Building Detail Modal */}
      <BuildingDetailModal
        building={selectedBuilding}
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
      />
    </div>
  );
}