import React, { useEffect, useState } from 'react';
import axios from 'axios';
import MapView from './MapView';

export default function RouteFinder() {
  const [cities, setCities] = useState([]);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [cityCoords, setCityCoords] = useState({});

  useEffect(() => {
    async function loadCities() {
      try {
        const res = await axios.get('/api/cities');
        setCities(res.data || []);
      } catch (e) {
        setError('Failed to load cities');
      }
    }
    async function loadCoords() {
      try {
        const res = await axios.get('/api/city_coords');
        setCityCoords(res.data || {});
      } catch (e) {
        // Non-fatal if map coords can't load
      }
    }
    loadCities();
    loadCoords();
  }, []);

  const onSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setResult(null);
    if (!start || !end) {
      setError('Please select both start and end cities');
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post('/api/route', { start, end });
      setResult(res.data);
    } catch (e) {
      const msg = e?.response?.data?.error || 'Failed to compute route';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-body">
        <form onSubmit={onSubmit} className="row g-3">
          <div className="col-md-5">
            <label className="form-label">Start City</label>
            <select className="form-select" value={start} onChange={(e) => setStart(e.target.value)}>
              <option value="">Select start</option>
              {cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="col-md-5">
            <label className="form-label">End City</label>
            <select className="form-select" value={end} onChange={(e) => setEnd(e.target.value)}>
              <option value="">Select end</option>
              {cities.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
          <div className="col-md-2 d-flex align-items-end">
            <button className="btn btn-primary w-100" type="submit" disabled={loading}>
              {loading ? 'Finding...' : 'Find Best Route'}
            </button>
          </div>
        </form>

        {error && (
          <div className="alert alert-danger mt-3" role="alert">{error}</div>
        )}

        {result && (
          <div className="mt-4">
            <h5>Best Route</h5>
            <p className="mb-1"><strong>Path:</strong> {result.path.join(' → ')}</p>
            <p><strong>Estimated Total Time:</strong> {result.breakdown.estimated_total_time_min} min</p>

            <h6>Breakdown</h6>
            <ul className="list-group mb-3">
              <li className="list-group-item">Total Distance: {result.breakdown.total_distance_km} km</li>
              <li className="list-group-item">Traffic Delays: {result.breakdown.total_traffic_min} min</li>
              <li className="list-group-item">Weather Delays: {result.breakdown.total_weather_min} min</li>
              <li className="list-group-item">Risk Extra Time: {result.breakdown.risk_extra_time_min} min</li>
            </ul>

            <h6>Legs</h6>
            <div className="table-responsive">
              <table className="table table-striped">
                <thead>
                  <tr>
                    <th>From</th>
                    <th>To</th>
                    <th>Distance (km)</th>
                    <th>Traffic (min)</th>
                    <th>Weather (min)</th>
                    <th>Risk</th>
                    <th>Est. Time (min)</th>
                  </tr>
                </thead>
                <tbody>
                  {result.breakdown.legs.map((leg, idx) => (
                    <tr key={idx}>
                      <td>{leg.from}</td>
                      <td>{leg.to}</td>
                      <td>{leg.distance_km}</td>
                      <td>{leg.traffic_min}</td>
                      <td>{leg.weather_min}</td>
                      <td>{leg.risk}</td>
                      <td>{leg.estimated_time_min}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <h6>Map</h6>
            <MapView pathCities={result.path} cityCoords={cityCoords} />
          </div>
        )}
      </div>
    </div>
  );
}
