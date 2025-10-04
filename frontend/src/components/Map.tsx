import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useDashboardStore } from '@/store/dashboardStore';
import MassAveSB from '../assets/MassAveSB.json';
import MassAveNB from '../assets/MassAveNB.json';
import { FeatureCollection, LineString, GeoJsonProperties, Point } from 'geojson';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;

interface TrafficDataPoint {
  id: number;
  intersection_id: number;
  reading_timestamp: string;
  northbound_left: number;
  northbound_thru: number;
  northbound_right: number;
  southbound_left: number;
  southbound_thru: number;
  southbound_right: number;
  total_vehicle_count: number;
  average_speed: number;
  congestion_level: string;
  time_period: string;
}

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markersRef = useRef<globalThis.Map<string, { marker: mapboxgl.Marker; element: HTMLDivElement }>>(new globalThis.Map());
  const hoverPopup = useRef<mapboxgl.Popup | null>(null);
  const clickPopup = useRef<mapboxgl.Popup | null>(null);
  const roadPopupRef = useRef<mapboxgl.Popup | null>(null);
  
  // Refs to hold current traffic values
  const trafficVolumeNBRef = useRef(35);
  const trafficVolumeSBRef = useRef(68);
  const currentVehiclesNBRef = useRef(0);
  const currentVehiclesSBRef = useRef(0);

  // Traffic volume state (0-100) - will be calculated from actual data
  const [trafficVolumeNB, setTrafficVolumeNB] = useState(35);
  const [trafficVolumeSB, setTrafficVolumeSB] = useState(68);
  const [currentVehiclesNB, setCurrentVehiclesNB] = useState(0);
  const [currentVehiclesSB, setCurrentVehiclesSB] = useState(0);
  
  // State for tracking current data index
  const [trafficData, setTrafficData] = useState<TrafficDataPoint[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const { pinpoints, activeStudyCase } = useDashboardStore();

  // Fetch traffic data on mount
  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
        // Fetch data for intersection 31 (or make this configurable)
        const response = await fetch('http://localhost:5001/api/traffic/directional?intersection_id=31&limit=24');
        const result = await response.json();
        
        if (result.success && result.data) {
          setTrafficData(result.data);
          console.log(`Loaded ${result.data.length} traffic data points`);
        }
      } catch (error) {
        console.error('Error fetching traffic data:', error);
      }
    };

    fetchTrafficData();
  }, []);

  // Update traffic volumes every 3 seconds and cycle through data
  useEffect(() => {
    if (trafficData.length === 0) return;

    const interval = setInterval(() => {
      const currentData = trafficData[currentIndex];
      
      // Calculate northbound total
      const nbTotal = currentData.northbound_left + currentData.northbound_thru + currentData.northbound_right;
      
      // Calculate southbound total
      const sbTotal = currentData.southbound_left + currentData.southbound_thru + currentData.southbound_right;
      
      // Store actual vehicle counts
      setCurrentVehiclesNB(nbTotal);
      setCurrentVehiclesSB(sbTotal);
      
      // Update refs
      currentVehiclesNBRef.current = nbTotal;
      currentVehiclesSBRef.current = sbTotal;
      
      // Normalize to 0-100 scale (assuming max ~400 vehicles per direction)
      const nbVolume = Math.min(100, Math.round((nbTotal / 400) * 100));
      const sbVolume = Math.min(100, Math.round((sbTotal / 400) * 100));
      
      setTrafficVolumeNB(nbVolume);
      setTrafficVolumeSB(sbVolume);
      
      // Update refs
      trafficVolumeNBRef.current = nbVolume;
      trafficVolumeSBRef.current = sbVolume;
      
      console.log(`Time: ${currentData.reading_timestamp}, NB: ${nbTotal} (${nbVolume}%), SB: ${sbTotal} (${sbVolume}%)`);
      
      // Move to next data point, loop back to start if at end
      setCurrentIndex((prevIndex) => (prevIndex + 1) % trafficData.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [trafficData, currentIndex]);

  // Function to get color based on traffic volume (0-100)
  const getTrafficColor = (volume: number): string => {
    if (volume <= 33) {
      const ratio = volume / 33;
      const r = Math.round(34 + (139 - 34) * ratio);
      const g = Math.round(197 + (195 - 197) * ratio);
      const b = Math.round(94 + (66 - 94) * ratio);
      return `rgb(${r}, ${g}, ${b})`;
    } else if (volume <= 66) {
      const ratio = (volume - 33) / 33;
      const r = Math.round(139 + (245 - 139) * ratio);
      const g = Math.round(195 + (158 - 195) * ratio);
      const b = Math.round(66 + (11 - 66) * ratio);
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      const ratio = (volume - 66) / 34;
      const r = Math.round(245 + (239 - 245) * ratio);
      const g = Math.round(158 - 158 * ratio);
      const b = Math.round(11 - 11 * ratio);
      return `rgb(${r}, ${g}, ${b})`;
    }
  };

  // Initialize map only once - on mount
  useEffect(() => {
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

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-71.1189, 42.3736],
      zoom: 12,
      pitch: 60,
      bearing: -17.5,
      antialias: true,
    });

    map.current.addControl(new mapboxgl.NavigationControl({
      visualizePitch: true
    }), 'top-right');

    map.current.on('load', () => {
      console.info('Map loaded successfully');

      map.current!.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14,
      });

      map.current!.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });

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

    map.current.on('style.load', () => {
      console.log('Style loaded, adding 3D buildings...');

      const layers = map.current!.getStyle().layers;
      let labelLayerId: string | undefined;

      for (const layer of layers || []) {
        if (layer.type === 'symbol' && layer.layout && layer.layout['text-field']) {
          labelLayerId = layer.id;
          break;
        }
      }

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
                '#fbbf24',
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

      if (!map.current!.getSource('mass-ave-nb')) {
        map.current!.addSource('mass-ave-nb', {
          type: 'geojson',
          data: MassAveNB as FeatureCollection<LineString, GeoJsonProperties>
        });

        map.current!.addLayer({
          id: 'mass-ave-nb-glow',
          type: 'line',
          source: 'mass-ave-nb',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': getTrafficColor(trafficVolumeNB),
            'line-width': 8,
            'line-opacity': 0.4,
            'line-blur': 4,
          },
        });

        map.current!.addLayer({
          id: 'mass-ave-nb-highlight',
          type: 'line',
          source: 'mass-ave-nb',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': getTrafficColor(trafficVolumeNB),
            'line-width': 4,
            'line-opacity': 0.8,
          },
        });
      }

      if (!map.current!.getSource('mass-ave-sb')) {
        map.current!.addSource('mass-ave-sb', {
          type: 'geojson',
          data: MassAveSB as FeatureCollection<LineString, GeoJsonProperties>
        });

        map.current!.addLayer({
          id: 'mass-ave-sb-glow',
          type: 'line',
          source: 'mass-ave-sb',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': getTrafficColor(trafficVolumeSB),
            'line-width': 8,
            'line-opacity': 0.4,
            'line-blur': 4,
          },
        });

        map.current!.addLayer({
          id: 'mass-ave-sb-highlight',
          type: 'line',
          source: 'mass-ave-sb',
          layout: { 'line-join': 'round', 'line-cap': 'round' },
          paint: {
            'line-color': getTrafficColor(trafficVolumeSB),
            'line-width': 4,
            'line-opacity': 0.8,
          },
        });
      }

      // Road hover popups
      roadPopupRef.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      // Northbound road hover
      const updateNBPopup = (e: mapboxgl.MapMouseEvent) => {
        map.current!.getCanvas().style.cursor = 'pointer';

        roadPopupRef.current!
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h4 style="margin: 0 0 4px 0; font-weight: 600; color: #fff;">Massachusetts Ave Northbound</h4>
              <p style="margin: 0; font-size: 12px; color: #d1d5db;">Traffic Volume: <strong style="color: ${getTrafficColor(trafficVolumeNBRef.current)}">${currentVehiclesNBRef.current} vehicles (${trafficVolumeNBRef.current}%)</strong></p>
            </div>
          `)
          .addTo(map.current!);
      };
      
      map.current!.on('mouseenter', 'mass-ave-nb-highlight', updateNBPopup);

      map.current!.on('mouseleave', 'mass-ave-nb-highlight', () => {
        map.current!.getCanvas().style.cursor = '';
        roadPopupRef.current!.remove();
      });

      // Southbound road hover
      const updateSBPopup = (e: mapboxgl.MapMouseEvent) => {
        map.current!.getCanvas().style.cursor = 'pointer';

        roadPopupRef.current!
          .setLngLat(e.lngLat)
          .setHTML(`
            <div style="padding: 8px; font-family: system-ui, -apple-system, sans-serif;">
              <h4 style="margin: 0 0 4px 0; font-weight: 600; color: #fff;">Massachusetts Ave Southbound</h4>
              <p style="margin: 0; font-size: 12px; color: #d1d5db;">Traffic Volume: <strong style="color: ${getTrafficColor(trafficVolumeSBRef.current)}">${currentVehiclesSBRef.current} vehicles (${trafficVolumeSBRef.current}%)</strong></p>
            </div>
          `)
          .addTo(map.current!);
      };
      
      map.current!.on('mouseenter', 'mass-ave-sb-highlight', updateSBPopup);

      map.current!.on('mouseleave', 'mass-ave-sb-highlight', () => {
        map.current!.getCanvas().style.cursor = '';
        roadPopupRef.current!.remove();
      });

      if (!pinpoints || pinpoints.length === 0) {
        return;
      }

      const pinpointsGeoJSON: FeatureCollection<Point, GeoJsonProperties> = {
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

      if (!map.current!.getSource('pinpoints')) {
        map.current!.addSource('pinpoints', {
          type: 'geojson',
          data: pinpointsGeoJSON,
        });
      }

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

      let hoveredBuildingId: string | number | null = null;

      hoverPopup.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

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

          hoverPopup.current!.setLngLat(coordinates).setHTML(description).addTo(map.current!);
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
        hoverPopup.current!.remove();
      });

      map.current!.on('click', '3d-buildings', (e) => {
        if (e.features && e.features.length > 0) {
          const feature = e.features[0];
          const properties = feature.properties;

          const buildingInfo = {
            name: properties?.name || 'Unnamed Building',
            height: properties?.height || 'N/A',
            type: properties?.type || 'Commercial',
            underground: properties?.underground || 'No',
            minHeight: properties?.min_height || 0,
          };

          console.log('Building clicked:', buildingInfo);

          if (clickPopup.current) {
            clickPopup.current.remove();
          }

          clickPopup.current = new mapboxgl.Popup({
            offset: 25,
            closeButton: true,
            closeOnClick: true,
            closeOnMove: false,
            maxWidth: '280px',
            className: 'building-details-popup'
          })
            .setLngLat(e.lngLat)
            .setHTML(
              `<div style="padding: 12px; font-family: system-ui, -apple-system, sans-serif;">
                <div style="border-bottom: 1px solid #fbbf24; padding-bottom: 8px; margin-bottom: 12px;">
                  <h3 style="margin:0; font-weight:600; font-size:16px; color: #fff;">
                    ${buildingInfo.name}
                  </h3>
                  <p style="margin:2px 0 0 0; font-size:11px; color: #9ca3af;">
                    ${buildingInfo.type}
                  </p>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
                  <div style="background: rgba(251, 191, 36, 0.1); padding: 8px; border-radius: 4px; border-left: 2px solid #fbbf24;">
                    <p style="margin:0; font-size:10px; color: #9ca3af; text-transform: uppercase;">Height</p>
                    <p style="margin:2px 0 0 0; font-size:14px; font-weight:600; color: #fbbf24;">${buildingInfo.height}m</p>
                  </div>
                  <div style="background: rgba(34, 197, 94, 0.1); padding: 8px; border-radius: 4px; border-left: 2px solid #22c55e;">
                    <p style="margin:0; font-size:10px; color: #9ca3af; text-transform: uppercase;">Energy</p>
                    <p style="margin:2px 0 0 0; font-size:14px; font-weight:600; color: #22c55e;">87.3%</p>
                  </div>
                </div>
                <div style="font-size:11px; color: #d1d5db; margin-bottom: 12px;">
                  <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                    <span>Consumption:</span>
                    <strong style="color: #22c55e;">124.5 MWh/yr</strong>
                  </div>
                  <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                    <span>CO₂ Emissions:</span>
                    <strong style="color: #f59e0b;">48.2 tons/yr</strong>
                  </div>
                </div>
                <button 
                  onclick="console.log('View analytics for: ${buildingInfo.name}')" 
                  style="width: 100%; padding: 8px; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #000; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 12px; transition: transform 0.2s;"
                  onmouseover="this.style.transform='scale(1.02)'"
                  onmouseout="this.style.transform='scale(1)'"
                >
                  View Details
                </button>
              </div>`
            )
            .addTo(map.current!);

          clickPopup.current.on('close', () => {
            // Popup closed
          });
        }
      });

      map.current!.on('click', (e) => {
        const features = map.current!.queryRenderedFeatures(e.point, {
          layers: ['3d-buildings']
        });

        if (features.length === 0 && clickPopup.current) {
          clickPopup.current.remove();
        }
      });
    });

    map.current.on('error', (_e) => {
      // Handle map error
    });

    const markersForCleanup = markersRef.current;
    const hoverPopupForCleanup = hoverPopup.current;
    const clickPopupForCleanup = clickPopup.current;
    const roadPopupForCleanup = roadPopupRef.current;

    return () => {
      markersForCleanup.forEach(({ marker }) => marker.remove());
      markersForCleanup.clear();
      if (hoverPopupForCleanup) {
        hoverPopupForCleanup.remove();
      }
      if (clickPopupForCleanup) {
        clickPopupForCleanup.remove();
      }
      if (roadPopupForCleanup) {
        roadPopupForCleanup.remove();
      }
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [pinpoints]);

  // Update road colors when traffic volume changes
  useEffect(() => {
    if (!map.current) return;

    if (map.current.getLayer('mass-ave-nb-glow')) {
      map.current.setPaintProperty('mass-ave-nb-glow', 'line-color', getTrafficColor(trafficVolumeNB));
    }
    if (map.current.getLayer('mass-ave-nb-highlight')) {
      map.current.setPaintProperty('mass-ave-nb-highlight', 'line-color', getTrafficColor(trafficVolumeNB));
    }

    if (map.current.getLayer('mass-ave-sb-glow')) {
      map.current.setPaintProperty('mass-ave-sb-glow', 'line-color', getTrafficColor(trafficVolumeSB));
    }
    if (map.current.getLayer('mass-ave-sb-highlight')) {
      map.current.setPaintProperty('mass-ave-sb-highlight', 'line-color', getTrafficColor(trafficVolumeSB));
    }
  }, [trafficVolumeNB, trafficVolumeSB]);

  // Update marker styles when active study case changes
  useEffect(() => {
    if (!map.current || !pinpoints || pinpoints.length === 0) return;

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