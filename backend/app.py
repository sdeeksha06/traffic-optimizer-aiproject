from flask import Flask, request, jsonify
from flask_cors import CORS
from math import radians, sin, cos, sqrt, atan2
import heapq

from data.mock_data import CITIES, GRAPH
from weather_utils import get_weather_delay

app = Flask(__name__)
CORS(app)

# Configurable assumptions
AVERAGE_SPEED_KMH = 80.0  # km/h
KM_PER_MIN = AVERAGE_SPEED_KMH / 60.0  # km per minute
AVG_RISK = 1.05


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def heuristic_time_min(city_a, city_b):
    a, b = CITIES[city_a], CITIES[city_b]
    dist_km = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
    return (dist_km / KM_PER_MIN) * AVG_RISK


def edge_cost_minutes(edge):
    # Base time from distance
    base_time = edge["distance_km"] / KM_PER_MIN
    # Add delays
    time_with_delays = base_time + edge.get("traffic_min", 0) + edge.get("weather_min", 0)
    # Apply risk multiplier
    return time_with_delays * edge.get("risk", 1.0)


def a_star_route(start, goal):
    if start not in CITIES or goal not in CITIES:
        return None

    open_heap = []
    heapq.heappush(open_heap, (0 + heuristic_time_min(start, goal), 0, start))

    came_from = {}
    g_score = {start: 0}

    while open_heap:
        f_current, g_current, current = heapq.heappop(open_heap)
        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        for neighbor, attrs in GRAPH.get(current, {}).items():
            tentative_g = g_current + edge_cost_minutes(attrs)
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_neighbor = tentative_g + heuristic_time_min(neighbor, goal)
                heapq.heappush(open_heap, (f_neighbor, tentative_g, neighbor))

    return None


def route_breakdown(path):
    total_distance = 0.0
    total_traffic = 0.0
    total_weather = 0.0
    compounded_risk_effect = 0.0  # additional minutes due to risk
    total_time = 0.0

    legs = []
    for i in range(len(path) - 1):
        a, b = path[i], path[i + 1]
        edge = GRAPH[a][b]
        dist = edge["distance_km"]
        traffic = edge.get("traffic_min", 0)
        weather = edge.get("weather_min", 0)
        risk = edge.get("risk", 1.0)

        base_time = dist / KM_PER_MIN
        time_with_delays = base_time + traffic + weather
        time_with_risk = time_with_delays * risk

        total_distance += dist
        total_traffic += traffic
        total_weather += weather
        compounded_risk_effect += time_with_risk - time_with_delays
        total_time += time_with_risk

        legs.append({
            "from": a,
            "to": b,
            "distance_km": round(dist, 2),
            "traffic_min": round(traffic, 2),
            "weather_min": round(weather, 2),
            "risk": round(risk, 3),
            "estimated_time_min": round(time_with_risk, 2),
        })

    return {
        "total_distance_km": round(total_distance, 2),
        "total_traffic_min": round(total_traffic, 2),
        "total_weather_min": round(total_weather, 2),
        "risk_extra_time_min": round(compounded_risk_effect, 2),
        "estimated_total_time_min": round(total_time, 2),
        "legs": legs,
    }


@app.get("/api/cities")
def get_cities():
    return jsonify(sorted(list(CITIES.keys())))


@app.post("/api/route")
def get_route():
    data = request.get_json(silent=True) or {}
    start = data.get("start")
    end = data.get("end")

    if not start or not end:
        return jsonify({"error": "Missing 'start' or 'end'"}), 400
    if start == end:
        return jsonify({
            "path": [start],
            "breakdown": {
                "total_distance_km": 0,
                "total_traffic_min": 0,
                "total_weather_min": 0,
                "risk_extra_time_min": 0,
                "estimated_total_time_min": 0,
                "legs": []
            }
        })

    path = a_star_route(start, end)
    if not path:
        return jsonify({"error": "No route found"}), 404

    breakdown = route_breakdown(path)
    return jsonify({
        "path": path,
        "breakdown": breakdown
    })


@app.get("/api/city_coords")
def get_city_coords():
    # Returns mapping of city name to {lat, lon}
    return jsonify(CITIES)


@app.post("/api/update_weather")
def update_weather():
    # Iterate over all cities and update weather impacts on all connected edges
    summary = {}
    for city, coords in CITIES.items():
        lat, lon = coords["lat"], coords["lon"]
        info = get_weather_delay(city, lat, lon)
        condition = info.get("condition", "Unknown")
        delay = int(info.get("delay_min", 0))
        risk = float(info.get("risk", 1.0))

        summary[city] = {"condition": condition, "delay_min": delay, "risk": round(risk, 2)}

        # Update all edges from this city
        neighbors = list(GRAPH.get(city, {}).keys())
        for nb in neighbors:
            # Ensure reverse edge exists
            if nb not in GRAPH:
                GRAPH[nb] = {}
            if city not in GRAPH[nb]:
                # If reverse edge missing, mirror minimal details
                dist = GRAPH[city][nb].get("distance_km", 0)
                GRAPH[nb][city] = {
                    "distance_km": dist,
                    "traffic_min": GRAPH[city][nb].get("traffic_min", 0),
                    "weather_min": 0,
                    "risk": 1.0,
                }

            GRAPH[city][nb]["weather_min"] = delay
            GRAPH[city][nb]["risk"] = risk
            GRAPH[nb][city]["weather_min"] = delay
            GRAPH[nb][city]["risk"] = risk

    # Print for server logs and return to client
    print("Weather summary:", summary)
    return jsonify(summary)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
