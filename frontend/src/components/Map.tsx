import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import MassAveNB from '../assets/MassAveNB.json';
import MassAveSB from '../assets/MassAveSB.json';
import { FeatureCollection, LineString, GeoJsonProperties } from 'geojson';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    if (!mapboxgl.supported() || !mapContainer.current) return;

    // Example traffic values (replace with dynamic values or props/state)
    const nbTrafficCount = 120;
    const sbTrafficCount = 80;

    // Attach custom properties
    const MassAveNBWithProps = {
      ...MassAveNB,
      features: MassAveNB.features.map((f: any) => ({
        ...f,
        properties: { ...(f.properties || {}), trafficCount: nbTrafficCount, direction: 'northbound' }
      }))
    } as FeatureCollection<LineString, GeoJsonProperties>;
    const MassAveSBWithProps = {
      ...MassAveSB,
      features: MassAveSB.features.map((f: any) => ({
        ...f,
        properties: { ...(f.properties || {}), trafficCount: sbTrafficCount, direction: 'southbound' }
      }))
    } as FeatureCollection<LineString, GeoJsonProperties>;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      center: [-71.0589, 42.3601],
      zoom: 12,
    });

    map.current.on('load', () => {
      if (!map.current) return;

      // Add NB source/layer
      map.current.addSource('massAveNB', {
        type: 'geojson',
        data: MassAveNBWithProps
      });
      map.current.addLayer({
        id: 'massAveNB-layer',
        type: 'line',
        source: 'massAveNB',
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
        }
      });

      // Add SB source/layer
      map.current.addSource('massAveSB', {
        type: 'geojson',
        data: MassAveSBWithProps
      });
      map.current.addLayer({
        id: 'massAveSB-layer',
        type: 'line',
        source: 'massAveSB',
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
        }
      });

      // Clickable NB
      map.current.on('click', 'massAveNB-layer', (e: any) => {
        if (!e.features || !e.features[0]) return;
        const feature = e.features[0];
        const count = feature.properties.trafficCount;
        const direction = feature.properties.direction;
        new mapboxgl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`<strong>${direction}</strong><br/>Traffic: ${count}`)
          .addTo(map.current!);
      });

      // Clickable SB
      map.current.on('click', 'massAveSB-layer', (e: any) => {
        if (!e.features || !e.features[0]) return;
        const feature = e.features[0];
        const count = feature.properties.trafficCount;
        const direction = feature.properties.direction;
        new mapboxgl.Popup()
          .setLngLat(e.lngLat)
          .setHTML(`<strong>${direction}</strong><br/>Traffic: ${count}`)
          .addTo(map.current!);
      });

      // Cursor pointer for NB
      map.current.on('mouseenter', 'massAveNB-layer', () => {
        map.current?.getCanvas().style && (map.current.getCanvas().style.cursor = 'pointer');
      });
      map.current.on('mouseleave', 'massAveNB-layer', () => {
        map.current?.getCanvas().style && (map.current.getCanvas().style.cursor = '');
      });

      // Cursor pointer for SB
      map.current.on('mouseenter', 'massAveSB-layer', () => {
        map.current?.getCanvas().style && (map.current.getCanvas().style.cursor = 'pointer');
      });
      map.current.on('mouseleave', 'massAveSB-layer', () => {
        map.current?.getCanvas().style && (map.current.getCanvas().style.cursor = '');
      });
    });

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
