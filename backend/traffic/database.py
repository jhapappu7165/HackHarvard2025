"""
Database management for traffic data
SQLite database with optimized schema for traffic management
"""

import sqlite3
import json
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import os

class DatabaseManager:
    def __init__(self, db_path: str = "traffic_data.db"):
        self.db_path = db_path
        self.connection = None
    
    async def initialize(self):
        """Initialize database with required tables"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        
        # Create tables
        await self._create_tables()
        await self._insert_initial_data()
    
    async def _create_tables(self):
        """Create database tables"""
        cursor = self.connection.cursor()
        
        # Intersections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS intersections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT,
                coordinates TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Time periods table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_periods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration_minutes INTEGER,
                peak_status TEXT,
                traffic_volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id)
            )
        """)
        
        # Streets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS streets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                street_name TEXT NOT NULL,
                direction TEXT NOT NULL,
                coordinates TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id)
            )
        """)
        
        # Traffic data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                time_period_id INTEGER,
                street_id INTEGER,
                time_interval TEXT,
                vehicle_count INTEGER,
                movement_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id),
                FOREIGN KEY (time_period_id) REFERENCES time_periods(id),
                FOREIGN KEY (street_id) REFERENCES streets(id)
            )
        """)
        
        # Traffic rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                time_period_id INTEGER,
                street_name TEXT,
                direction TEXT,
                signal_timing INTEGER,
                cycle_length INTEGER,
                phase_duration INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id),
                FOREIGN KEY (time_period_id) REFERENCES time_periods(id)
            )
        """)
        
        # AI recommendations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                time_period_id INTEGER,
                recommendation_text TEXT,
                reasoning TEXT,
                performance_impact TEXT,
                implementation_steps TEXT,
                expected_improvement TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id),
                FOREIGN KEY (time_period_id) REFERENCES time_periods(id)
            )
        """)
        
        # Performance metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                time_period_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                metric_unit TEXT,
                measurement_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id),
                FOREIGN KEY (time_period_id) REFERENCES time_periods(id)
            )
        """)
        
        # Traffic simulations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_simulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                intersection_id INTEGER,
                time_period_id INTEGER,
                simulation_type TEXT,
                current_performance TEXT,
                optimized_performance TEXT,
                improvements TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (intersection_id) REFERENCES intersections(id),
                FOREIGN KEY (time_period_id) REFERENCES time_periods(id)
            )
        """)
        
        self.connection.commit()
    
    async def _insert_initial_data(self):
        """Insert initial traffic data"""
        cursor = self.connection.cursor()
        
        # Insert Mass Ave & Magazine St intersection
        cursor.execute("""
            INSERT OR IGNORE INTO intersections (id, name, location, coordinates)
            VALUES (1, 'Mass Ave & Magazine St', 'Boston, MA', '42.3505,-71.1053')
        """)
        
        # Insert streets
        streets = [
            (1, 1, 'Mass Ave', 'Northbound'),
            (2, 1, 'Mass Ave', 'Southbound'),
            (3, 1, 'Magazine St', 'Eastbound'),
            (4, 1, 'Driveway', 'Westbound')
        ]
        
        for street in streets:
            cursor.execute("""
                INSERT OR IGNORE INTO streets (id, intersection_id, street_name, direction)
                VALUES (?, ?, ?, ?)
            """, street)
        
        # Insert time periods (7 AM to 6 PM in 15-minute intervals)
        time_periods = []
        current_time = time(7, 0)
        end_time = time(18, 0)
        period_id = 1
        
        while current_time < end_time:
            next_minute = current_time.minute + 15
            if next_minute >= 60:
                next_time = time(current_time.hour + 1, next_minute - 60)
            else:
                next_time = time(current_time.hour, next_minute)
            
            time_periods.append((
                period_id, 1, 
                current_time.strftime("%H:%M"), 
                next_time.strftime("%H:%M"),
                15,
                'peak' if 7 <= current_time.hour <= 9 or 16 <= current_time.hour <= 18 else 'off-peak',
                0
            ))
            
            current_time = next_time
            period_id += 1
        
        for period in time_periods:
            cursor.execute("""
                INSERT OR IGNORE INTO time_periods 
                (id, intersection_id, start_time, end_time, duration_minutes, peak_status, traffic_volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, period)
        
        # Insert default traffic rules
        default_rules = [
            (1, 1, 1, 'Mass Ave', 'Northbound', 30, 90, 30),
            (2, 1, 1, 'Mass Ave', 'Southbound', 45, 90, 45),
            (3, 1, 1, 'Magazine St', 'Eastbound', 15, 90, 15),
            (4, 1, 1, 'Driveway', 'Westbound', 0, 90, 0)
        ]
        
        for rule in default_rules:
            cursor.execute("""
                INSERT OR IGNORE INTO traffic_rules 
                (id, intersection_id, time_period_id, street_name, direction, signal_timing, cycle_length, phase_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, rule)
        
        self.connection.commit()
    
    async def get_intersections(self) -> List[Dict[str, Any]]:
        """Get all intersections"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM intersections")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_time_periods(self, intersection_id: int) -> List[Dict[str, Any]]:
        """Get time periods for an intersection"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM time_periods 
            WHERE intersection_id = ? 
            ORDER BY start_time
        """, (intersection_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_streets(self, intersection_id: int) -> List[Dict[str, Any]]:
        """Get streets for an intersection"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM streets 
            WHERE intersection_id = ? 
            ORDER BY street_name, direction
        """, (intersection_id,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_traffic_data(self, intersection_id: int, time_period_id: int) -> List[Dict[str, Any]]:
        """Get traffic data for intersection and time period"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT td.*, s.street_name, s.direction, tp.start_time, tp.end_time
            FROM traffic_data td
            JOIN streets s ON td.street_id = s.id
            JOIN time_periods tp ON td.time_period_id = tp.id
            WHERE td.intersection_id = ? AND td.time_period_id = ?
            ORDER BY td.time_interval, s.street_name
        """, (intersection_id, time_period_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def get_traffic_rules(self, intersection_id: int, time_period_id: int) -> List[Dict[str, Any]]:
        """Get traffic rules for intersection and time period"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM traffic_rules 
            WHERE intersection_id = ? AND time_period_id = ? AND is_active = 1
            ORDER BY street_name, direction
        """, (intersection_id, time_period_id))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    async def update_traffic_rules(self, intersection_id: int, time_period_id: int, rules: List[Dict[str, Any]]) -> bool:
        """Update traffic rules"""
        cursor = self.connection.cursor()
        
        try:
            # Deactivate current rules
            cursor.execute("""
                UPDATE traffic_rules 
                SET is_active = 0 
                WHERE intersection_id = ? AND time_period_id = ?
            """, (intersection_id, time_period_id))
            
            # Insert new rules
            for rule in rules:
                cursor.execute("""
                    INSERT INTO traffic_rules 
                    (intersection_id, time_period_id, street_name, direction, 
                     signal_timing, cycle_length, phase_duration, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, (
                    intersection_id, time_period_id,
                    rule['street_name'], rule['direction'],
                    rule['signal_timing'], rule['cycle_length'], 
                    rule['phase_duration']
                ))
            
            self.connection.commit()
            return True
        except Exception as e:
            self.connection.rollback()
            raise e
    
    async def save_ai_recommendation(self, intersection_id: int, time_period_id: int, 
                                  recommendation: Dict[str, Any]) -> int:
        """Save AI recommendation"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO ai_recommendations 
            (intersection_id, time_period_id, recommendation_text, reasoning, 
             performance_impact, implementation_steps, expected_improvement)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            intersection_id, time_period_id,
            recommendation['text'],
            recommendation['reasoning'],
            recommendation['impact'],
            recommendation['steps'],
            recommendation['improvement']
        ))
        self.connection.commit()
        return cursor.lastrowid
    
    async def save_simulation_result(self, intersection_id: int, time_period_id: int, 
                                   simulation_data: Dict[str, Any]) -> int:
        """Save simulation result"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO traffic_simulations 
            (intersection_id, time_period_id, simulation_type, current_performance, 
             optimized_performance, improvements)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            intersection_id, time_period_id,
            simulation_data['type'],
            json.dumps(simulation_data['current']),
            json.dumps(simulation_data['optimized']),
            json.dumps(simulation_data['improvements'])
        ))
        self.connection.commit()
        return cursor.lastrowid
    
    async def get_performance_metrics(self, intersection_id: int) -> List[Dict[str, Any]]:
        """Get performance metrics for intersection"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM performance_metrics 
            WHERE intersection_id = ? 
            ORDER BY measurement_date DESC
        """, (intersection_id,))
        rows = cursor.fetchall()
        
        # If no data exists, generate sample metrics
        if not rows:
            return self._generate_sample_performance_metrics(intersection_id)
        
        return [dict(row) for row in rows]
    
    def _generate_sample_performance_metrics(self, intersection_id: int) -> List[Dict[str, Any]]:
        """Generate sample performance metrics for demo purposes"""
        from datetime import datetime, timedelta
        import random
        
        metrics = []
        base_date = datetime.now()
        
        for i in range(7):  # Last 7 days
            date = base_date - timedelta(days=i)
            
            # Generate realistic metrics
            avg_delay = random.uniform(15, 45)
            throughput = random.randint(800, 1200)
            efficiency = random.uniform(70, 95)
            level_of_service = random.choice(['B', 'C', 'D'])
            
            metric = {
                "id": i + 1,
                "intersection_id": intersection_id,
                "measurement_date": date.strftime("%Y-%m-%d"),
                "avg_delay_seconds": round(avg_delay, 1),
                "throughput_vph": throughput,
                "efficiency_score": round(efficiency, 1),
                "level_of_service": level_of_service,
                "peak_hour_volume": random.randint(400, 600),
                "off_peak_volume": random.randint(200, 400),
                "signal_cycle_efficiency": round(random.uniform(75, 90), 1),
                "created_at": date.isoformat()
            }
            metrics.append(metric)
        
        return metrics
    
    async def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
