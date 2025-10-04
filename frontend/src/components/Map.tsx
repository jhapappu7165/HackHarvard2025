import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useDashboardStore } from '@/store/dashboardStore';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<globalThis.Map<string, { marker: mapboxgl.Marker; element: HTMLDivElement }>>(new globalThis.Map());
  const popup = useRef<mapboxgl.Popup | null>(null);
  
  const { pinpoints, activeStudyCase } = useDashboardStore();

  // Initialize map only once - on mount
  useEffect(() => {
    // Prevent re-initialization if map already exists
    if (map.current) return;

    if (!mapboxgl.supported()) {
      console.error('Your browser does not support Mapbox GL');
      return;
    }

    if (!mapContainer.current) {
      console.error('Map container ref missing');
      return;
    }

    if (!mapboxgl.accessToken || !mapboxgl.accessToken.startsWith('pk.')) {
      console.error('Missing or invalid Mapbox public token');
      return;
    }

    console.log('Initializing map...');

    // Initialize map with 3D view settings
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-71.0589, 42.3601],
      zoom: 15.5, // Increased zoom to see buildings better
      pitch: 60,
      bearing: -17.6,
      antialias: true,
    });

    // Add navigation controls
    map.current.addControl(new mapboxgl.NavigationControl({
      visualizePitch: true
    }), 'top-right');

    map.current.on('load', () => {
      console.info('Map loaded successfully');

      // Add 3D terrain
      map.current!.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14,
      });

      map.current!.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });

      // Add sky layer
      map.current!.addLayer({
        id: 'sky',
        type: 'sky',
        paint: {
          'sky-type': 'atmosphere',
          'sky-atmosphere-sun': [0.0, 90.0],
          'sky-atmosphere-sun-intensity': 15,
        },
      });
    });

    // Wait for style to be fully loaded before adding 3D buildings
    map.current.on('style.load', () => {
      console.log('Style loaded, adding 3D buildings...');

      // Find the first symbol layer to insert buildings before labels
      const layers = map.current!.getStyle().layers;
      let labelLayerId: string | undefined;
      
      for (const layer of layers || []) {
        if (layer.type === 'symbol' && layer.layout && layer.layout['text-field']) {
          labelLayerId = layer.id;
          break;
        }
      }

      // Add 3D buildings layer
      if (!map.current!.getLayer('3d-buildings')) {
        map.current!.addLayer(
          {
            id: '3d-buildings',
            source: 'composite',
            'source-layer': 'building',
            filter: ['==', 'extrude', 'true'],
            type: 'fill-extrusion',
            minzoom: 14,
            paint: {
              'fill-extrusion-color': [
                'case',
                ['boolean', ['feature-state', 'hover'], false],
                '#fbbf24', // Yellow/amber when hovered
                [
                  'interpolate',
                  ['linear'],
                  ['get', 'height'],
                  0, '#6b7280',
                  50, '#4b5563',
                  100, '#374151',
                  200, '#1f2937'
                ]
              ],
              'fill-extrusion-height': [
                'interpolate',
                ['linear'],
                ['zoom'],
                14, 0,
                14.05, ['get', 'height']
              ],
              'fill-extrusion-base': [
                'interpolate',
                ['linear'],
                ['zoom'],
                14, 0,
                14.05, ['get', 'min_height']
              ],
              'fill-extrusion-opacity': 0.85,
            },
          },
          labelLayerId
        );
        console.log('3D buildings layer added');
      }

      // Add Massachusetts Avenue highlight
      if (!map.current!.getSource('mass-ave')) {
        map.current!.addSource('mass-ave', {
          type: 'geojson',
          data: {
            type: 'Feature',
            properties: {
              name: 'Massachusetts Avenue',
            },
            geometry: {
              type: 'LineString',
              coordinates: [
                [-71.1189, 42.3736],
                [-71.1150, 42.3710],
                [-71.1100, 42.3685],
                [-71.1050, 42.3660],
                [-71.0950, 42.3615],
                [-71.0900, 42.3590],
                [-71.0850, 42.3570],
                [-71.0789, 42.3550],
              ],
            },
          },
        });

        map.current!.addLayer({
          id: 'mass-ave-glow',
          type: 'line',
          source: 'mass-ave',
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': '#fbbf24',
            'line-width': 8,
            'line-opacity': 0.4,
            'line-blur': 4,
          },
        });

        map.current!.addLayer({
          id: 'mass-ave-highlight',
          type: 'line',
          source: 'mass-ave',
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
          paint: {
            'line-color': '#fbbf24',
            'line-width': 4,
            'line-opacity': 0.8,
          },
        });
      }

      // Convert pinpoints to GeoJSON
      const pinpointsGeoJSON: GeoJSON.FeatureCollection = {
        type: 'FeatureCollection',
        features: pinpoints.map((pinpoint) => ({
          type: 'Feature',
          properties: {
            id: pinpoint.id,
            name: pinpoint.name,
            type: pinpoint.type,
          },
          geometry: {
            type: 'Point',
            coordinates: pinpoint.coordinates,
          },
        })),
      };

      // Add pinpoints as a GeoJSON source
      if (!map.current!.getSource('pinpoints')) {
        map.current!.addSource('pinpoints', {
          type: 'geojson',
          data: pinpointsGeoJSON,
        });
      }

      // Add custom HTML markers for each pinpoint (only once)
      if (markersRef.current.size === 0) {
        pinpoints.forEach((pinpoint) => {
          const el = document.createElement('div');
          el.className = 'custom-marker';
          el.style.width = '40px';
          el.style.height = '40px';
          el.style.borderRadius = '50%';
          el.style.cursor = 'pointer';
          el.style.display = 'flex';
          el.style.alignItems = 'center';
          el.style.justifyContent = 'center';
          el.style.fontWeight = 'bold';
          el.style.fontSize = '18px';
          el.style.transition = 'all 0.3s ease';
          el.style.border = '3px solid white';
          el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';

          if (pinpoint.type === 'traffic') {
            el.style.backgroundColor = '#ef4444';
            el.innerHTML = '🚗';
          } else if (pinpoint.type === 'weather') {
            el.style.backgroundColor = '#3b82f6';
            el.innerHTML = '🌤️';
          } else if (pinpoint.type === 'energy') {
            el.style.backgroundColor = '#22c55e';
            el.innerHTML = '⚡';
          }

          const handleClick = (e: Event) => {
            e.stopPropagation();
            e.preventDefault();
            const { activeStudyCase: current, setActiveStudyCase: setState } = useDashboardStore.getState();
            setState(current === pinpoint.type ? null : pinpoint.type);
          };

          el.addEventListener('click', handleClick);

          const marker = new mapboxgl.Marker({ element: el, anchor: 'center' })
            .setLngLat(pinpoint.coordinates)
            .addTo(map.current!);

          const markerPopup = new mapboxgl.Popup({
            offset: 25,
            closeButton: false,
            closeOnClick: false,
          }).setHTML(
            `<h3 style="margin:0; font-weight:bold;">${pinpoint.name}</h3>
             <p style="margin:4px 0 0 0; text-transform:capitalize;">${pinpoint.type} Analysis</p>`
          );

          el.addEventListener('mouseenter', () => {
            markerPopup.setLngLat(pinpoint.coordinates).addTo(map.current!);
          });

          el.addEventListener('mouseleave', () => {
            markerPopup.remove();
          });

          markersRef.current.set(pinpoint.id, { marker, element: el });
        });
      }

      // Building interaction variables
      let hoveredBuildingId: string | number | null = null;

      // Create a popup for buildings
      popup.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      // Change cursor on hover
      map.current!.on('mousemove', '3d-buildings', (e) => {
        map.current!.getCanvas().style.cursor = 'pointer';

        if (e.features && e.features.length > 0) {
          if (hoveredBuildingId !== null) {
            map.current!.setFeatureState(
              { source: 'composite', sourceLayer: 'building', id: hoveredBuildingId },
              { hover: false }
            );
          }

          hoveredBuildingId = e.features[0].id as string | number;

          map.current!.setFeatureState(
            { source: 'composite', sourceLayer: 'building', id: hoveredBuildingId },
            { hover: true }
          );

          const properties = e.features[0].properties;
          const height = properties?.height || 'Unknown';
          const name = properties?.name || 'Building';
          
          const coordinates = e.lngLat;
          const description = `
            <div style="padding: 8px;">
              <h3 style="margin:0 0 8px 0; font-weight:bold; font-size:14px;">${name}</h3>
              <p style="margin:0; font-size:12px;"><strong>Height:</strong> ${height}m</p>
              <p style="margin:4px 0 0 0; font-size:11px; color:#888;">Click for details</p>
            </div>
          `;

          popup.current!.setLngLat(coordinates).setHTML(description).addTo(map.current!);
        }
      });

      map.current!.on('mouseleave', '3d-buildings', () => {
        map.current!.getCanvas().style.cursor = '';
        
        if (hoveredBuildingId !== null) {
          map.current!.setFeatureState(
            { source: 'composite', sourceLayer: 'building', id: hoveredBuildingId },
            { hover: false }
          );
        }
        hoveredBuildingId = null;
        popup.current!.remove();
      });

      map.current!.on('click', '3d-buildings', (e) => {
        if (e.features && e.features.length > 0) {
          const feature = e.features[0];
          const properties = feature.properties;
          
          const buildingInfo = {
            name: properties?.name || 'Unnamed Building',
            height: properties?.height || 'Unknown',
            type: properties?.type || 'Building',
            underground: properties?.underground || 'No',
            minHeight: properties?.min_height || 0,
          };

          console.log('Building clicked:', buildingInfo);

          const detailedPopup = new mapboxgl.Popup({ offset: 25 })
            .setLngLat(e.lngLat)
            .setHTML(
              `<div style="padding: 12px; min-width: 200px;">
                <h3 style="margin:0 0 12px 0; font-weight:bold; font-size:16px; border-bottom: 2px solid #fbbf24; padding-bottom: 8px;">
                  ${buildingInfo.name}
                </h3>
                <div style="font-size:13px; line-height: 1.8;">
                  <p style="margin:4px 0;"><strong>Type:</strong> ${buildingInfo.type}</p>
                  <p style="margin:4px 0;"><strong>Height:</strong> ${buildingInfo.height}m</p>
                  <p style="margin:4px 0;"><strong>Base Height:</strong> ${buildingInfo.minHeight}m</p>
                  <p style="margin:4px 0;"><strong>Underground:</strong> ${buildingInfo.underground}</p>
                </div>
                <button 
                  onclick="alert('Navigate to building details')" 
                  style="margin-top:12px; width:100%; padding:8px; background:#fbbf24; border:none; border-radius:4px; cursor:pointer; font-weight:bold;"
                >
                  View Details
                </button>
              </div>`
            )
            .addTo(map.current!);
        }
      });
    });

    map.current.on('error', (e) => {
      console.error('Mapbox map error event:', e.error);
    });

    return () => {
      console.log('Cleaning up map...');
      markersRef.current.forEach(({ marker }) => marker.remove());
      markersRef.current.clear();
      if (popup.current) {
        popup.current.remove();
      }
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Update marker styles when active study case changes
  useEffect(() => {
    if (!map.current) return;

    pinpoints.forEach((pinpoint) => {
      const markerData = markersRef.current.get(pinpoint.id);
      if (!markerData) return;

      const { element } = markerData;

      if (activeStudyCase === pinpoint.type) {
        element.style.transform = 'scale(1.3)';
        element.style.boxShadow = '0 6px 20px rgba(255,255,255,0.5)';
        element.style.zIndex = '1000';
      } else {
        element.style.transform = 'scale(1)';
        element.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
        element.style.zIndex = '1';
      }
    });
  }, [activeStudyCase, pinpoints]);

  return (
    <div
      ref={mapContainer}
      style={{
        width: '100%',
        height: 400,
        borderRadius: '8px',
      }}
      className="map-container"
    />
  );
};

export default Map;