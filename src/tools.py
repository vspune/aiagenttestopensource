"""
tools.py
--------
All tool definitions for the Weather Agent POC.
Uses Open-Meteo (free, no API key) + Geocoding API.

Tools:
  1. get_weather(city)                  → current weather
  2. get_forecast(city, days)           → N-day forecast
  3. convert_temperature(value, unit)   → °C ↔ °F ↔ K
  4. get_location_info(city)            → city metadata
"""

import requests

# ─────────────────────────────────────────────────────────
# INTERNAL HELPER — Geocoding (city name → lat/lon)
# ─────────────────────────────────────────────────────────
def _geocode(city: str) -> dict:
    """Convert city name to latitude/longitude using Open-Meteo Geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("results"):
        raise ValueError(f"City not found: '{city}'. Please check the city name.")

    r = data["results"][0]
    return {
        "name":      r.get("name"),
        "country":   r.get("country"),
        "latitude":  r.get("latitude"),
        "longitude": r.get("longitude"),
        "timezone":  r.get("timezone"),
        "population":r.get("population"),
    }


# ─────────────────────────────────────────────────────────
# TOOL 1 — get_weather
# ─────────────────────────────────────────────────────────
def get_weather(city: str) -> dict:
    """
    Fetch current weather for a given city.

    Args:
        city (str): Name of the city e.g. "London"

    Returns:
        dict: temperature_c, feels_like_c, humidity_pct,
              wind_speed_kmh, description, city, country
    
    Raises:
        ValueError: If city is not found
        requests.RequestException: If API call fails
    """
    location = _geocode(city)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":   location["latitude"],
        "longitude":  location["longitude"],
        "current":    "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
        "timezone":   "auto",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    current = data["current"]

    # WMO weather code → human description
    weather_code = current.get("weather_code", 0)
    description  = _wmo_description(weather_code)

    return {
        "city":            location["name"],
        "country":         location["country"],
        "temperature_c":   current["temperature_2m"],
        "feels_like_c":    current["apparent_temperature"],
        "humidity_pct":    current["relative_humidity_2m"],
        "wind_speed_kmh":  current["wind_speed_10m"],
        "description":     description,
        "timezone":        data.get("timezone"),
    }


# ─────────────────────────────────────────────────────────
# TOOL 2 — get_forecast
# ─────────────────────────────────────────────────────────
def get_forecast(city: str, days: int = 3) -> dict:
    """
    Fetch N-day weather forecast for a city.

    Args:
        city (str): City name e.g. "Tokyo"
        days (int): Number of forecast days (1–7)

    Returns:
        dict: city, country, forecast list with date,
              max/min temp, precipitation, description
    
    Raises:
        ValueError: If city not found or days out of range
    """
    if not 1 <= days <= 7:
        raise ValueError(f"Days must be between 1 and 7. Got: {days}")

    location = _geocode(city)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude":     location["latitude"],
        "longitude":    location["longitude"],
        "daily":        "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
        "timezone":     "auto",
        "forecast_days": days,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    daily = data["daily"]

    forecast = []
    for i in range(days):
        forecast.append({
            "date":          daily["time"][i],
            "max_temp_c":    daily["temperature_2m_max"][i],
            "min_temp_c":    daily["temperature_2m_min"][i],
            "precipitation": daily["precipitation_sum"][i],
            "description":   _wmo_description(daily["weather_code"][i]),
        })

    return {
        "city":     location["name"],
        "country":  location["country"],
        "days":     days,
        "forecast": forecast,
    }


# ─────────────────────────────────────────────────────────
# TOOL 3 — convert_temperature
# ─────────────────────────────────────────────────────────
def convert_temperature(value: float, from_unit: str, to_unit: str) -> dict:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.

    Args:
        value     (float): Temperature value to convert
        from_unit (str):   Source unit — 'C', 'F', or 'K'
        to_unit   (str):   Target unit — 'C', 'F', or 'K'

    Returns:
        dict: original_value, from_unit, converted_value, to_unit, formula

    Raises:
        ValueError: If units are invalid
    """
    from_unit = from_unit.upper().strip()
    to_unit   = to_unit.upper().strip()
    valid     = {"C", "F", "K"}

    if from_unit not in valid or to_unit not in valid:
        raise ValueError(f"Invalid unit. Use one of: C, F, K. Got: '{from_unit}', '{to_unit}'")

    # Convert to Celsius first
    if from_unit == "C":
        celsius = value
    elif from_unit == "F":
        celsius = (value - 32) * 5 / 9
    else:  # K
        celsius = value - 273.15

    # Celsius → target
    if to_unit == "C":
        result  = celsius
        formula = f"{value}°{from_unit} → {result:.2f}°C"
    elif to_unit == "F":
        result  = (celsius * 9 / 5) + 32
        formula = f"{value}°{from_unit} → {result:.2f}°F"
    else:  # K
        result  = celsius + 273.15
        formula = f"{value}°{from_unit} → {result:.2f}K"

    return {
        "original_value":  value,
        "from_unit":       from_unit,
        "converted_value": round(result, 2),
        "to_unit":         to_unit,
        "formula":         formula,
    }


# ─────────────────────────────────────────────────────────
# TOOL 4 — get_location_info
# ─────────────────────────────────────────────────────────
def get_location_info(city: str) -> dict:
    """
    Get metadata about a city/location.

    Args:
        city (str): City name e.g. "Paris"

    Returns:
        dict: name, country, latitude, longitude,
              timezone, population, elevation

    Raises:
        ValueError: If city is not found
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("results"):
        raise ValueError(f"Location not found: '{city}'. Please verify the city name.")

    r = data["results"][0]
    return {
        "name":       r.get("name"),
        "country":    r.get("country"),
        "country_code": r.get("country_code"),
        "latitude":   r.get("latitude"),
        "longitude":  r.get("longitude"),
        "elevation":  r.get("elevation"),
        "timezone":   r.get("timezone"),
        "population": r.get("population"),
        "admin1":     r.get("admin1"),   # State / Province
    }


# ─────────────────────────────────────────────────────────
# HELPER — WMO Weather Code → Description
# ─────────────────────────────────────────────────────────
def _wmo_description(code: int) -> str:
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        77: "Snow grains",
        80: "Slight showers", 81: "Moderate showers", 82: "Violent showers",
        85: "Slight snow showers", 86: "Heavy snow showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail",
    }
    return mapping.get(code, f"Unknown (code {code})")


# ─────────────────────────────────────────────────────────
# TOOL REGISTRY — Used by Agent to discover tools
# ─────────────────────────────────────────────────────────
TOOL_REGISTRY = {
    "get_weather":          get_weather,
    "get_forecast":         get_forecast,
    "convert_temperature":  convert_temperature,
    "get_location_info":    get_location_info,
}

# Tool schemas for OLLAMA function-calling format
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name":        "get_weather",
            "description": "Get the current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name e.g. London"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "get_forecast",
            "description": "Get weather forecast for next N days for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"},
                    "days": {"type": "integer", "description": "Number of days (1-7)", "default": 3},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "convert_temperature",
            "description": "Convert temperature between Celsius (C), Fahrenheit (F), and Kelvin (K)",
            "parameters": {
                "type": "object",
                "properties": {
                    "value":     {"type": "number",  "description": "Temperature value"},
                    "from_unit": {"type": "string",  "description": "Source unit: C, F, or K"},
                    "to_unit":   {"type": "string",  "description": "Target unit: C, F, or K"},
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name":        "get_location_info",
            "description": "Get geographic and demographic info about a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name e.g. Paris"}
                },
                "required": ["city"],
            },
        },
    },
]
