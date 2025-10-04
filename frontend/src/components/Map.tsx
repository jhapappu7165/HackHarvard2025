import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { useDashboardStore } from '@/store/dashboardStore';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const markers = useRef<mapboxgl.Marker[]>([]);
  
  const { pinpoints, setActiveStudyCase, activeStudyCase } = useDashboardStore();

  useEffect(() => {
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

    // Initialize map
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-71.0589, 42.3601],
      zoom: 12.5,
    });

    map.current.on('load', () => {
      console.info('Map loaded successfully');
      
      // Add pinpoint markers
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

        // Color and icon based on type
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

        // Highlight active marker
        if (activeStudyCase === pinpoint.type) {
          el.style.transform = 'scale(1.3)';
          el.style.boxShadow = '0 6px 20px rgba(255,255,255,0.5)';
        }

        el.addEventListener('click', () => {
          setActiveStudyCase(
            activeStudyCase === pinpoint.type ? null : pinpoint.type
          );
        });

        const marker = new mapboxgl.Marker(el)
          .setLngLat(pinpoint.coordinates)
          .setPopup(
            new mapboxgl.Popup({ offset: 25 }).setHTML(
              `<h3 style="margin:0; font-weight:bold;">${pinpoint.name}</h3>
               <p style="margin:4px 0 0 0; text-transform:capitalize;">${pinpoint.type} Analysis</p>`
            )
          )
          .addTo(map.current!);

        markers.current.push(marker);
      });
    });

    map.current.on('error', (e) => {
      console.error('Mapbox map error event:', e.error);
    });

    return () => {
      markers.current.forEach((marker) => marker.remove());
      markers.current = [];
      map.current?.remove();
    };
  }, []);

  // Update marker styles when active study case changes
  useEffect(() => {
    markers.current.forEach((marker, index) => {
      const el = marker.getElement();
      const pinpoint = pinpoints[index];
      
      if (activeStudyCase === pinpoint.type) {
        el.style.transform = 'scale(1.3)';
        el.style.boxShadow = '0 6px 20px rgba(255,255,255,0.5)';
      } else {
        el.style.transform = 'scale(1)';
        el.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
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