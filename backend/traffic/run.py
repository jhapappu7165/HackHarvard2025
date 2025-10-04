# (base) pappu@Aquaman:~/HackHarvard2025/traffic$ curl http://localhost:8000/api/traffic/data/1/14:00-15:00
# {"detail":"Intersection 1 not found"}(base) pappu@Aquaman:~/HackHarvard2025/traffic$ 

#{"analysis":{"intersection_id":"MASS_AVE_MAGAZINE_ST","time_period":{"start_time":"14:00","end_time":"15:00","duration_minutes":60},"analysis_timestamp":"2025-10-04T02:23:25.089798","bottlenecks":[],"traffic_volume_analysis":{"mass_ave_northbound":{"total_volume":83,"movement_distribution":{"thru":55.42168674698795,"left":44.57831325301205,"right":0.0,"u_turn":0.0},"primary_movement":{"movement":"thru","volume":46,"percentage":55.42168674698795},"efficiency_score":60,"optimization_potential":"medium"},"mass_ave_southbound":{"total_volume":88,"movement_distribution":{"thru":78.4090909090909,"left":0.0,"right":21.59090909090909,"u_turn":0.0},"primary_movement":{"movement":"thru","volume":69,"percentage":78.4090909090909},"efficiency_score":45,"optimization_potential":"medium"},"magazine_st_eastbound":{"total_volume":51,"movement_distribution":{"thru":0.0,"left":45.09803921568628,"right":54.90196078431373,"u_turn":0.0},"primary_movement":{"movement":"right","volume":28,"percentage":54.90196078431373},"efficiency_score":60,"optimization_potential":"medium"},"driveway_westbound":{"total_volume":0,"movement_distribution":{"thru":0,"left":0,"right":0,"u_turn":0},"primary_movement":{"movement":"thru","volume":0,"percentage":0},"efficiency_score":100,"optimization_potential":"low"}},"optimization_opportunities":[{"street":"mass_ave_northbound","movement":"right","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"},{"street":"mass_ave_southbound","movement":"left","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"},{"street":"magazine_st_eastbound","movement":"thru","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"},{"street":"driveway_westbound","movement":"thru","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"},{"street":"driveway_westbound","movement":"left","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"},{"street":"driveway_westbound","movement":"right","opportunity":"Unused movement - can optimize signal timing","impact":"Reduce signal cycle time"}],"performance_metrics":{"total_volume":222,"average_delay_seconds":111.0,"throughput_vph":888,"efficiency_score":65,"level_of_service":"F","optimization_potential":"high"}}}

# # (base) pappu@Aquaman:~/HackHarvard2025/traffic$ curl -X POST http://localhost:8000/api/traffic/recommendations \
#   -H "Content-Type: application/json" \
#   -d '{
#     "intersection_id": "MASS_AVE_MAGAZINE_ST",
#     "time_period": {
#       "start_time": "14:00",
#       "end_time": "15:00",
#       "duration_minutes": 60
#     },
#     "street_data": {
#       "mass_ave_northbound": {"thru": 46, "left": 37, "right": 0, "u_turn": 0},
#       "mass_ave_southbound": {"thru": 69, "left": 0, "right": 19, "u_turn": 0},
#       "magazine_st_eastbound": {"thru": 0, "left": 23, "right": 28, "u_turn": 0},
#   }'
# {"detail":"Time period 14:00-15:00 not found"}(base) pappu@Aquaman:~/HackHarv





#!/usr/bin/env python3
"""
Boston Daddy Traffic Backend - Startup Script
Quick start script for the traffic management system
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlite3
        import numpy
        import pandas
        print("✓ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment variables"""
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set - using demo mode")
        print("   Set GEMINI_API_KEY environment variable for full AI functionality")
    
    # Set default database path
    os.environ.setdefault("DATABASE_URL", "traffic_data.db")
    
    print("✓ Environment configured")

def create_database():
    """Create database if it doesn't exist"""
    db_path = os.getenv("DATABASE_URL", "traffic_data.db")
    
    if not os.path.exists(db_path):
        print(f"Creating database: {db_path}")
        # Database will be created when the app starts
    else:
        print(f"✓ Database exists: {db_path}")

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Boston Daddy Traffic Backend...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔍 Health check at: http://localhost:8000/api/traffic/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    print("🏙️  Boston Daddy - Traffic Management Backend")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found")
        print("   Please run this script from the traffic/ directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Create database
    create_database()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
