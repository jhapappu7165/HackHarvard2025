import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import MassAveSB from '../assets/MassAveSB.json';
import MassAveNB from '../assets/MassAveNB.json';
import type { FeatureCollection, LineString, GeoJsonProperties} from 'geojson';

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN as string;
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://boston-daddy-production.up.railway.app';

const BUILDINGS_WITH_DATA = [
  { id: 1, name: 'Central Library', coords: [-71.0779, 42.3493] as [number, number], category: 'Recreation Center', sqft: 63726, year: 1967, usage: 2100, cost: 252000, efficiency: 112.3, co2: 845 },
  { id: 2, name: 'City Hall', coords: [-71.0914, 42.3655] as [number, number], category: 'Public Safety', sqft: 62766, year: 2014, usage: 2400, cost: 288000, efficiency: 130.2, co2: 966 },
  { id: 3, name: 'Community Center', coords: [-71.0939, 42.3596] as [number, number], category: 'School', sqft: 45291, year: 1970, usage: 1850, cost: 222000, efficiency: 139.1, co2: 744 },
  { id: 4, name: 'Fire Station #1', coords: [-71.1163, 42.3766] as [number, number], category: 'School', sqft: 89991, year: 2008, usage: 3200, cost: 384000, efficiency: 121.2, co2: 1288 },
  { id: 5, name: 'Health Department', coords: [-71.0868, 42.3625] as [number, number], category: 'Public Works', sqft: 36997, year: 2017, usage: 1450, cost: 174000, efficiency: 133.5, co2: 583 },
  { id: 6, name: 'Municipal Court', coords: [-71.0634, 42.3481] as [number, number], category: 'School', sqft: 24348, year: 1954, usage: 1100, cost: 132000, efficiency: 153.9, co2: 442 },
  { id: 7, name: 'North High School', coords: [-71.0548, 42.3392] as [number, number], category: 'School', sqft: 10215, year: 1954, usage: 580, cost: 69600, efficiency: 193.3, co2: 233 },
  { id: 8, name: 'Parks Department', coords: [-71.0720, 42.3580] as [number, number], category: 'Library', sqft: 42149, year: 1957, usage: 1700, cost: 204000, efficiency: 137.3, co2: 684 },
  { id: 9, name: 'Police Headquarters', coords: [-71.0850, 42.3700] as [number, number], category: 'School', sqft: 49128, year: 2015, usage: 1950, cost: 234000, efficiency: 135.2, co2: 784 },
  { id: 10, name: 'Public Works Facility', coords: [-71.0680, 42.3520] as [number, number], category: 'Recreation Center', sqft: 9982, year: 2009, usage: 480, cost: 57600, efficiency: 163.8, co2: 193 },
  { id: 11, name: 'Recreation Center', coords: [-71.0950, 42.3450] as [number, number], category: 'Recreation Center', sqft: 86892, year: 2010, usage: 3100, cost: 372000, efficiency: 121.6, co2: 1247 },
  { id: 12, name: 'Senior Center', coords: [-71.0600, 42.3550] as [number, number], category: 'Public Safety', sqft: 43638, year: 1961, usage: 1800, cost: 216000, efficiency: 140.6, co2: 724 },
  { id: 13, name: 'South Elementary', coords: [-71.0800, 42.3400] as [number, number], category: 'School', sqft: 57234, year: 2009, usage: 2200, cost: 264000, efficiency: 130.9, co2: 885 },
  { id: 14, name: 'Water Treatment Plant', coords: [-71.0500, 42.3650] as [number, number], category: 'Community Center', sqft: 50995, year: 2015, usage: 2050, cost: 246000, efficiency: 136.9, co2: 825 },
  { id: 15, name: 'Youth Center', coords: [-71.0920, 42.3420] as [number, number], category: 'School', sqft: 86103, year: 1974, usage: 3250, cost: 390000, efficiency: 128.6, co2: 1308 }
];

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

const Map: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const buildingMarkers = useRef<mapboxgl.Marker[]>([]);
  const roadPopupRef = useRef<mapboxgl.Popup | null>(null);
  
  const trafficVolumeNBRef = useRef(35);
  const trafficVolumeSBRef = useRef(68);
  const currentVehiclesNBRef = useRef(0);
  const currentVehiclesSBRef = useRef(0);

  const [trafficVolumeNB, setTrafficVolumeNB] = useState(35);
  const [trafficVolumeSB, setTrafficVolumeSB] = useState(68);
  const [, setCurrentVehiclesNB] = useState(0);
  const [, setCurrentVehiclesSB] = useState(0);
  const [weatherData, setWeatherData] = useState<WeatherDataPoint[]>([]);
  const [currentWeatherIndex, setCurrentWeatherIndex] = useState(0);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [trafficData, setTrafficData] = useState<TrafficDataPoint[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [lastAlertSent, setLastAlertSent] = useState<number>(0);

  const sendPoopAlert = async (alertMessage: string, weatherType: string) => {
    const now = Date.now();
    if (now - lastAlertSent < 10000) {
      console.log('Skipping email - sent too recently');
      return;
    }
    setLastAlertSent(now);
    try {
      const userId = '27';
      const userEmail = 'aabmtho12@gmail.com';
      const userName = 'Allen';
      const response = await fetch(`${API_BASE_URL}/api/sim/poop-alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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

  useEffect(() => {
    const fetchTrafficData = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/traffic/directional?intersection_id=31&limit=24`);
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
        const response = await fetch(`${API_BASE_URL}/api/sim/weather`);
        const result = await response.json();
        if (result.success && result.data) {
          setWeatherData(result.data);
          console.log(`Loaded ${result.data.length} weather data points`);
        }
      } catch (error) {
        console.error('Error fetching weather data:', error);
      }
    };

    fetchTrafficData();
    fetchWeatherData();
  }, []);

  useEffect(() => {
    if (trafficData.length === 0) return;

    const interval = setInterval(() => {
      const currentData = trafficData[currentIndex];
      const nbTotal = currentData.northbound_left + currentData.northbound_thru + currentData.northbound_right;
      const sbTotal = currentData.southbound_left + currentData.southbound_thru + currentData.southbound_right;
      
      setCurrentVehiclesNB(nbTotal);
      setCurrentVehiclesSB(sbTotal);
      currentVehiclesNBRef.current = nbTotal;
      currentVehiclesSBRef.current = sbTotal;
      
      const nbVolume = Math.min(100, Math.round((nbTotal / 400) * 100));
      const sbVolume = Math.min(100, Math.round((sbTotal / 400) * 100));
      
      setTrafficVolumeNB(nbVolume);
      setTrafficVolumeSB(sbVolume);
      trafficVolumeNBRef.current = nbVolume;
      trafficVolumeSBRef.current = sbVolume;
      
      setCurrentIndex((prevIndex) => (prevIndex + 1) % trafficData.length);
    }, 3000);

    return () => clearInterval(interval);
  }, [trafficData, currentIndex]);

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
  }, [weatherData, currentWeatherIndex, trafficVolumeNB, trafficVolumeSB]);

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 'p' || e.key === 'P') {
        setCurrentWeatherIndex((prevIndex) => (prevIndex + 1) % weatherData.length);
        console.log('Weather cycled to index:', (currentWeatherIndex + 1) % weatherData.length);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [weatherData.length, currentWeatherIndex]);

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

  useEffect(() => {
    if (map.current) return;
    if (!mapContainer.current) return;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [-71.0789, 42.3656],
      zoom: 13,
      pitch: 45,
      bearing: -17.6,
    });

    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.current.on('load', () => {
      if (!map.current) return;

      map.current.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14,
      });
      map.current.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });

      BUILDINGS_WITH_DATA.forEach(building => {
        if (!map.current) return;

        const el = document.createElement('div');
        el.style.width = '24px';
        el.style.height = '24px';
        el.style.borderRadius = '50%';
        el.style.backgroundColor = '#22c55e';
        el.style.border = '3px solid #fff';
        el.style.cursor = 'pointer';
        el.style.boxShadow = '0 0 15px rgba(34, 197, 94, 0.8)';

        const popup = new mapboxgl.Popup({ 
          offset: 25,
          closeButton: true,
          closeOnClick: true,
          maxWidth: '320px'
        }).setHTML(`
          <div style="padding: 14px; background: #1f2937; color: #fff; font-family: system-ui, -apple-system, sans-serif;">
            <h3 style="margin: 0 0 10px 0; color: #22c55e; font-size: 17px; font-weight: 700;">${building.name}</h3>
            <p style="margin: 0 0 12px 0; font-size: 13px; color: #9ca3af;">
              <strong style="color: #fff;">${building.category}</strong> • Built ${building.year}
            </p>
            <hr style="border: none; border-top: 1px solid #374151; margin: 10px 0;">
            <div style="font-size: 12px; line-height: 1.6;">
              <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">Square Feet:</span>
                <strong style="color: #fff;">${building.sqft.toLocaleString()}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">Annual Usage:</span>
                <strong style="color: #22c55e;">${building.usage.toLocaleString()} MWh/yr</strong>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">Annual Cost:</span>
                <strong style="color: #fbbf24;">$${building.cost.toLocaleString()}</strong>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #374151;">
                <span style="color: #9ca3af;">CO2 Emissions:</span>
                <strong style="color: #f59e0b;">${building.co2.toLocaleString()} tons/yr</strong>
              </div>
              <div style="display: flex; justify-content: space-between; padding: 6px 0;">
                <span style="color: #9ca3af;">Energy Intensity:</span>
                <strong style="color: #a78bfa;">${building.efficiency.toFixed(1)} kBTU/sf</strong>
              </div>
            </div>
          </div>
        `);

        const marker = new mapboxgl.Marker(el)
          .setLngLat(building.coords)
          .setPopup(popup)
          .addTo(map.current);

        buildingMarkers.current.push(marker);
      });

      map.current.addSource('mass-ave-nb', {
        type: 'geojson',
        data: MassAveNB as FeatureCollection<LineString, GeoJsonProperties>
      });

      map.current.addLayer({
        id: 'mass-ave-nb-line',
        type: 'line',
        source: 'mass-ave-nb',
        paint: {
          'line-color': getTrafficColor(trafficVolumeNB),
          'line-width': 6,
          'line-opacity': 0.8,
        },
      });

      map.current.addSource('mass-ave-sb', {
        type: 'geojson',
        data: MassAveSB as FeatureCollection<LineString, GeoJsonProperties>
      });

      map.current.addLayer({
        id: 'mass-ave-sb-line',
        type: 'line',
        source: 'mass-ave-sb',
        paint: {
          'line-color': getTrafficColor(trafficVolumeSB),
          'line-width': 6,
          'line-opacity': 0.8,
        },
      });

      roadPopupRef.current = new mapboxgl.Popup({
        closeButton: false,
        closeOnClick: false,
      });

      map.current.on('mouseenter', 'mass-ave-nb-line', (e) => {
        if (!map.current) return;
        map.current.getCanvas().style.cursor = 'pointer';
        
        const vehicles = currentVehiclesNBRef.current;
        const volume = trafficVolumeNBRef.current;
        const color = getTrafficColor(volume);
        
        roadPopupRef.current!.setLngLat(e.lngLat).setHTML(`
          <div style="padding: 6px; color: black;">
            <strong>Mass Ave NB</strong><br>
            <span style="color: ${color}; font-weight: bold;">${vehicles} vehicles (${volume}%)</span>
          </div>
        `).addTo(map.current);
      });

      map.current.on('mouseleave', 'mass-ave-nb-line', () => {
        if (!map.current) return;
        map.current.getCanvas().style.cursor = '';
        roadPopupRef.current!.remove();
      });

      map.current.on('mouseenter', 'mass-ave-sb-line', (e) => {
        if (!map.current) return;
        map.current.getCanvas().style.cursor = 'pointer';
        
        const vehicles = currentVehiclesSBRef.current;
        const volume = trafficVolumeSBRef.current;
        const color = getTrafficColor(volume);
        
        roadPopupRef.current!.setLngLat(e.lngLat).setHTML(`
          <div style="padding: 6px; color: black;">
            <strong>Mass Ave SB</strong><br>
            <span style="color: ${color}; font-weight: bold;">${vehicles} vehicles (${volume}%)</span>
          </div>
        `).addTo(map.current);
      });

      map.current.on('mouseleave', 'mass-ave-sb-line', () => {
        if (!map.current) return;
        map.current.getCanvas().style.cursor = '';
        roadPopupRef.current!.remove();
      });
    });

    return () => {
      buildingMarkers.current.forEach(m => m.remove());
      buildingMarkers.current = [];
      if (roadPopupRef.current) roadPopupRef.current.remove();
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    
    if (map.current.getLayer('mass-ave-nb-line')) {
      map.current.setPaintProperty('mass-ave-nb-line', 'line-color', getTrafficColor(trafficVolumeNB));
    }
    if (map.current.getLayer('mass-ave-sb-line')) {
      map.current.setPaintProperty('mass-ave-sb-line', 'line-color', getTrafficColor(trafficVolumeSB));
    }
  }, [trafficVolumeNB, trafficVolumeSB]);

  return (
    <div style={{ position: 'relative', width: '100%', height: 400 }}>
      {weatherData.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '10px',
          left: '10px',
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '8px 12px',
          borderRadius: '6px',
          zIndex: 10,
          fontSize: '12px',
          fontWeight: '600',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          backdropFilter: 'blur(10px)'
        }}>
          {weatherData[currentWeatherIndex]?.weatherType} • {weatherData[currentWeatherIndex]?.temp}°C
        </div>
      )}
  
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
          zIndex: 1000,
          fontSize: '14px',
          fontWeight: '600',
          maxWidth: '400px',
          textAlign: 'center',
          border: '2px solid #fff',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
        }}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>WARNING</div>
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
        }}
      />
    </div>
  );
};

export default Map;