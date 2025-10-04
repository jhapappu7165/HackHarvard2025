from utils.supabase_client import SupabaseClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    """Run database migrations"""
    try:
        db = SupabaseClient().get_client()
        
        # Read the SQL file
        with open('migrations/init_schema.sql', 'r') as f:
            sql_content = f.read()
        
        # Split into individual statements (Supabase API limitation)
        # We'll execute the most critical CREATE TABLE statements
        
        tables_sql = [
            # Energy Buildings
            """
            CREATE TABLE IF NOT EXISTS energy_buildings (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                address TEXT,
                city TEXT DEFAULT 'Boston',
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                square_feet INTEGER NOT NULL,
                category TEXT NOT NULL,
                year_built INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            # Energy Readings
            """
            CREATE TABLE IF NOT EXISTS energy_readings (
                id BIGSERIAL PRIMARY KEY,
                building_id BIGINT NOT NULL REFERENCES energy_buildings(id) ON DELETE CASCADE,
                reading_date DATE NOT NULL,
                fuel_type TEXT NOT NULL,
                usage DOUBLE PRECISION NOT NULL,
                cost DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT valid_fuel_type CHECK (fuel_type IN ('electricity', 'natural_gas', 'oil', 'propane'))
            );
            """,
            
            # Weather Stations
            """
            CREATE TABLE IF NOT EXISTS weather_stations (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            # Weather Data
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id BIGSERIAL PRIMARY KEY,
                station_id BIGINT NOT NULL REFERENCES weather_stations(id) ON DELETE CASCADE,
                reading_date DATE NOT NULL,
                temp_avg DOUBLE PRECISION NOT NULL,
                temp_min DOUBLE PRECISION NOT NULL,
                temp_max DOUBLE PRECISION NOT NULL,
                heating_degree_days INTEGER NOT NULL DEFAULT 0,
                cooling_degree_days INTEGER NOT NULL DEFAULT 0,
                precipitation DOUBLE PRECISION NOT NULL DEFAULT 0,
                wind_speed DOUBLE PRECISION NOT NULL DEFAULT 0,
                humidity DOUBLE PRECISION NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            # Traffic Intersections
            """
            CREATE TABLE IF NOT EXISTS traffic_intersections (
                id BIGSERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                latitude DOUBLE PRECISION NOT NULL,
                longitude DOUBLE PRECISION NOT NULL,
                streets TEXT[] NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            
            # Traffic Data
            """
            CREATE TABLE IF NOT EXISTS traffic_data (
                id BIGSERIAL PRIMARY KEY,
                intersection_id BIGINT NOT NULL REFERENCES traffic_intersections(id) ON DELETE CASCADE,
                reading_timestamp TIMESTAMP NOT NULL,
                time_period TEXT NOT NULL,
                total_vehicle_count INTEGER NOT NULL DEFAULT 0,
                average_speed DOUBLE PRECISION NOT NULL DEFAULT 0,
                congestion_level TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT valid_time_period CHECK (time_period IN ('morning_peak', 'midday', 'afternoon_peak', 'evening', 'night')),
                CONSTRAINT valid_congestion CHECK (congestion_level IN ('low', 'moderate', 'high', 'severe'))
            );
            """,
            
            # Insights
            """
            CREATE TABLE IF NOT EXISTS insights (
                id BIGSERIAL PRIMARY KEY,
                insight_type TEXT NOT NULL,
                entity_id BIGINT,
                entity_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                category TEXT,
                potential_savings DOUBLE PRECISION,
                confidence_score DOUBLE PRECISION,
                data_sources TEXT[],
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT valid_insight_type CHECK (insight_type IN ('energy', 'weather', 'traffic', 'cross_domain')),
                CONSTRAINT valid_entity_type CHECK (entity_type IN ('building', 'intersection', 'station', 'city', 'system')),
                CONSTRAINT valid_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
                CONSTRAINT valid_confidence CHECK (confidence_score >= 0 AND confidence_score <= 100)
            );
            """
        ]
        
        logger.info("Creating database tables...")
        
        # Note: Supabase REST API doesn't directly support DDL
        # You need to run this in the Supabase SQL Editor
        logger.warning("=" * 60)
        logger.warning("IMPORTANT: Please run the SQL manually in Supabase!")
        logger.warning("=" * 60)
        logger.warning("\n1. Go to: https://supabase.com/dashboard")
        logger.warning("2. Select your project")
        logger.warning("3. Click 'SQL Editor'")
        logger.warning("4. Copy the contents of 'migrations/init_schema.sql'")
        logger.warning("5. Paste and run in the SQL Editor")
        logger.warning("=" * 60)
        
        print("\n\nSQL TO RUN:\n")
        print(sql_content[:2000])  # Print first 2000 chars as preview
        print("\n... (see full SQL in migrations/init_schema.sql)")
        
    except Exception as e:
        logger.error(f"Migration error: {str(e)}")
        raise

if __name__ == '__main__':
    run_migrations()