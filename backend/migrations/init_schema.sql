-- Boston Energy Insights Database Schema
-- Complete schema for energy, weather, traffic, and insights

-- ============================================
-- ENERGY TABLES
-- ============================================

-- Energy Buildings Table
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

-- Energy Readings Table
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

-- ============================================
-- WEATHER TABLES
-- ============================================

-- Weather Stations Table
CREATE TABLE IF NOT EXISTS weather_stations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Weather Data Table
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

-- ============================================
-- TRAFFIC TABLES
-- ============================================

-- Traffic Intersections Table
CREATE TABLE IF NOT EXISTS traffic_intersections (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    streets TEXT[] NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Traffic Data Table
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

-- ============================================
-- INSIGHTS TABLE
-- ============================================

-- Unified Insights Table (Cross-Domain)
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

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Energy indexes
CREATE INDEX IF NOT EXISTS idx_energy_readings_building ON energy_readings(building_id);
CREATE INDEX IF NOT EXISTS idx_energy_readings_date ON energy_readings(reading_date);
CREATE INDEX IF NOT EXISTS idx_energy_readings_fuel_type ON energy_readings(fuel_type);
CREATE INDEX IF NOT EXISTS idx_energy_readings_building_date ON energy_readings(building_id, reading_date);

-- Weather indexes
CREATE INDEX IF NOT EXISTS idx_weather_data_station ON weather_data(station_id);
CREATE INDEX IF NOT EXISTS idx_weather_data_date ON weather_data(reading_date);
CREATE INDEX IF NOT EXISTS idx_weather_data_station_date ON weather_data(station_id, reading_date);

-- Traffic indexes
CREATE INDEX IF NOT EXISTS idx_traffic_data_intersection ON traffic_data(intersection_id);
CREATE INDEX IF NOT EXISTS idx_traffic_data_timestamp ON traffic_data(reading_timestamp);
CREATE INDEX IF NOT EXISTS idx_traffic_data_time_period ON traffic_data(time_period);
CREATE INDEX IF NOT EXISTS idx_traffic_data_intersection_time ON traffic_data(intersection_id, reading_timestamp);

-- Insights indexes
CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_entity ON insights(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_insights_priority ON insights(priority);
CREATE INDEX IF NOT EXISTS idx_insights_created ON insights(created_at DESC);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Latest energy readings per building
CREATE OR REPLACE VIEW latest_energy_readings AS
SELECT DISTINCT ON (building_id)
    building_id,
    reading_date,
    fuel_type,
    usage,
    cost
FROM energy_readings
ORDER BY building_id, reading_date DESC;

-- View: Monthly energy summary by building
CREATE OR REPLACE VIEW monthly_energy_summary AS
SELECT 
    building_id,
    DATE_TRUNC('month', reading_date) as month,
    fuel_type,
    SUM(usage) as total_usage,
    SUM(cost) as total_cost,
    AVG(usage) as avg_usage,
    COUNT(*) as reading_count
FROM energy_readings
GROUP BY building_id, DATE_TRUNC('month', reading_date), fuel_type
ORDER BY building_id, month DESC;

-- View: High priority insights summary
CREATE OR REPLACE VIEW high_priority_insights AS
SELECT 
    i.*,
    CASE 
        WHEN i.entity_type = 'building' THEN eb.name
        WHEN i.entity_type = 'intersection' THEN ti.name
        WHEN i.entity_type = 'station' THEN ws.name
        ELSE 'System-wide'
    END as entity_name
FROM insights i
LEFT JOIN energy_buildings eb ON i.entity_type = 'building' AND i.entity_id = eb.id
LEFT JOIN traffic_intersections ti ON i.entity_type = 'intersection' AND i.entity_id = ti.id
LEFT JOIN weather_stations ws ON i.entity_type = 'station' AND i.entity_id = ws.id
WHERE i.priority IN ('high', 'critical')
ORDER BY 
    CASE i.priority 
        WHEN 'critical' THEN 1 
        WHEN 'high' THEN 2 
        ELSE 3 
    END,
    i.created_at DESC;

-- View: Building energy performance
CREATE OR REPLACE VIEW building_energy_performance AS
SELECT 
    eb.id,
    eb.name,
    eb.category,
    eb.square_feet,
    SUM(er.usage) as total_usage,
    SUM(er.cost) as total_cost,
    SUM(er.usage) / NULLIF(eb.square_feet, 0) as usage_per_sqft,
    COUNT(DISTINCT er.reading_date) as reading_days
FROM energy_buildings eb
LEFT JOIN energy_readings er ON eb.id = er.building_id
GROUP BY eb.id, eb.name, eb.category, eb.square_feet
ORDER BY usage_per_sqft DESC;

-- View: Traffic congestion summary
CREATE OR REPLACE VIEW traffic_congestion_summary AS
SELECT 
    ti.id as intersection_id,
    ti.name as intersection_name,
    td.time_period,
    AVG(td.total_vehicle_count) as avg_vehicle_count,
    AVG(td.average_speed) as avg_speed,
    COUNT(*) as reading_count,
    MODE() WITHIN GROUP (ORDER BY td.congestion_level) as most_common_congestion
FROM traffic_intersections ti
JOIN traffic_data td ON ti.id = td.intersection_id
GROUP BY ti.id, ti.name, td.time_period
ORDER BY ti.name, td.time_period;

-- View: Weather impact summary
CREATE OR REPLACE VIEW weather_impact_summary AS
SELECT 
    DATE_TRUNC('month', wd.reading_date) as month,
    AVG(wd.temp_avg) as avg_temperature,
    SUM(wd.heating_degree_days) as total_hdd,
    SUM(wd.cooling_degree_days) as total_cdd,
    SUM(wd.precipitation) as total_precipitation,
    AVG(wd.humidity) as avg_humidity
FROM weather_data wd
GROUP BY DATE_TRUNC('month', wd.reading_date)
ORDER BY month DESC;

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function: Calculate energy intensity for a building
CREATE OR REPLACE FUNCTION calculate_energy_intensity(
    p_building_id BIGINT,
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE(
    building_id BIGINT,
    total_usage DOUBLE PRECISION,
    total_cost DOUBLE PRECISION,
    intensity_kbtu_per_sqft DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        eb.id,
        SUM(er.usage) as total_usage,
        SUM(er.cost) as total_cost,
        (SUM(er.usage) * 3.412) / NULLIF(eb.square_feet, 0) as intensity_kbtu_per_sqft
    FROM energy_buildings eb
    JOIN energy_readings er ON eb.id = er.building_id
    WHERE eb.id = p_building_id
        AND er.reading_date BETWEEN p_start_date AND p_end_date
    GROUP BY eb.id, eb.square_feet;
END;
$$ LANGUAGE plpgsql;

-- Function: Get nearby intersections for a building
CREATE OR REPLACE FUNCTION get_nearby_intersections(
    p_building_id BIGINT,
    p_radius_miles DOUBLE PRECISION DEFAULT 0.5
)
RETURNS TABLE(
    intersection_id BIGINT,
    intersection_name TEXT,
    distance_miles DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ti.id,
        ti.name,
        (
            3959 * acos(
                cos(radians(eb.latitude)) * 
                cos(radians(ti.latitude)) * 
                cos(radians(ti.longitude) - radians(eb.longitude)) + 
                sin(radians(eb.latitude)) * 
                sin(radians(ti.latitude))
            )
        ) as distance_miles
    FROM traffic_intersections ti
    CROSS JOIN energy_buildings eb
    WHERE eb.id = p_building_id
        AND (
            3959 * acos(
                cos(radians(eb.latitude)) * 
                cos(radians(ti.latitude)) * 
                cos(radians(ti.longitude) - radians(eb.longitude)) + 
                sin(radians(eb.latitude)) * 
                sin(radians(ti.latitude))
            )
        ) <= p_radius_miles
    ORDER BY distance_miles;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- INITIAL DATA CONSTRAINTS
-- ============================================

-- Ensure valid coordinates (Boston area)
ALTER TABLE energy_buildings ADD CONSTRAINT valid_building_coords 
    CHECK (latitude BETWEEN 42.2 AND 42.4 AND longitude BETWEEN -71.2 AND -70.9);

ALTER TABLE weather_stations ADD CONSTRAINT valid_station_coords 
    CHECK (latitude BETWEEN 42.2 AND 42.4 AND longitude BETWEEN -71.2 AND -70.9);

ALTER TABLE traffic_intersections ADD CONSTRAINT valid_intersection_coords 
    CHECK (latitude BETWEEN 42.2 AND 42.4 AND longitude BETWEEN -71.2 AND -70.9);

-- Ensure positive values
ALTER TABLE energy_readings ADD CONSTRAINT positive_usage CHECK (usage >= 0);
ALTER TABLE energy_readings ADD CONSTRAINT positive_cost CHECK (cost >= 0);
ALTER TABLE traffic_data ADD CONSTRAINT positive_vehicle_count CHECK (total_vehicle_count >= 0);
ALTER TABLE traffic_data ADD CONSTRAINT positive_speed CHECK (average_speed >= 0);

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE energy_buildings IS 'Municipal buildings with energy consumption data';
COMMENT ON TABLE energy_readings IS 'Energy consumption readings by fuel type';
COMMENT ON TABLE weather_stations IS 'Weather monitoring stations';
COMMENT ON TABLE weather_data IS 'Daily weather readings including degree days';
COMMENT ON TABLE traffic_intersections IS 'Traffic monitoring intersections';
COMMENT ON TABLE traffic_data IS 'Traffic volume and speed data';
COMMENT ON TABLE insights IS 'AI-generated insights from cross-domain analysis';

COMMENT ON COLUMN energy_readings.usage IS 'Energy usage in kWh or equivalent units';
COMMENT ON COLUMN energy_readings.cost IS 'Cost in USD';
COMMENT ON COLUMN weather_data.heating_degree_days IS 'Heating degree days (base 65°F)';
COMMENT ON COLUMN weather_data.cooling_degree_days IS 'Cooling degree days (base 65°F)';
COMMENT ON COLUMN insights.confidence_score IS 'Confidence score 0-100';
COMMENT ON COLUMN insights.data_sources IS 'Array of data sources used (energy, weather, traffic)';

-- ============================================
-- GRANT PERMISSIONS (adjust as needed)
-- ============================================

-- Grant read access to anon role (for public API)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

-- Grant full access to authenticated users
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ============================================
-- SEED DATA (Optional - for testing)
-- ============================================

-- Note: Actual seed data will be generated by the data generators
-- This is just a placeholder to show the structure

-- Example: Insert a sample building (optional)
-- INSERT INTO energy_buildings (name, address, city, latitude, longitude, square_feet, category, year_built)
-- VALUES ('Sample City Hall', '123 Main St', 'Boston', 42.3601, -71.0589, 50000, 'Administration', 1980);