import os
import math
import requests
from typing import Dict, Any, Tuple

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes the great-circle distance between two points in kilometers.
    """
    # Radius of the Earth in km
    R = 6371.0
    
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distance in km
    distance = R * c
    return round(distance, 3)

def get_route_details(lat1: float, lon1: float, lat2: float, lon2: float) -> Tuple[float, float]:
    """
    Calculates the real road distance (km) and estimated travel time (min) between two locations
    using the public OpenStreetMap OSRM API. Falls back to Haversine calculation if offline.
    
    Returns:
        (distance_km, travel_time_min)
    """
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=false"
    
    try:
        # 3 seconds timeout to avoid blocking the application
        response = requests.get(url, timeout=3.0)
        if response.status_code == 200:
            result = response.json()
            if "routes" in result and len(result["routes"]) > 0:
                route = result["routes"][0]
                distance_meters = route["distance"]
                duration_seconds = route["duration"]
                
                distance_km = round(distance_meters / 1000.0, 2)
                travel_time_min = round(duration_seconds / 60.0, 1)
                
                print(f"OSRM Route Success: {distance_km} km in {travel_time_min} mins")
                return distance_km, travel_time_min
    except Exception as e:
        print(f"OSRM Routing failed ({e}). Using Haversine formula fallback.")
        
    # Haversine fallback
    h_dist = haversine_distance(lat1, lon1, lat2, lon2)
    # Add a circuitry factor of 1.3 to represent real city road networks compared to straight line
    road_dist = round(h_dist * 1.3, 2)
    # Standard city driving speed assumption: 25 km/h
    avg_speed_kph = 25.0
    travel_time = round((road_dist / avg_speed_kph) * 60.0, 1)
    
    print(f"Haversine Fallback Route: {road_dist} km in {travel_time} mins")
    return road_dist, travel_time

def get_weather_details(lat: float, lon: float, api_key: str = None) -> Dict[str, Any]:
    """
    Fetches real weather details using OpenWeatherMap API if a key is provided,
    otherwise generates highly realistic simulated weather conditions.
    
    Returns:
        Dictionary containing Temperature_C, Weather_Condition, Visibility_km, Rain_Severity
    """
    # Use environment api key if available
    api_key = api_key or os.environ.get("OPENWEATHER_API_KEY")
    
    if api_key:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        try:
            response = requests.get(url, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                weather_main = data["weather"][0]["main"]
                visibility = data.get("visibility", 10000) / 1000.0  # Convert meters to km
                
                # Map OpenWeather main categories to our weather scale
                condition = "Sunny"
                rain_sev = 0.0
                
                if "Rain" in weather_main or "Drizzle" in weather_main:
                    condition = "Rainy"
                    rain_sev = 3.0
                elif "Thunderstorm" in weather_main or "Extreme" in weather_main:
                    condition = "Storm"
                    rain_sev = 4.0
                elif "Cloud" in weather_main:
                    condition = "Cloudy"
                    rain_sev = 1.0
                elif "Mist" in weather_main or "Fog" in weather_main or "Haze" in weather_main:
                    condition = "Cloudy"  # Fog/Cloudy
                    visibility = min(visibility, 2.0)
                    
                print(f"OpenWeather OWM Success: Temp={temp}°C, Condition={condition}")
                return {
                    "Temperature_C": temp,
                    "Weather_Condition": condition,
                    "Visibility_km": visibility,
                    "Rain_Severity": rain_sev
                }
        except Exception as e:
            print(f"OpenWeatherMap API request failed ({e}). Using simulated weather.")
            
    # Simulated weather generator (deterministic based on coordinates to make it consistent for the same restaurant)
    # Simple hash of coordinates to generate stable weather
    coord_sum = int(abs(lat * 100) + abs(lon * 100))
    rand_val = coord_sum % 100
    
    if rand_val < 50:
        condition = "Sunny"
        temp = round(24.0 + (rand_val % 8), 1)
        visibility = 10.0
        rain_sev = 0.0
    elif rand_val < 75:
        condition = "Cloudy"
        temp = round(18.0 + (rand_val % 6), 1)
        visibility = 8.0
        rain_sev = 1.0
    elif rand_val < 92:
        condition = "Rainy"
        temp = round(14.0 + (rand_val % 5), 1)
        visibility = 4.5
        rain_sev = 3.0
    else:
        condition = "Storm"
        temp = round(12.0 + (rand_val % 4), 1)
        visibility = 1.5
        rain_sev = 4.0
        
    return {
        "Temperature_C": temp,
        "Weather_Condition": condition,
        "Visibility_km": visibility,
        "Rain_Severity": rain_sev
    }

if __name__ == "__main__":
    # Test route details
    # Portland, OR coords test
    dist, duration = get_route_details(45.5152, -122.6784, 45.5230, -122.6678)
    print(f"Test Route: {dist} km, {duration} mins")
    
    # Test weather details
    weather = get_weather_details(45.5152, -122.6784)
    print(f"Test Weather: {weather}")
