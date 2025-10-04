"""
UrbanMind AI - Traffic Management Backend
FastAPI application for intelligent traffic optimization
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import sqlite3
import json
from datetime import datetime, time
import asyncio
from traffic_analyzer import TrafficAnalyzer
from ai_recommendations import AIRecommendationEngine
from traffic_simulator import TrafficSimulator
from database import DatabaseManager

app = FastAPI(title="Boston Daddy", version="1.0.0")

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
traffic_analyzer = TrafficAnalyzer()
ai_engine = AIRecommendationEngine()
traffic_simulator = TrafficSimulator()

# Pydantic models
class TimePeriod(BaseModel):
    start_time: str
    end_time: str
    duration_minutes: int

class TrafficData(BaseModel):
    intersection_id: str
    time_period: TimePeriod
    street_data: Dict[str, Any]

class TrafficRecommendation(BaseModel):
    step: int
    action: str
    reasoning: str
    impact: str
    performance_improvement: str

class TrafficRule(BaseModel):
    street_name: str
    direction: str
    signal_timing: int
    cycle_length: int
    phase_duration: int

class SimulationResult(BaseModel):
    simulation_id: str
    current_performance: Dict[str, float]
    optimized_performance: Dict[str, float]
    improvements: Dict[str, str]

@app.on_event("startup")
async def startup_event():
    """Initialize database and load traffic data"""
    await db_manager.initialize()
    await traffic_analyzer.load_traffic_data()
    print("Boston Daddy backend initialized successfully")

@app.get("/")
async def root():
    return {"message": "Boston Daddy", "status": "running"}

@app.get("/api/traffic/intersections")
async def get_intersections():
    """Get all available intersections"""
    try:
        intersections = await db_manager.get_intersections()
        return {"intersections": intersections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/time-periods/{intersection_id}")
async def get_time_periods(intersection_id: str):
    """Get available time periods for an intersection"""
    try:
        periods = await db_manager.get_time_periods(intersection_id)
        return {"time_periods": periods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/data/{intersection_id}/{time_period_id}")
async def get_traffic_data(intersection_id: str, time_period_id: str):
    """Get traffic data for specific intersection and time period"""
    try:
        # Convert string intersection_id to int if it's a number
        if intersection_id.isdigit():
            intersection_id = int(intersection_id)
        
        data = await traffic_analyzer.get_traffic_data(intersection_id, time_period_id)
        return {"traffic_data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/streets/{intersection_id}")
async def get_street_data(intersection_id: str):
    """Get street information for an intersection"""
    try:
        streets = await db_manager.get_streets(intersection_id)
        return {"streets": streets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/current-rules/{intersection_id}/{time_period_id}")
async def get_current_rules(intersection_id: str, time_period_id: str):
    """Get current traffic rules for intersection and time period"""
    try:
        rules = await db_manager.get_traffic_rules(intersection_id, time_period_id)
        return {"traffic_rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic/analyze")
async def analyze_traffic(request: TrafficData):
    """Analyze traffic patterns and identify bottlenecks"""
    try:
        analysis = await traffic_analyzer.analyze_traffic_patterns(
            request.intersection_id,
            request.time_period,
            request.street_data
        )
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic/recommendations")
async def get_ai_recommendations(request: TrafficData):
    """Get AI-powered traffic optimization recommendations"""
    try:
        # Handle intersection ID conversion
        intersection_id = request.intersection_id
        if intersection_id.isdigit():
            intersection_id = int(intersection_id)
        
        # Use the street_data directly from the request instead of fetching from database
        # This ensures we have the actual traffic data for analysis
        traffic_data_for_ai = {
            "street_data": request.street_data,
            "intersection_id": intersection_id,
            "time_period": request.time_period
        }
        
        # Generate AI recommendations
        recommendations = await ai_engine.generate_recommendations(
            intersection_id,
            traffic_data_for_ai,
            request.time_period
        )
        
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic/simulate")
async def simulate_traffic(request: TrafficData):
    """Simulate traffic flow with current and optimized rules"""
    try:
        # Get current rules
        current_rules = await db_manager.get_traffic_rules(
            request.intersection_id,
            request.time_period.start_time + "-" + request.time_period.end_time
        )
        
        # Generate optimized rules
        optimized_rules = await ai_engine.generate_optimized_rules(
            request.intersection_id,
            request.street_data,
            request.time_period
        )
        
        # Run simulation
        simulation_result = await traffic_simulator.simulate_traffic_flow(
            request.intersection_id,
            current_rules,
            optimized_rules,
            request.street_data
        )
        
        return {"simulation": simulation_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/traffic/apply-rules")
async def apply_traffic_rules(
    rules: List[TrafficRule], 
    intersection_id: str = None, 
    time_period_id: str = None
):
    """Apply optimized traffic rules"""
    try:
        # Handle both query parameters and body data
        if intersection_id is None or time_period_id is None:
            raise HTTPException(status_code=400, detail="intersection_id and time_period_id are required")
        
        # Convert to int if needed
        if intersection_id.isdigit():
            intersection_id = int(intersection_id)
        
        result = await db_manager.update_traffic_rules(
            intersection_id,
            time_period_id,
            [rule.dict() for rule in rules]
        )
        return {"status": "success", "applied_rules": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/performance/{intersection_id}")
async def get_performance_metrics(intersection_id: str):
    """Get performance metrics for an intersection"""
    try:
        metrics = await db_manager.get_performance_metrics(intersection_id)
        return {"performance_metrics": metrics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/traffic/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": "connected",
            "ai_engine": "ready",
            "traffic_simulator": "ready"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
