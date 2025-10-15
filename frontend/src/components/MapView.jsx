import React, { useMemo } from 'react';
import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip } from 'react-leaflet';

// pathCities: array of city names in order
// cityCoords: mapping { city: { lat, lon } }
export default function MapView({ pathCities = [], cityCoords = {} }) {
  const positions = useMemo(() => {
    return pathCities
      .map((c) => cityCoords[c])
      .filter(Boolean)
      .map(({ lat, lon }) => [lat, lon]);
  }, [pathCities, cityCoords]);

  const center = positions.length > 0 ? positions[Math.floor(positions.length / 2)] : [40.7128, -74.006];

  return (
    <div className="mt-3" style={{ height: 420 }}>
      <MapContainer center={center} zoom={6} style={{ height: '100%', width: '100%' }} scrollWheelZoom={true}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {positions.length >= 2 && (
          <Polyline positions={positions} color="#0d6efd" weight={5} opacity={0.8} />
        )}

        {pathCities.map((c, idx) => {
          const coord = cityCoords[c];
          if (!coord) return null;
          return (
            <CircleMarker key={c + idx} center={[coord.lat, coord.lon]} radius={8} pathOptions={{ color: idx === 0 ? 'green' : (idx === pathCities.length - 1 ? 'red' : '#0d6efd') }}>
              <Tooltip permanent direction="top" offset={[0, -8]}>{c}</Tooltip>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
