# Traffic Optimization System (A*)

Find the optimal route between two cities using A* combining distance, traffic, weather, and risk.

## Tech Stack
- Backend: Flask (+ CORS)
- Frontend: React + Axios + Bootstrap

## Project Structure
```
traffic-optimizer/
├── backend/
│   ├── app.py
│   ├── data/
│   │   └── mock_data.py
│   ├── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── RouteFinder.jsx
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
└── README.md
```

## Installation & Running

### 1) Backend (Flask)
```bash
# In traffic-optimizer/backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
# Server runs on http://localhost:5000
```

### 2) Frontend (React)
```bash
# In traffic-optimizer/frontend
npm install
npm start
# App opens on http://localhost:3000
```

The frontend proxies API calls to the backend at `http://localhost:5000`.

## API
- `GET /api/cities` -> `["New York", ...]`
- `POST /api/route` body `{ start: string, end: string }` -> `{ path: string[], breakdown: {...} }`

## A* Cost Function
For each edge:
- Base time = distance_km / (80 km/h)
- Add delays: `+ traffic_min + weather_min`
- Apply risk: `* risk`

Heuristic uses straight-line (haversine) distance converted to minutes with average risk.

## Optional Extensions
- Add map view with React-Leaflet by installing `react-leaflet` and `leaflet` and rendering the path coordinates.
- Integrate live weather via OpenWeatherMap API and adjust `weather_min` dynamically.
