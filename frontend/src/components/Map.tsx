import { useEffect, useRef, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useDashboardStore } from '@/store/dashboardStore';
import { Loader2 } from 'lucide-react';

// Set Mapbox token
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN || '';

const BOSTON_CENTER: [number, number] = [-71.0589, 42.3601];

export function Map() {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const markersRef = useRef<mapboxgl.Marker[]>([]);
  const { mapData, loading, fetchMapData } = useDashboardStore();

  // Initialize map
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: BOSTON_CENTER,
        zoom: 12,
        pitch: 45,
        bearing: 0,
      });

      // Add navigation controls
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

      map.current.on('load', () => {
        console.log('Map loaded successfully');
        setMapLoaded(true);
        
        // Add 3D buildings layer
        if (map.current) {
          const layers = map.current.getStyle().layers;
          const labelLayerId = layers?.find(
            (layer) => layer.type === 'symbol' && layer.layout?.['text-field']
          )?.id;

          if (!map.current.getLayer('3d-buildings')) {
            map.current.addLayer(
              {
                id: '3d-buildings',
                source: 'composite',
                'source-layer': 'building',
                filter: ['==', 'extrude', 'true'],
                type: 'fill-extrusion',
                minzoom: 15,
                paint: {
                  'fill-extrusion-color': '#aaa',
                  'fill-extrusion-height': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    15,
                    0,
                    15.05,
                    ['get', 'height'],
                  ],
                  'fill-extrusion-base': [
                    'interpolate',
                    ['linear'],
                    ['zoom'],
                    15,
                    0,
                    15.05,
                    ['get', 'min_height'],
                  ],
                  'fill-extrusion-opacity': 0.6,
                },
              },
              labelLayerId
            );
          }
        }
      });

      map.current.on('error', (e) => {
        console.error('Map error:', e);
      });

      // Force resize after a short delay to ensure proper rendering
      setTimeout(() => {
        map.current?.resize();
      }, 100);

    } catch (error) {
      console.error('Error initializing map:', error);
    }

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Fetch map data
  useEffect(() => {
    if (!mapData) {
      console.log('Fetching map data...');
      fetchMapData();
    }
  }, [mapData, fetchMapData]);

  // Add markers when data is loaded
  useEffect(() => {
    if (!mapLoaded || !map.current || !mapData) {
      console.log('Not ready to add markers:', { mapLoaded, hasMap: !!map.current, hasData: !!mapData });
      return;
    }

    console.log('Adding markers:', {
      buildings: mapData.buildings?.length || 0,
      weather: mapData.weather_stations?.length || 0,
      traffic: mapData.intersections?.length || 0
    });

    // Clear existing markers
    markersRef.current.forEach(marker => marker.remove());
    markersRef.current = [];

    // Add building markers
    if (mapData.buildings && Array.isArray(mapData.buildings)) {
      mapData.buildings.forEach((building) => {
        try {
          const el = document.createElement('div');
          el.className = 'building-marker';
          el.style.width = '12px';
          el.style.height = '12px';
          el.style.borderRadius = '50%';
          el.style.backgroundColor = '#3b82f6';
          el.style.border = '2px solid white';
          el.style.cursor = 'pointer';
          el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

          const popup = new mapboxgl.Popup({ 
            offset: 25,
            closeButton: false,
            maxWidth: '300px'
          }).setHTML(
            `
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h3 style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #1a1a1a;">${building.name || 'Unknown Building'}</h3>
              <p style="font-size: 12px; color: #666; margin-bottom: 2px;">${building.category || 'Unknown Category'}</p>
              <p style="font-size: 12px; color: #333;">${building.square_feet ? building.square_feet.toLocaleString() : 'N/A'} sq ft</p>
            </div>
            `
          );

          const marker = new mapboxgl.Marker(el)
            .setLngLat([building.longitude || 0, building.latitude || 0])
            .setPopup(popup)
            .addTo(map.current!);

          markersRef.current.push(marker);
        } catch (error) {
          console.error('Error adding building marker:', error, building);
        }
      });
    }

    // Add weather station markers
    if (mapData.weather_stations && Array.isArray(mapData.weather_stations)) {
      mapData.weather_stations.forEach((station) => {
        try {
          const el = document.createElement('div');
          el.className = 'weather-marker';
          el.style.width = '10px';
          el.style.height = '10px';
          el.style.borderRadius = '50%';
          el.style.backgroundColor = '#10b981';
          el.style.border = '2px solid white';
          el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

          const popup = new mapboxgl.Popup({ 
            offset: 25,
            closeButton: false
          }).setHTML(
            `
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h3 style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #1a1a1a;">${station.name || 'Unknown Station'}</h3>
              <p style="font-size: 12px; color: #666;">Weather Station</p>
            </div>
            `
          );

          const marker = new mapboxgl.Marker(el)
            .setLngLat([station.longitude || 0, station.latitude || 0])
            .setPopup(popup)
            .addTo(map.current!);

          markersRef.current.push(marker);
        } catch (error) {
          console.error('Error adding weather marker:', error, station);
        }
      });
    }

    // Add traffic intersection markers
    if (mapData.intersections && Array.isArray(mapData.intersections)) {
      mapData.intersections.forEach((intersection) => {
        try {
          const el = document.createElement('div');
          el.className = 'traffic-marker';
          el.style.width = '8px';
          el.style.height = '8px';
          el.style.borderRadius = '50%';
          el.style.backgroundColor = '#f59e0b';
          el.style.border = '2px solid white';
          el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

          const popup = new mapboxgl.Popup({ 
            offset: 25,
            closeButton: false
          }).setHTML(
            `
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h3 style="font-weight: bold; font-size: 14px; margin-bottom: 4px; color: #1a1a1a;">${intersection.name || 'Unknown Intersection'}</h3>
              <p style="font-size: 12px; color: #666;">Traffic Intersection</p>
            </div>
            `
          );

          const marker = new mapboxgl.Marker(el)
            .setLngLat([intersection.longitude || 0, intersection.latitude || 0])
            .setPopup(popup)
            .addTo(map.current!);

          markersRef.current.push(marker);
        } catch (error) {
          console.error('Error adding traffic marker:', error, intersection);
        }
      });
    }

    // Fit bounds to show all buildings
    if (mapData.buildings && mapData.buildings.length > 0) {
      const bounds = new mapboxgl.LngLatBounds();
      mapData.buildings.forEach(building => {
        if (building.longitude && building.latitude) {
          bounds.extend([building.longitude, building.latitude]);
        }
      });
      map.current?.fitBounds(bounds, { padding: 50, maxZoom: 14, duration: 1000 });
    }
  }, [mapLoaded, mapData]);

  // Handle container resize
  useEffect(() => {
    const handleResize = () => {
      map.current?.resize();
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900">
        <Loader2 className="h-8 w-8 animate-spin text-white" />
      </div>
    );
  }

  if (!mapboxgl.accessToken) {
    return (
      <div className="w-full h-full flex items-center justify-center bg-gray-900 text-white">
        <div className="text-center">
          <p className="text-red-500">Mapbox token not found</p>
          <p className="text-sm text-gray-400 mt-2">Check your .env file</p>
        </div>
      </div>
    );
  }

  return (
    <div 
      ref={mapContainer} 
      className="w-full h-full rounded-lg overflow-hidden" 
      style={{ minHeight: '400px', position: 'relative' }} 
    />
  );
}