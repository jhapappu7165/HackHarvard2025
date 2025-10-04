from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from datetime import datetime
import pytz

app = FastAPI(
    title="Weather (OpenMeteo) Service",
    description="Weather API service for Boston traffic management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Boston lat/lon
LAT = 42.3601
LON = -71.0589

@app.get("/weather/openmeteo_current")
async def get_current_weather_openmeteo():
    # open-meteo: “current_weather” endpoint
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&current_weather=true"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail="Weather API error")
        data = r.json()

    cw = data.get("current_weather", {})
    # The Open-Meteo current_weather object includes:
    #   - temperature (°C)
    #   - windspeed (km/h) or similar
    #   - wind direction
    #   - time (ISO string)
    # It does *not* always include precipitation probability directly; you might get that in forecast.
    normalized = {
        "timestamp": cw.get("time"),
        "temperature_c": cw.get("temperature"),
        "windspeed": cw.get("windspeed"),
        "winddirection": cw.get("winddirection"),
        # For rain / precipitation, you’ll need the forecast endpoint
    }
    return normalized

@app.get("/weather/openmeteo_forecast")
async def get_forecast_openmeteo():
    # hourly forecast with precipitation probability, etc.
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={LAT}&longitude={LON}"
        f"&hourly=precipitation_probability,temperature_2m,weathercode,windspeed_10m"
        f"&forecast_days=1"
    )
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=500, detail="Weather API error")
        data = r.json()

    # data["hourly"] will contain arrays for each field
    h = data.get("hourly", {})
    times = h.get("time", [])
    precip_probs = h.get("precipitation_probability", [])
    temps = h.get("temperature_2m", [])
    wind_speeds = h.get("windspeed_10m", [])
    weathercodes = h.get("weathercode", [])

    results = []
    for i, t in enumerate(times):
        results.append({
            "timestamp": t,
            "temperature_c": temps[i] if i < len(temps) else None,
            "rain_prob": precip_probs[i] if i < len(precip_probs) else None,
            "wind_speed": wind_speeds[i] if i < len(wind_speeds) else None,
            "weathercode": weathercodes[i] if i < len(weathercodes) else None
        })
    return results

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "weather", "timestamp": datetime.now(pytz.UTC).isoformat()}

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Weather API",
        "version": "1.0.0",
        "description": "OpenMeteo weather service for Boston traffic management",
        "endpoints": [
            "/weather/openmeteo_current",
            "/weather/openmeteo_forecast",
            "/health"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=True)
