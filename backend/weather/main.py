from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import pytz

app = FastAPI(
    title="Weather (OpenMeteo) Service",
    description="Weather API service for Boston traffic and energy management",
    version="1.0.1"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Boston coordinates
LAT = 42.3601
LON = -71.0589

@app.get("/weather/openmeteo_current")
async def get_current_weather_openmeteo():
    """
    Current weather with comprehensive data:
    - is_day
    - cloudcover
    - shortwave_radiation (solar intensity)
    - temperature_2m
    - precipitation_probability (from current forecast hour)
    - rain
    - windspeed and direction
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current=is_day,cloudcover,shortwave_radiation,temperature_2m,precipitation,rain"
        f"&hourly=precipitation_probability"
        f"&forecast_days=1"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail="Weather API error")
        data = r.json()

    current = data.get("current", {})
    
    # Get current hour's precipitation probability from hourly data
    hourly = data.get("hourly", {})
    current_precip_prob = None
    if hourly.get("precipitation_probability"):
        # Take the first hour's precipitation probability as current
        current_precip_prob = hourly["precipitation_probability"][0]

    normalized = {
        "timestamp": current.get("time"),
        "is_day": current.get("is_day"),
        "cloudcover_percent": current.get("cloudcover"),
        "shortwave_radiation_wm2": current.get("shortwave_radiation"),
        "temperature_c": current.get("temperature_2m"),
        "precip_prob_percent": current_precip_prob,
        "rain_mm": current.get("rain"),
    }
    return normalized


@app.get("/weather/openmeteo_forecast")
async def get_forecast_openmeteo():
    """
    Hourly forecast with only essential fields:
    - is_day
    - cloudcover
    - shortwave_radiation (solar intensity)
    - temperature_2m
    - precipitation_probability
    - rain
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=is_day,cloudcover,shortwave_radiation,temperature_2m,precipitation_probability,rain"
        f"&forecast_days=1"
    )

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail="Weather API error")
        data = r.json()

    h = data.get("hourly", {})
    times = h.get("time", [])

    results = []
    for i, t in enumerate(times):
        results.append({
            "timestamp": t,
            "is_day": h.get("is_day", [None])[i] if i < len(h.get("is_day", [])) else None,
            "cloudcover_percent": h.get("cloudcover", [None])[i] if i < len(h.get("cloudcover", [])) else None,
            "shortwave_radiation_wm2": h.get("shortwave_radiation", [None])[i] if i < len(h.get("shortwave_radiation", [])) else None,
            "temperature_c": h.get("temperature_2m", [None])[i] if i < len(h.get("temperature_2m", [])) else None,
            "precip_prob_percent": h.get("precipitation_probability", [None])[i] if i < len(h.get("precipitation_probability", [])) else None,
            "rain_mm": h.get("rain", [None])[i] if i < len(h.get("rain", [])) else None,
        })

    return results


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "weather",
        "timestamp": datetime.now(pytz.UTC).isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Weather API",
        "version": "1.0.1",
        "description": "OpenMeteo weather service for Boston traffic and energy management",
        "endpoints": [
            "/weather/openmeteo_current",
            "/weather/openmeteo_forecast",
            "/health"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
