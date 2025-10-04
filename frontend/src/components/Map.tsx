import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

// Import GeoJSON files (declarations.d.ts needed for this)
import MassAveNB from '../assets/MassAveNB.json';
import MassAveSB from '../assets/MassAveSB.json';

// Set access token (use your .env for production)
mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapboxgl.supported()) {
      alert('Your browser does not support Mapbox GL');
      return;
    }
    if (!mapContainer.current) return;

    // Example: Set or update dynamic traffic values (use real data here)
    const nbTrafficCount = 120;
    const sbTrafficCount = 80;

    // Add/update properties to northbound and southbound features
    const MassAveNBWithProps = {
      ...MassAveNB,
      features: MassAveNB.features.map((f: any) => ({
        ...f,
        properties: { ...(f.properties || {}), trafficCount: nbTrafficCount, direction: 'northbound' }
      }))
    };

    const MassAveSBWithProps = {
      ...MassAveSB,
      features: MassAveSB.features.map((f: any) => ({
        ...f,
        properties: { ...(f.properties || {}), trafficCount: sbTrafficCount, direction: 'southbound' }
      }))
    };

    // Create map instance
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-71.0589, 42.3601], // Boston
      zoom: 15,
    });

    map.current.on('load', () => {
      // Northbound
      map.current?.addSource('MassAveNB', {
        type: 'geojson',
        data: MassAveNBWithProps,
      });
      map.current?.addLayer({
        id: 'MassAveNB-layer',
        type: 'line',
        source: 'MassAveNB',
        paint: {
          'line-width': 6,
          'line-color': [
            'interpolate',
            ['linear'],
            ['get', 'trafficCount'],
            0, '#00FF00',     // green
            100, '#FFFF00',   // yellow
            200, '#FF0000'    // red
          ]
        },
      });

      // Southbound
      map.current?.addSource('MassAveSB', {
        type: 'geojson',
        data: MassAveSBWithProps,
      });
      map.current?.addLayer({
        id: 'MassAveSB-layer',
        type: 'line',
        source: 'MassAveSB',
        paint: {
          'line-width': 6,
          'line-color': [
            'interpolate',
            ['linear'],
            ['get', 'trafficCount'],
            0, '#00FF00',
            100, '#FFFF00',
            200, '#FF0000'
          ]
        },
      });
    });

    // Clean up on unmount
    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
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
    />
  );
};

export default Map;
