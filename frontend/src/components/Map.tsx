import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import MassAveSB from '../assets/MassAveSB.json';
import MassAveNB from '../assets/MassAveNB.json';
import type { FeatureCollection, LineString, GeoJsonProperties } from 'geojson';
import type { Building } from '@/types';


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


interface WeatherDataPoint {
  id: number;
  weatherType: string;
  temp: number;
}

interface MapProps {
  onBuildingSelect?: (building: Building) => void;
}

const Map: React.FC<MapProps> = ({ onBuildingSelect }) => {
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
  const [, setCurrentVehiclesNB] = useState(0);
  const [, setCurrentVehiclesSB] = useState(0);

  // Weather state
  const [weatherData, setWeatherData] = useState<WeatherDataPoint[]>([]);
  const [currentWeatherIndex, setCurrentWeatherIndex] = useState(0);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');

  // Building state
  const [buildingData, setBuildingData] = useState<Building[]>([]);

  // State for tracking current data index
  const [trafficData, setTrafficData] = useState<TrafficDataPoint[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [lastAlertSent, setLastAlertSent] = useState<number>(0);

  const sendPoopAlert = async (alertMessage: string, weatherType: string) => {
    const now = Date.now();
    if (now - lastAlertSent < 10000) { // 10 seconds in milliseconds
      console.log('Skipping email - sent too recently');
      return;
    }

    setLastAlertSent(now);

    try {
      // Replace these with actual user data from your auth/user store
      const userId = '27'; // TODO: Get from your auth context/store
      const userEmail = 'aabmtho12@gmail.com'; // TODO: Get from your auth context/store
      const userName = 'Allen'; // TODO: Get from your auth context/store

      const response = await fetch('http://localhost:5001/api/sim/poop-alert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          user_email: userEmail,
          user_name: userName,
          tamagotchi_name: `Traffic Alert - ${weatherType}`,
          custom_message: alertMessage
        })
      });

      const data = await response.json();
      console.log('Alert email result:', data);
    } catch (error) {
      console.error('Error sending alert email:', error);
    }
  };

  // Fetch traffic data on mount
  // Fetch traffic data on mount
  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
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

    const fetchWeatherData = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/sim/weather');
        const result = await response.json();

        if (result.success && result.data) {
          setWeatherData(result.data);
          console.log(`Loaded ${result.data.length} weather data points`);
        }
      } catch (error) {
        console.error('Error fetching weather data:', error);
      }
    };

    const fetchBuildingData = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/energy/buildings');
        const result = await response.json();

        if (result.success && result.buildings) {
          setBuildingData(result.buildings);
          console.log(`Loaded ${result.buildings.length} buildings`);
        }
      } catch (error) {
        console.error('Error fetching building data:', error);
      }
    };

    fetchTrafficData();
    fetchWeatherData();
    fetchBuildingData();
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
  // Check for weather alerts
  useEffect(() => {
    if (weatherData.length === 0) return;

    const currentWeather = weatherData[currentWeatherIndex];
    const weatherType = currentWeather.weatherType;
    const nbVolume = trafficVolumeNB;
    const sbVolume = trafficVolumeSB;
    const maxVolume = Math.max(nbVolume, sbVolume);

    let alert = '';

    if (weatherType === 'Rainy' && maxVolume > 65) {
      const roadDirection = nbVolume > sbVolume ? 'Northbound' : 'Southbound';
      alert = `ALERT! Many drivers on the road in dangerous conditions, possible flooding. Massachusetts Ave ${roadDirection} is at ${maxVolume}% capacity`;
    } else if (weatherType === 'Thunder Storm' && maxVolume > 35) {
      const roadDirection = nbVolume > sbVolume ? 'Northbound' : 'Southbound';
      alert = `ALERT! Many drivers on the road in dangerous conditions, possible flooding. Massachusetts Ave ${roadDirection} is at ${maxVolume}% capacity`;
    } else if (weatherType === 'Ice' && maxVolume > 15) {
      alert = `ALERT! The road is at ${maxVolume}% capacity and it is ICY!!`;
    }


    if (alert) {
      setAlertMessage(alert);
      setShowAlert(true);
      sendPoopAlert(alert, weatherType);
    } else {
      setShowAlert(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [weatherData, currentWeatherIndex, trafficVolumeNB, trafficVolumeSB]);

  // Keyboard handler for 'o' key to cycle weather
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'o' || e.key === 'O') {
        setCurrentWeatherIndex((prevIndex) => (prevIndex + 1) % weatherData.length);
        console.log('Weather cycled to index:', (currentWeatherIndex + 1) % weatherData.length);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [weatherData.length, currentWeatherIndex]);

  // Effect to add building markers when building data is loaded
  useEffect(() => {
    if (map.current && buildingData.length > 0) {
      addBuildingMarkers();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps  
  }, [buildingData]);
  // Function to add building markers to the map
  const addBuildingMarkers = async () => {
    if (!map.current || buildingData.length === 0) return;

    console.log(`Adding ${buildingData.length} building markers to map`);
    console.log('Buildings to add:', buildingData.map(b => ({ id: b.id, name: b.name, lat: b.latitude, lng: b.longitude })));

    for (const building of buildingData) {
      try {
        // Fetch energy readings for this building
        const energyResponse = await fetch(`http://localhost:5001/api/energy/buildings/${building.id}/readings?limit=10`);
        const energyData = await energyResponse.json();
        const energyReadings = energyData.success ? energyData.readings : [];

        // Calculate total energy consumption
        const totalUsage = energyReadings.reduce((sum: number, reading: any) => sum + reading.usage, 0);
        const totalCost = energyReadings.reduce((sum: number, reading: any) => sum + reading.cost, 0);

        // Create marker element - make it much more visible
        const markerElement = document.createElement('div');
        markerElement.className = 'building-marker';

        // Determine marker size based on building category or size
        const isImportant = ['Administration', 'School', 'Hospital', 'Fire Station', 'Police Headquarters'].includes(building.category);
        const markerSize = isImportant ? 20 : 16;
        const pulseSize = isImportant ? 30 : 24;

        markerElement.innerHTML = `
          <div class="marker-pulse" style="
            position: absolute;
            width: ${pulseSize}px;
            height: ${pulseSize}px;
            border-radius: 50%;
            background: rgba(251, 191, 36, 0.3);
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation: pulse 2s infinite;
          "></div>
          <div class="marker-core" style="
            position: relative;
            width: ${markerSize}px;
            height: ${markerSize}px;
            border-radius: 50%;
            background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
            border: 3px solid #fff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
            font-size: ${isImportant ? '12px' : '10px'};
          ">🏢</div>
        `;

        markerElement.style.cssText = `
          position: relative;
          cursor: pointer;
          transition: all 0.3s ease;
          z-index: 100;
        `;

        // Add CSS animation for pulse effect
        if (!document.querySelector('#building-marker-styles')) {
          const style = document.createElement('style');
          style.id = 'building-marker-styles';
          style.textContent = `
            @keyframes pulse {
              0% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
              50% { transform: translate(-50%, -50%) scale(1.2); opacity: 0.3; }
              100% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
            }
            .building-marker:hover .marker-core {
              transform: scale(1.3);
              box-shadow: 0 6px 20px rgba(251, 191, 36, 0.6);
            }
            .building-marker:hover .marker-pulse {
              animation-duration: 1s;
            }
            .mapboxgl-popup {
              z-index: 999999 !important;
            }
            .mapboxgl-popup-content {
              z-index: 999999 !important;
            }
            .building-details-popup {
              z-index: 999999 !important;
            }
            .building-details-popup .mapboxgl-popup-content {
              z-index: 999999 !important;
            }
          `;
          document.head.appendChild(style);
        }

        // Add hover effects with building info tooltip
        let hoverTimeout: NodeJS.Timeout;
        const hoverPopup = new mapboxgl.Popup({
          closeButton: false,
          closeOnClick: false,
          offset: 15
        });

        markerElement.addEventListener('mouseenter', () => {
          hoverTimeout = setTimeout(() => {
            hoverPopup.setLngLat([building.longitude, building.latitude])
              .setHTML(`
                <div style="padding: 8px; font-family: system-ui, sans-serif; max-width: 200px;">
                  <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600; color: #fbbf24;">
                    ${building.name}
                  </h4>
                  <p style="margin: 0; font-size: 11px; color: #9ca3af;">
                    ${building.category} • ${building.square_feet.toLocaleString()} sq ft
                  </p>
                  <p style="margin: 4px 0 0 0; font-size: 10px; color: #6b7280;">
                    Click for detailed energy data
                  </p>
                </div>
              `)
              .addTo(map.current!);
          }, 500);
        });

        markerElement.addEventListener('mouseleave', () => {
          clearTimeout(hoverTimeout);
          hoverPopup.remove();
        });

        // Create marker
        const marker = new mapboxgl.Marker(markerElement)
          .setLngLat([building.longitude, building.latitude])
          .addTo(map.current);

        // Calculate energy efficiency (usage per square foot)
        const usagePerSqft = totalUsage > 0 ? (totalUsage / building.square_feet).toFixed(2) : 'N/A';
        const efficiencyColor = totalUsage > 0 ? (totalUsage / building.square_feet > 0.1 ? '#ef4444' : '#22c55e') : '#9ca3af';

        // Create popup for building with consistent styling
        const popup = new mapboxgl.Popup({
          offset: 25,
          closeButton: true,
          closeOnClick: true,
          closeOnMove: false,
          maxWidth: '280px',
          className: 'building-details-popup'
        }).setHTML(`
          <div style="padding: 12px; font-family: system-ui, -apple-system, sans-serif;">
            <div style="border-bottom: 1px solid #fbbf24; padding-bottom: 8px; margin-bottom: 12px;">
              <h3 style="margin:0; font-weight:600; font-size:16px; color: #fff;">
                ${building.name}
              </h3>
              <p style="margin:2px 0 0 0; font-size:11px; color: #9ca3af;">
                ${building.category} • Built ${building.year_built}
              </p>
            </div>
            
            <div style="margin-bottom: 12px;">
              <p style="margin: 0; font-size: 11px; color: #d1d5db;">
                <strong>Address:</strong> ${building.address}, ${building.city}
              </p>
              <p style="margin: 4px 0 0 0; font-size: 11px; color: #d1d5db;">
                <strong>Size:</strong> ${building.square_feet.toLocaleString()} sq ft
              </p>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px;">
              <div style="background: rgba(251, 191, 36, 0.1); padding: 8px; border-radius: 4px; border-left: 2px solid #fbbf24;">
                <p style="margin:0; font-size:10px; color: #9ca3af; text-transform: uppercase;">Usage</p>
                <p style="margin:2px 0 0 0; font-size:14px; font-weight:600; color: #fbbf24;">${totalUsage > 0 ? totalUsage.toFixed(1) : 'N/A'} kWh</p>
              </div>
              <div style="background: rgba(34, 197, 94, 0.1); padding: 8px; border-radius: 4px; border-left: 2px solid #22c55e;">
                <p style="margin:0; font-size:10px; color: #9ca3af; text-transform: uppercase;">Cost</p>
                <p style="margin:2px 0 0 0; font-size:14px; font-weight:600; color: #22c55e;">$${totalCost > 0 ? totalCost.toFixed(0) : 'N/A'}</p>
              </div>
            </div>

            ${energyReadings.length > 0 ? `
              <div style="font-size:11px; color: #d1d5db; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                  <span>Efficiency:</span>
                  <strong style="color: ${efficiencyColor};">${usagePerSqft} kWh/sqft</strong>
                </div>
                <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                  <span>Data Points:</span>
                  <strong style="color: #fbbf24;">${energyReadings.length}</strong>
                </div>
              </div>
            ` : `
              <div style="font-size:11px; color: #d1d5db; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; padding: 4px 0;">
                  <span>Energy Data:</span>
                  <strong style="color: #9ca3af;">No data available</strong>
                </div>
              </div>
            `}

            <button 
              id="building-details-btn-${building.id}"
              style="width: 100%; padding: 8px; background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); color: #000; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 12px; transition: transform 0.2s;"
              onmouseover="this.style.transform='scale(1.02)'"
              onmouseout="this.style.transform='scale(1)'"
            >
              View Details
            </button>
          </div>
        `);

        // Add click event to marker
        markerElement.addEventListener('click', (e) => {
          e.stopPropagation();

          // Close any existing popups first
          if (clickPopup.current) {
            clickPopup.current.remove();
          }

          // Close any existing building popups
          document.querySelectorAll('.mapboxgl-popup').forEach(popup => {
            const closeButton = popup.querySelector('.mapboxgl-popup-close-button');
            if (closeButton) {
              (closeButton as HTMLElement).click();
            }
          });

          // Show building popup
          const activePopup = popup.setLngLat([building.longitude, building.latitude]).addTo(map.current!);

          // Store reference to current building popup for cleanup
          clickPopup.current = activePopup;

          // Add event listener for View Details button
          setTimeout(() => {
            const detailsButton = document.getElementById(`building-details-btn-${building.id}`);
            if (detailsButton) {
              detailsButton.addEventListener('click', (e) => {
                e.stopPropagation();
                if (onBuildingSelect) {
                  onBuildingSelect(building);
                }
                // Close the popup after navigating
                activePopup.remove();
              });
            }
          }, 100);

          // Add close event listener
          activePopup.on('close', () => {
            if (clickPopup.current === activePopup) {
              clickPopup.current = null;
            }
          });
        });

        // Store marker reference for cleanup
        markersRef.current.set(`building-${building.id}`, { marker, element: markerElement });

        console.log(`Added marker for building: ${building.name} at [${building.longitude}, ${building.latitude}]`);

      } catch (error) {
        console.error(`Error creating marker for building ${building.name}:`, error);
      }
    }

    // Optionally fit the map to show all building markers
    if (buildingData.length > 0 && map.current) {
      const bounds = new mapboxgl.LngLatBounds();
      buildingData.forEach(building => {
        bounds.extend([building.longitude, building.latitude]);
      });

      // Only fit bounds if there are multiple buildings spread out
      const sw = bounds.getSouthWest();
      const ne = bounds.getNorthEast();
      const distance = Math.abs(ne.lng - sw.lng) + Math.abs(ne.lat - sw.lat);

      if (distance > 0.01) { // Only if buildings are spread out
        map.current.fitBounds(bounds, {
          padding: 50,
          maxZoom: 14
        });
      }
    }
  };

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

  // Initialize map
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
      center: [-71.0565, 42.3555],
      zoom: 12,
      pitch: 60,
      bearing: -17.5,
      antialias: true,
    });

    map.current.addControl(new mapboxgl.NavigationControl({
      visualizePitch: true
    }), 'top-right');

    map.current.on('load', () => {
      console.info('===== Map loaded successfully =====');

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
      console.log('===== Style loaded, adding 3D buildings... =====');

      // Debug: Log current zoom level
      console.log('Current zoom level:', map.current!.getZoom());

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
            minzoom: 12,  // Changed from 14 to match initial zoom
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

        // Debug: Verify layer was added
        setTimeout(() => {
          console.log('Layer check:', map.current!.getLayer('3d-buildings'));
          console.log('All layers:', map.current!.getStyle().layers?.map(l => l.id));
        }, 1000);
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

      // Building markers will be added via useEffect when data is loaded

      // Road hover popups
      roadPopupRef.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      console.log('Setting up click handlers...');

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

      // Add general map click handler here, after all layers are set up
      console.log('Setting up click handlers...');
      console.log('Map object exists:', !!map.current);

      map.current!.on('click', (e) => {
        console.log('===== MAP CLICK EVENT FIRED =====');
        console.log('Map clicked at:', e.lngLat);
        console.log('Click point pixel coordinates:', e.point);

        // Check for buildings first
        const buildingFeatures = map.current!.queryRenderedFeatures(e.point, {
          layers: ['3d-buildings']
        });
        console.log('Buildings at click point:', buildingFeatures.length);

        if (buildingFeatures.length > 0) {
          console.log('Building features:', buildingFeatures);

          const feature = buildingFeatures[0];
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

          return; // Stop here, don't close popup
        }

        // Close any popups if we didn't click on a building
        if (clickPopup.current) {
          clickPopup.current.remove();
          clickPopup.current = null;
        }

        // Also close any building marker popups
        document.querySelectorAll('.mapboxgl-popup').forEach(popup => {
          const closeButton = popup.querySelector('.mapboxgl-popup-close-button');
          if (closeButton) {
            (closeButton as HTMLElement).click();
          }
        });
      });

      let hoveredBuildingId: string | number | null = null;

      hoverPopup.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      map.current!.on('mousemove', '3d-buildings', (e) => {
        console.log('Mouse moving over buildings!'); // Debug
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

      map.current!.on('click', (e) => {
        console.log('===== MAP CLICK EVENT FIRED =====');
        console.log('Map clicked at:', e.lngLat);
        console.log('Click point pixel coordinates:', e.point);

        // Check for buildings first
        const buildingFeatures = map.current!.queryRenderedFeatures(e.point, {
          layers: ['3d-buildings']
        });
        console.log('Buildings at click point:', buildingFeatures.length);

        if (buildingFeatures.length > 0) {
          console.log('Building features:', buildingFeatures);

          // If we clicked on a building, handle it and stop
          if (buildingFeatures.length > 0) {
            const feature = buildingFeatures[0];
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

            return; // Stop here, don't close popup
          }

          // Only close popup if we didn't click on a building
          if (clickPopup.current) {
            clickPopup.current.remove();
          }
        }
      });
    });

    map.current.on('error', (e) => {
      console.error('===== MAP ERROR =====', e);
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  return (
    <div style={{ position: 'relative', width: '100%', height: 400 }}>
      {/* Weather Display Box */}
      {weatherData.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '8px 12px',
          borderRadius: '6px',
          zIndex: 1000,
          fontSize: '12px',
          fontWeight: '600',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          backdropFilter: 'blur(10px)'
        }}>
          {weatherData[currentWeatherIndex]?.weatherType} • {weatherData[currentWeatherIndex]?.temp}°C
        </div>
      )}

      {/* Building Legend */}
      {buildingData.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '12px',
          borderRadius: '6px',
          zIndex: 1000,
          fontSize: '11px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          backdropFilter: 'blur(10px)',
          maxWidth: '200px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
            <div style={{
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)',
              border: '2px solid #fff',
              marginRight: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '8px'
            }}>🏢</div>
            <span style={{ fontWeight: '600' }}>Energy Buildings</span>
          </div>
          <div style={{ fontSize: '10px', color: '#9ca3af' }}>
            {buildingData.length} buildings displayed
          </div>
          <div style={{ fontSize: '10px', color: '#9ca3af', marginTop: '4px' }}>
            Click markers for energy data
          </div>
        </div>
      )}

      {/* Alert Popup */}
      {showAlert && (
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          backgroundColor: 'rgba(239, 68, 68, 0.95)',
          color: 'white',
          padding: '20px 24px',
          borderRadius: '8px',
          zIndex: 1000000,
          fontSize: '14px',
          fontWeight: '600',
          maxWidth: '400px',
          textAlign: 'center',
          border: '2px solid #fff',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>⚠️</div>
          {alertMessage}
          <button
            onClick={() => setShowAlert(false)}
            style={{
              marginTop: '12px',
              padding: '6px 16px',
              backgroundColor: 'white',
              color: '#ef4444',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '12px'
            }}
          >
            Dismiss
          </button>
        </div>
      )}

      <div
        ref={mapContainer}
        style={{
          width: '100%',
          height: 400,
          borderRadius: '8px',
          position: 'relative',
          zIndex: 1,
        }}
        className="map-container"
        onClick={() => console.log('DIV CLICKED')}
      />
    </div>
  );
};

export default Map;
