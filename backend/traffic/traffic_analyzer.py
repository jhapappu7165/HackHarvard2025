"""
Traffic Data Analyzer
Processes traffic data from PDF and provides analysis capabilities
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, time
import asyncio
import re

class TrafficAnalyzer:
    def __init__(self):
        self.traffic_data = {}
        self.analysis_cache = {}
    
    async def load_traffic_data(self):
        """Load and process traffic data from PDF"""
        try:
            # Try to load extracted PDF data first
            with open("traffic_data_extracted.json", "r") as f:
                extracted_data = json.load(f)
            
            # Convert extracted data to our format
            self.traffic_data = self._convert_extracted_data(extracted_data)
            print("✅ Loaded real traffic data from PDF extraction")
            
        except FileNotFoundError:
            print("⚠️  No extracted PDF data found, using simulated data")
            # Fallback to simulated data
            self.traffic_data = {
                "MASS_AVE_MAGAZINE_ST": {
                    "intersection_id": "MASS_AVE_MAGAZINE_ST",
                    "location": "Mass Ave & Magazine St, Boston, MA",
                    "streets": {
                        "mass_ave_northbound": {
                            "name": "Mass Ave",
                            "direction": "Northbound",
                            "coordinates": "42.3505,-71.1053"
                        },
                        "mass_ave_southbound": {
                            "name": "Mass Ave", 
                            "direction": "Southbound",
                            "coordinates": "42.3505,-71.1053"
                        },
                        "magazine_st_eastbound": {
                            "name": "Magazine St",
                            "direction": "Eastbound", 
                            "coordinates": "42.3505,-71.1053"
                        },
                        "driveway_westbound": {
                            "name": "Driveway",
                            "direction": "Westbound",
                            "coordinates": "42.3505,-71.1053"
                        }
                    },
                    "time_periods": self._generate_time_periods()
                }
            }
    
    def _convert_extracted_data(self, extracted_data: List[Dict]) -> Dict[str, Any]:
        """Convert extracted PDF data to our internal format"""
        time_periods = {}
        
        for period_data in extracted_data:
            period_key = period_data['period']
            time_periods[period_key] = {
                "start_time": period_data['start_time'],
                "end_time": period_data['end_time'],
                "duration_minutes": 15,
                "peak_status": period_data['peak_status'],
                "traffic_data": period_data['traffic_data']
            }
        
        return {
            "MASS_AVE_MAGAZINE_ST": {
                "intersection_id": "MASS_AVE_MAGAZINE_ST",
                "location": "Mass Ave & Magazine St, Boston, MA",
                "streets": {
                    "mass_ave_northbound": {
                        "name": "Mass Ave",
                        "direction": "Northbound",
                        "coordinates": "42.3505,-71.1053"
                    },
                    "mass_ave_southbound": {
                        "name": "Mass Ave", 
                        "direction": "Southbound",
                        "coordinates": "42.3505,-71.1053"
                    },
                    "magazine_st_eastbound": {
                        "name": "Magazine St",
                        "direction": "Eastbound", 
                        "coordinates": "42.3505,-71.1053"
                    },
                    "driveway_westbound": {
                        "name": "Driveway",
                        "direction": "Westbound",
                        "coordinates": "42.3505,-71.1053"
                    }
                },
                "time_periods": time_periods
            }
        }
    
    def _generate_time_periods(self) -> Dict[str, Dict[str, Any]]:
        """Generate realistic traffic data for 7 AM - 6 PM"""
        time_periods = {}
        
        # Generate 15-minute intervals from 7 AM to 6 PM
        current_time = time(7, 0)
        end_time = time(18, 0)
        
        while current_time < end_time:
            next_minute = current_time.minute + 15
            if next_minute >= 60:
                next_time = time(current_time.hour + 1, next_minute - 60)
            else:
                next_time = time(current_time.hour, next_minute)
            
            period_key = f"{current_time.strftime('%H:%M')}-{next_time.strftime('%H:%M')}"
            
            # Generate realistic traffic patterns
            is_peak = (7 <= current_time.hour <= 9) or (16 <= current_time.hour <= 18)
            is_midday = 11 <= current_time.hour <= 14
            
            time_periods[period_key] = {
                "start_time": current_time.strftime("%H:%M"),
                "end_time": next_time.strftime("%H:%M"),
                "duration_minutes": 15,
                "peak_status": "peak" if is_peak else "off-peak",
                "traffic_data": self._generate_street_traffic_data(current_time, is_peak, is_midday)
            }
            
            current_time = next_time
        
        return time_periods
    
    def _generate_street_traffic_data(self, current_time: time, is_peak: bool, is_midday: bool) -> Dict[str, Any]:
        """Generate realistic traffic data for each street"""
        base_volume = 50 if is_peak else 30 if is_midday else 20
        
        return {
            "mass_ave_northbound": {
                "thru": int(base_volume * (1.2 if is_peak else 0.8)),
                "left": int(base_volume * 0.6),
                "right": int(base_volume * 0.3),
                "u_turn": int(base_volume * 0.1)
            },
            "mass_ave_southbound": {
                "thru": int(base_volume * (1.5 if is_peak else 1.0)),
                "left": int(base_volume * 0.2),
                "right": int(base_volume * 0.4),
                "u_turn": int(base_volume * 0.05)
            },
            "magazine_st_eastbound": {
                "thru": int(base_volume * 0.1),
                "left": int(base_volume * 0.5),
                "right": int(base_volume * 0.6),
                "u_turn": int(base_volume * 0.05)
            },
            "driveway_westbound": {
                "thru": 0,
                "left": 0,
                "right": 0,
                "u_turn": 0
            }
        }
    
    async def get_traffic_data(self, intersection_id, time_period: str) -> Dict[str, Any]:
        """Get traffic data for specific intersection and time period"""
        # Handle both string and int intersection IDs
        if isinstance(intersection_id, int):
            intersection_key = "MASS_AVE_MAGAZINE_ST"
        else:
            intersection_key = intersection_id
        
        if intersection_key not in self.traffic_data:
            raise ValueError(f"Intersection {intersection_id} not found")
        
        intersection_data = self.traffic_data[intersection_key]
        
        # Try to find the time period, handle different formats
        found_period = None
        for period_key in intersection_data["time_periods"]:
            if time_period in period_key or period_key in time_period:
                found_period = period_key
                break
        
        if not found_period:
            # Try to find a close match (e.g., 14:00-15:00 might match 14:00-14:15)
            for period_key in intersection_data["time_periods"]:
                if time_period.split('-')[0] in period_key:
                    found_period = period_key
                    break
        
        if not found_period:
            raise ValueError(f"Time period {time_period} not found. Available periods: {list(intersection_data['time_periods'].keys())[:5]}...")
        
        time_period = found_period
        
        return {
            "intersection_id": intersection_id,
            "time_period": time_period,
            "traffic_data": intersection_data["time_periods"][time_period],
            "streets": intersection_data["streets"]
        }
    
    async def analyze_traffic_patterns(self, intersection_id: str, time_period: Dict[str, Any], 
                                    street_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze traffic patterns and identify bottlenecks"""
        
        analysis = {
            "intersection_id": intersection_id,
            "time_period": time_period,
            "analysis_timestamp": datetime.now().isoformat(),
            "bottlenecks": [],
            "traffic_volume_analysis": {},
            "optimization_opportunities": [],
            "performance_metrics": {}
        }
        
        # Analyze each street
        for street_name, street_info in street_data.items():
            street_analysis = self._analyze_street_traffic(street_name, street_info)
            analysis["traffic_volume_analysis"][street_name] = street_analysis
            
            # Identify bottlenecks
            if street_analysis["total_volume"] > 100:  # High volume threshold
                analysis["bottlenecks"].append({
                    "street": street_name,
                    "issue": "High traffic volume",
                    "severity": "high" if street_analysis["total_volume"] > 150 else "medium",
                    "recommendation": "Consider signal timing optimization"
                })
            
            # Identify unused movements
            for movement, volume in street_info.items():
                if volume == 0 and movement != "u_turn":
                    analysis["optimization_opportunities"].append({
                        "street": street_name,
                        "movement": movement,
                        "opportunity": "Unused movement - can optimize signal timing",
                        "impact": "Reduce signal cycle time"
                    })
        
        # Calculate performance metrics
        analysis["performance_metrics"] = self._calculate_performance_metrics(street_data)
        
        return analysis
    
    def _analyze_street_traffic(self, street_name: str, street_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze traffic for a specific street"""
        total_volume = sum(street_data.values())
        
        # Calculate movement distribution
        movement_distribution = {}
        for movement, volume in street_data.items():
            if total_volume > 0:
                movement_distribution[movement] = (volume / total_volume) * 100
            else:
                movement_distribution[movement] = 0
        
        # Identify primary movement
        primary_movement = max(street_data.items(), key=lambda x: x[1])
        
        return {
            "total_volume": total_volume,
            "movement_distribution": movement_distribution,
            "primary_movement": {
                "movement": primary_movement[0],
                "volume": primary_movement[1],
                "percentage": movement_distribution[primary_movement[0]]
            },
            "efficiency_score": self._calculate_efficiency_score(street_data),
            "optimization_potential": "high" if total_volume > 100 else "medium" if total_volume > 50 else "low"
        }
    
    def _calculate_efficiency_score(self, street_data: Dict[str, Any]) -> float:
        """Calculate traffic efficiency score (0-100)"""
        total_volume = sum(street_data.values())
        if total_volume == 0:
            return 100  # No traffic = perfect efficiency
        
        # Penalize unused movements
        unused_movements = sum(1 for volume in street_data.values() if volume == 0)
        efficiency_penalty = unused_movements * 10
        
        # Base efficiency
        base_efficiency = 80
        
        # Adjust based on volume distribution
        max_volume = max(street_data.values())
        if max_volume > 0:
            concentration_ratio = max_volume / total_volume
            if concentration_ratio > 0.7:  # Too concentrated
                efficiency_penalty += 15
            elif concentration_ratio < 0.3:  # Too distributed
                efficiency_penalty += 10
        
        return max(0, base_efficiency - efficiency_penalty)
    
    def _calculate_performance_metrics(self, street_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        total_volume = sum(sum(street.values()) for street in street_data.values())
        
        # Calculate average delay (simplified)
        avg_delay = 0
        if total_volume > 0:
            # Simulate delay based on volume
            avg_delay = min(120, total_volume * 0.5)  # Max 2 minutes delay
        
        # Calculate throughput
        throughput = total_volume * 4  # vehicles per hour (15-min intervals)
        
        # Calculate efficiency
        efficiency = self._calculate_intersection_efficiency(street_data)
        
        return {
            "total_volume": total_volume,
            "average_delay_seconds": avg_delay,
            "throughput_vph": throughput,
            "efficiency_score": efficiency,
            "level_of_service": self._calculate_level_of_service(avg_delay),
            "optimization_potential": "high" if efficiency < 70 else "medium" if efficiency < 85 else "low"
        }
    
    def _calculate_intersection_efficiency(self, street_data: Dict[str, Any]) -> float:
        """Calculate overall intersection efficiency"""
        total_volume = sum(sum(street.values()) for street in street_data.values())
        if total_volume == 0:
            return 100
        
        # Calculate efficiency based on volume distribution and unused movements
        efficiency = 100
        
        # Penalize for unused streets
        unused_streets = sum(1 for street in street_data.values() 
                           if sum(street.values()) == 0)
        efficiency -= unused_streets * 20
        
        # Penalize for highly imbalanced traffic
        street_volumes = [sum(street.values()) for street in street_data.values()]
        if street_volumes:
            max_volume = max(street_volumes)
            min_volume = min(street_volumes)
            if max_volume > 0:
                imbalance_ratio = min_volume / max_volume
                if imbalance_ratio < 0.1:  # Highly imbalanced
                    efficiency -= 15
        
        return max(0, efficiency)
    
    def _calculate_level_of_service(self, avg_delay: float) -> str:
        """Calculate Level of Service based on average delay"""
        if avg_delay <= 10:
            return "A"
        elif avg_delay <= 20:
            return "B"
        elif avg_delay <= 35:
            return "C"
        elif avg_delay <= 55:
            return "D"
        elif avg_delay <= 80:
            return "E"
        else:
            return "F"
    
    async def get_intersection_summary(self, intersection_id: str) -> Dict[str, Any]:
        """Get summary of intersection traffic patterns"""
        if intersection_id not in self.traffic_data:
            raise ValueError(f"Intersection {intersection_id} not found")
        
        intersection_data = self.traffic_data[intersection_id]
        
        # Calculate overall statistics
        total_volume = 0
        peak_periods = []
        
        for period_key, period_data in intersection_data["time_periods"].items():
            period_volume = sum(
                sum(street.values()) for street in period_data["traffic_data"].values()
            )
            total_volume += period_volume
            
            if period_data["peak_status"] == "peak":
                peak_periods.append({
                    "period": period_key,
                    "volume": period_volume
                })
        
        return {
            "intersection_id": intersection_id,
            "total_daily_volume": total_volume,
            "peak_periods": peak_periods,
            "average_volume_per_period": total_volume / len(intersection_data["time_periods"]),
            "streets": list(intersection_data["streets"].keys()),
            "analysis_timestamp": datetime.now().isoformat()
        }
