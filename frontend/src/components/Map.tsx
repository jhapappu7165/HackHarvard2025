// Map.tsx
import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';


// BEGIN DEBUG
console.log('Top of Map.tsx loaded');
console.log('mapboxgl object:', mapboxgl);

//CHANGE THIS TO ENV FILE BEFORE PUSH
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;


const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    // Browser/mapbox GL support check
    if (!mapboxgl.supported()) {
      alert('Your browser does not support Mapbox GL');
      console.error('Mapbox GL not supported');
      return;
    }

    // Confirm container ref is set
    if (!mapContainer.current) {
      alert('Map container not found');
      console.error('Map container ref missing');
      return;
    } else {
      console.info('Map container is present and dimensions are:', mapContainer.current.getBoundingClientRect());
    }

    // Confirm access token
    if (!mapboxgl.accessToken || !mapboxgl.accessToken.startsWith('pk.')) {
      alert('Missing or invalid Mapbox public token');
      console.error('Mapbox accessToken:', mapboxgl.accessToken);
      return;
    } else {
      console.log('Using Mapbox access token:', mapboxgl.accessToken);
    }

    // Initialize map and listen for errors/load
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-71.0589, 42.3601],
      zoom: 12,
    });

    map.current.on('load', () => {
      console.info('Map loaded successfully');
    });

    map.current.on('error', (e) => {
      alert('Mapbox map error detected. See console for details.');
      console.error('Mapbox map error event:', e.error);
    });

    
  }, []);

  return (
    <div
      ref={mapContainer}
      style={{
        width: '100%',
        height: 400,
        background: '#b3e283',
        border: '2px dashed #1b5e20',
        position: 'relative',
      }}
      className="map-container"
    >
      {/* Visual debug: fallback text if map does not render */}
      <noscript>
        <p style={{ color: 'red' }}>JavaScript is off. Mapbox maps require JavaScript.</p>
      </noscript>
    </div>
  );
};

export default Map;