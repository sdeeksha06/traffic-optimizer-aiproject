import React, { useMemo, useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip } from 'react-leaflet';
import L from 'leaflet';

// pathCities: array of city names in order
// cityCoords: mapping { city: { lat, lon } }
export default function MapView({ pathCities = [], cityCoords = {} }) {
  const positions = useMemo(() => {
    return pathCities
      .map((c) => cityCoords[c])
      .filter(Boolean)
      .map(({ lat, lon }) => [lat, lon]);
  }, [pathCities, cityCoords]);

  // Default center: Hyderabad, Telangana
  const TELANGANA_CENTER = [17.3850, 78.4867];
  const center = positions.length > 0 ? positions[Math.floor(positions.length / 2)] : TELANGANA_CENTER;

  const [map, setMap] = useState(null);

  // Add scale and move the zoom control to top-right when map is created
  useEffect(() => {
    if (!map) return;
    // remove default zoom control if present and add a top-right one
    if (map.zoomControl) map.zoomControl.remove();
    L.control.zoom({ position: 'topright' }).addTo(map);
    L.control.scale({ position: 'bottomleft', metric: true, imperial: false }).addTo(map);

    return () => {
      // cleanup: remove added controls
      try { map.zoomControl.remove(); } catch (e) {}
    };
  }, [map]);

  // choose a pleasant tile provider (Carto Light) for a modern look
  const tileUrl = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png';
  const tileAttribution = '&copy; <a href="https://carto.com/attributions">CARTO</a> &copy; OpenStreetMap contributors';

  return (
    <div className="mt-3" style={{ height: 480, position: 'relative' }}>
      {/* Legend overlay */}
      <div style={{ position: 'absolute', top: 12, right: 12, zIndex: 400, minWidth: 160 }}>
        <div className="route-legend app-card small">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <strong style={{ color: '#0b5ed7' }}>Route</strong>
            <span className="badge">Telangana</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <div><span style={{ display: 'inline-block', width: 14, height: 6, background: '#cfe2ff', marginRight: 8 }}></span> Route shadow</div>
            <div><span style={{ display: 'inline-block', width: 14, height: 6, background: '#0d6efd', marginRight: 8 }}></span> Route</div>
            <div><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 6, background: 'green', marginRight: 8 }}></span> Start</div>
            <div><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: 6, background: 'red', marginRight: 8 }}></span> End</div>
          </div>
        </div>
      </div>

      <MapContainer
        center={center}
        zoom={positions.length > 0 ? 7 : 7}
        style={{ height: '100%', width: '100%', borderRadius: 10 }}
        scrollWheelZoom={true}
        whenCreated={(m) => setMap(m)}
        zoomControl={false}
      >
        <TileLayer attribution={tileAttribution} url={tileUrl} />

        {/* Underlay shadow for better visual depth */}
        {positions.length >= 2 && (
          <Polyline positions={positions} pathOptions={{ color: '#cfe2ff', weight: 12, opacity: 0.5 }} />
        )}

        {positions.length >= 2 && (
          <Polyline positions={positions} pathOptions={{ color: '#0d6efd', weight: 6, opacity: 0.95 }} />
        )}

        {pathCities.map((c, idx) => {
          const coord = cityCoords[c];
          if (!coord) return null;
          const isStart = idx === 0;
          const isEnd = idx === pathCities.length - 1;
          const fill = isStart ? 'green' : isEnd ? 'red' : '#0d6efd';
          const radius = isStart || isEnd ? 10 : 7;

          return (
            <CircleMarker
              key={c + idx}
              center={[coord.lat, coord.lon]}
              radius={radius}
              pathOptions={{ color: fill, fillColor: fill, fillOpacity: 0.95, weight: 1 }}
            >
              <Tooltip direction="top" offset={[0, -8]}>
                <div style={{ fontWeight: 700 }}>{c}</div>
                <div className="small muted">{isStart ? 'Start' : isEnd ? 'End' : `Stop ${idx + 1}`}</div>
              </Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
