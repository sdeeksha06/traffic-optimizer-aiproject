# Mock dataset with Telangana cities (coordinates) and road segments including distance (km),
# traffic delay (min), weather delay (min), and risk factor (multiplier).

# Cities in Telangana (approximate lat/lon)
CITIES = {
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Warangal": {"lat": 17.9689, "lon": 79.5941},
    "Nizamabad": {"lat": 18.6725, "lon": 78.0941},
    "Karimnagar": {"lat": 18.4386, "lon": 79.1288},
    "Khammam": {"lat": 17.2473, "lon": 80.1514},
    "Mahabubnagar": {"lat": 16.7425, "lon": 77.9860},
    "Nalgonda": {"lat": 17.0510, "lon": 79.2670},
    "Suryapet": {"lat": 17.1366, "lon": 79.6190},
    "Siddipet": {"lat": 18.1000, "lon": 78.8500},
    "Medak": {"lat": 17.7500, "lon": 78.2790},
}

# Undirected graph between Telangana cities. Distances are rough driving distances (km);
# traffic/weather/risk are mock values to demonstrate the routing algorithm.
GRAPH = {
    "Hyderabad": {
        "Medak": {"distance_km": 70, "traffic_min": 15, "weather_min": 0, "risk": 1.03},
        "Nizamabad": {"distance_km": 175, "traffic_min": 20, "weather_min": 2, "risk": 1.06},
        "Karimnagar": {"distance_km": 165, "traffic_min": 18, "weather_min": 1, "risk": 1.05},
        "Warangal": {"distance_km": 150, "traffic_min": 20, "weather_min": 2, "risk": 1.05},
        "Nalgonda": {"distance_km": 100, "traffic_min": 12, "weather_min": 1, "risk": 1.03},
        "Mahabubnagar": {"distance_km": 95, "traffic_min": 10, "weather_min": 0, "risk": 1.02},
        "Siddipet": {"distance_km": 100, "traffic_min": 14, "weather_min": 1, "risk": 1.04},
        "Suryapet": {"distance_km": 140, "traffic_min": 16, "weather_min": 1, "risk": 1.05},
        "Khammam": {"distance_km": 195, "traffic_min": 18, "weather_min": 2, "risk": 1.06},
    },
    "Medak": {
        "Hyderabad": {"distance_km": 70, "traffic_min": 12, "weather_min": 0, "risk": 1.03},
        "Siddipet": {"distance_km": 60, "traffic_min": 8, "weather_min": 0, "risk": 1.02},
        "Nizamabad": {"distance_km": 120, "traffic_min": 10, "weather_min": 1, "risk": 1.04},
    },
    "Siddipet": {
        "Medak": {"distance_km": 60, "traffic_min": 7, "weather_min": 0, "risk": 1.02},
        "Hyderabad": {"distance_km": 100, "traffic_min": 14, "weather_min": 1, "risk": 1.04},
        "Karimnagar": {"distance_km": 130, "traffic_min": 12, "weather_min": 1, "risk": 1.05},
    },
    "Nizamabad": {
        "Hyderabad": {"distance_km": 175, "traffic_min": 18, "weather_min": 2, "risk": 1.06},
        "Medak": {"distance_km": 120, "traffic_min": 10, "weather_min": 1, "risk": 1.04},
        "Karimnagar": {"distance_km": 130, "traffic_min": 15, "weather_min": 1, "risk": 1.06},
    },
    "Karimnagar": {
        "Nizamabad": {"distance_km": 130, "traffic_min": 14, "weather_min": 1, "risk": 1.05},
        "Hyderabad": {"distance_km": 165, "traffic_min": 16, "weather_min": 1, "risk": 1.05},
        "Warangal": {"distance_km": 90, "traffic_min": 10, "weather_min": 1, "risk": 1.03},
    },
    "Warangal": {
        "Karimnagar": {"distance_km": 90, "traffic_min": 9, "weather_min": 1, "risk": 1.03},
        "Hyderabad": {"distance_km": 150, "traffic_min": 18, "weather_min": 2, "risk": 1.05},
        "Suryapet": {"distance_km": 65, "traffic_min": 8, "weather_min": 0, "risk": 1.02},
        "Khammam": {"distance_km": 92, "traffic_min": 10, "weather_min": 1, "risk": 1.04},
    },
    "Suryapet": {
        "Warangal": {"distance_km": 65, "traffic_min": 7, "weather_min": 0, "risk": 1.02},
        "Hyderabad": {"distance_km": 140, "traffic_min": 15, "weather_min": 1, "risk": 1.05},
        "Nalgonda": {"distance_km": 60, "traffic_min": 8, "weather_min": 0, "risk": 1.03},
        "Khammam": {"distance_km": 110, "traffic_min": 12, "weather_min": 1, "risk": 1.05},
    },
    "Nalgonda": {
        "Hyderabad": {"distance_km": 100, "traffic_min": 10, "weather_min": 0, "risk": 1.03},
        "Suryapet": {"distance_km": 60, "traffic_min": 7, "weather_min": 0, "risk": 1.03},
        "Mahabubnagar": {"distance_km": 120, "traffic_min": 9, "weather_min": 1, "risk": 1.04},
    },
    "Mahabubnagar": {
        "Hyderabad": {"distance_km": 95, "traffic_min": 9, "weather_min": 0, "risk": 1.02},
        "Nalgonda": {"distance_km": 120, "traffic_min": 8, "weather_min": 1, "risk": 1.03},
    },
    "Khammam": {
        "Hyderabad": {"distance_km": 195, "traffic_min": 16, "weather_min": 2, "risk": 1.06},
        "Warangal": {"distance_km": 92, "traffic_min": 10, "weather_min": 1, "risk": 1.04},
        "Suryapet": {"distance_km": 110, "traffic_min": 12, "weather_min": 1, "risk": 1.05},
    },
}
