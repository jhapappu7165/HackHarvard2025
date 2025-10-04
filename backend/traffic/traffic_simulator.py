"""
Traffic Simulation Engine
Simulates traffic flow with different signal timings and calculates performance metrics
"""

import numpy as np
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class TrafficSimulator:
    def __init__(self):
        self.simulation_cache = {}
        self.performance_metrics = {}
    
    async def simulate_traffic_flow(self, intersection_id: str, current_rules: List[Dict[str, Any]], 
                                  optimized_rules: List[Dict[str, Any]], 
                                  traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate traffic flow with current and optimized rules"""
        
        # Run current rules simulation
        current_simulation = await self._run_simulation(
            intersection_id, current_rules, traffic_data, "current"
        )
        
        # Run optimized rules simulation
        optimized_simulation = await self._run_simulation(
            intersection_id, optimized_rules, traffic_data, "optimized"
        )
        
        # Calculate improvements
        improvements = self._calculate_improvements(current_simulation, optimized_simulation)
        
        # Generate simulation result
        simulation_result = {
            "simulation_id": f"sim_{intersection_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "intersection_id": intersection_id,
            "timestamp": datetime.now().isoformat(),
            "current_performance": current_simulation,
            "optimized_performance": optimized_simulation,
            "improvements": improvements,
            "recommendations": self._generate_simulation_recommendations(improvements)
        }
        
        return simulation_result
    
    async def _run_simulation(self, intersection_id: str, rules: List[Dict[str, Any]], 
                            traffic_data: Dict[str, Any], simulation_type: str) -> Dict[str, Any]:
        """Run traffic simulation with given rules"""
        
        # Extract traffic data - handle different structures
        street_data = traffic_data.get("street_data", {})
        if not street_data:
            street_data = traffic_data.get("traffic_data", {})
        
        # Calculate simulation parameters
        total_volume = 0
        if street_data:
            total_volume = sum(sum(street.values()) if isinstance(street, dict) else 0 for street in street_data.values())
        simulation_duration = 3600  # 1 hour simulation
        
        # Simulate traffic flow
        simulation_results = {}
        
        for street_name, street_info in street_data.items():
            if not isinstance(street_info, dict):
                continue
            street_volume = sum(street_info.values())
            if street_volume == 0:
                continue
            
            # Find corresponding rule
            rule = self._find_rule_for_street(rules, street_name)
            if not rule:
                continue
            
            # Simulate street performance
            street_performance = await self._simulate_street_performance(
                street_name, street_info, rule, simulation_duration
            )
            
            simulation_results[street_name] = street_performance
        
        # Calculate overall performance metrics
        overall_performance = self._calculate_overall_performance(simulation_results, total_volume)
        
        return {
            "simulation_type": simulation_type,
            "total_volume": total_volume,
            "simulation_duration": simulation_duration,
            "street_performance": simulation_results,
            "overall_performance": overall_performance,
            "rules_applied": rules
        }
    
    async def _simulate_street_performance(self, street_name: str, street_data: Dict[str, Any], 
                                        rule: Dict[str, Any], duration: int) -> Dict[str, Any]:
        """Simulate performance for a specific street"""
        
        # Extract rule parameters
        signal_timing = rule.get("signal_timing", 30)
        cycle_length = rule.get("cycle_length", 90)
        phase_duration = rule.get("phase_duration", 30)
        
        # Calculate traffic flow parameters
        total_volume = sum(street_data.values())
        if total_volume == 0:
            return {
                "street_name": street_name,
                "total_volume": 0,
                "average_delay": 0,
                "throughput": 0,
                "queue_length": 0,
                "efficiency": 100
            }
        
        # Simulate queue formation and dissipation
        queue_simulation = self._simulate_queue_dynamics(
            total_volume, signal_timing, cycle_length, duration
        )
        
        # Calculate performance metrics
        average_delay = self._calculate_average_delay(
            queue_simulation, signal_timing, cycle_length
        )
        
        throughput = self._calculate_throughput(
            total_volume, signal_timing, cycle_length, duration
        )
        
        queue_length = self._calculate_queue_length(queue_simulation)
        
        efficiency = self._calculate_street_efficiency(
            average_delay, throughput, total_volume
        )
        
        return {
            "street_name": street_name,
            "total_volume": total_volume,
            "average_delay": average_delay,
            "throughput": throughput,
            "queue_length": queue_length,
            "efficiency": efficiency,
            "signal_timing": signal_timing,
            "cycle_length": cycle_length
        }
    
    def _simulate_queue_dynamics(self, volume: int, signal_timing: int, 
                               cycle_length: int, duration: int) -> List[float]:
        """Simulate queue formation and dissipation over time"""
        
        # Calculate arrival rate (vehicles per second)
        arrival_rate = volume / 3600  # Convert to vehicles per second
        
        # Calculate service rate (vehicles per second during green)
        service_rate = 1 / 2  # Assume 2 seconds per vehicle during green
        
        # Simulate queue over time
        queue_lengths = []
        current_queue = 0
        
        for time_step in range(duration):
            # Add arriving vehicles
            arrivals = np.random.poisson(arrival_rate)
            current_queue += arrivals
            
            # Check if signal is green
            cycle_position = time_step % cycle_length
            is_green = cycle_position < signal_timing
            
            # Process vehicles if green
            if is_green and current_queue > 0:
                processed = min(current_queue, int(service_rate))
                current_queue -= processed
            
            queue_lengths.append(current_queue)
        
        return queue_lengths
    
    def _calculate_average_delay(self, queue_simulation: List[float], 
                               signal_timing: int, cycle_length: int) -> float:
        """Calculate average delay per vehicle"""
        
        if not queue_simulation:
            return 0
        
        # Calculate delay based on queue length and signal timing
        total_delay = sum(queue_simulation)
        total_vehicles = sum(queue_simulation)
        
        if total_vehicles == 0:
            return 0
        
        # Add signal delay (red time)
        red_time = cycle_length - signal_timing
        signal_delay = red_time * 0.5  # Average delay due to red signal
        
        average_delay = (total_delay / len(queue_simulation)) + signal_delay
        
        return min(average_delay, 120)  # Cap at 2 minutes
    
    def _calculate_throughput(self, volume: int, signal_timing: int, 
                            cycle_length: int, duration: int) -> float:
        """Calculate throughput (vehicles per hour)"""
        
        # Calculate effective green time ratio
        green_ratio = signal_timing / cycle_length
        
        # Calculate theoretical throughput
        theoretical_throughput = volume * green_ratio
        
        # Apply efficiency factor
        efficiency_factor = 0.85  # 85% efficiency
        
        return theoretical_throughput * efficiency_factor
    
    def _calculate_queue_length(self, queue_simulation: List[float]) -> float:
        """Calculate average queue length"""
        
        if not queue_simulation:
            return 0
        
        return sum(queue_simulation) / len(queue_simulation)
    
    def _calculate_street_efficiency(self, average_delay: float, throughput: float, 
                                   volume: int) -> float:
        """Calculate street efficiency score (0-100)"""
        
        if volume == 0:
            return 100
        
        # Base efficiency
        efficiency = 100
        
        # Penalize for high delay
        if average_delay > 30:
            efficiency -= min(50, (average_delay - 30) * 2)
        
        # Penalize for low throughput
        expected_throughput = volume * 0.8  # 80% of volume should be processed
        if throughput < expected_throughput:
            efficiency -= (expected_throughput - throughput) / expected_throughput * 30
        
        return max(0, efficiency)
    
    def _calculate_overall_performance(self, simulation_results: Dict[str, Any], 
                                     total_volume: int) -> Dict[str, Any]:
        """Calculate overall intersection performance"""
        
        if not simulation_results:
            return {
                "average_delay": 0,
                "total_throughput": 0,
                "efficiency": 100,
                "level_of_service": "A"
            }
        
        # Calculate weighted averages
        total_delay = 0
        total_throughput = 0
        total_efficiency = 0
        street_count = 0
        
        for street_name, performance in simulation_results.items():
            if performance["total_volume"] > 0:
                weight = performance["total_volume"] / total_volume
                total_delay += performance["average_delay"] * weight
                total_throughput += performance["throughput"]
                total_efficiency += performance["efficiency"] * weight
                street_count += 1
        
        if street_count == 0:
            return {
                "average_delay": 0,
                "total_throughput": 0,
                "efficiency": 100,
                "level_of_service": "A"
            }
        
        average_delay = total_delay
        efficiency = total_efficiency
        level_of_service = self._calculate_level_of_service(average_delay)
        
        return {
            "average_delay": average_delay,
            "total_throughput": total_throughput,
            "efficiency": efficiency,
            "level_of_service": level_of_service,
            "active_streets": street_count
        }
    
    def _calculate_level_of_service(self, average_delay: float) -> str:
        """Calculate Level of Service based on average delay"""
        
        if average_delay <= 10:
            return "A"
        elif average_delay <= 20:
            return "B"
        elif average_delay <= 35:
            return "C"
        elif average_delay <= 55:
            return "D"
        elif average_delay <= 80:
            return "E"
        else:
            return "F"
    
    def _find_rule_for_street(self, rules: List[Dict[str, Any]], street_name: str) -> Optional[Dict[str, Any]]:
        """Find rule for specific street"""
        
        # Map street names to rule names
        street_mapping = {
            "mass_ave_northbound": "Mass Ave",
            "mass_ave_southbound": "Mass Ave", 
            "magazine_st_eastbound": "Magazine St",
            "driveway_westbound": "Driveway"
        }
        
        rule_street_name = street_mapping.get(street_name, street_name)
        
        for rule in rules:
            if rule.get("street_name") == rule_street_name:
                return rule
        
        return None
    
    def _calculate_improvements(self, current_simulation: Dict[str, Any], 
                             optimized_simulation: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate improvements from optimization"""
        
        current_perf = current_simulation["overall_performance"]
        optimized_perf = optimized_simulation["overall_performance"]
        
        # Calculate percentage improvements
        delay_improvement = 0
        if current_perf["average_delay"] > 0:
            delay_improvement = ((current_perf["average_delay"] - optimized_perf["average_delay"]) 
                               / current_perf["average_delay"]) * 100
        
        throughput_improvement = 0
        if current_perf["total_throughput"] > 0:
            throughput_improvement = ((optimized_perf["total_throughput"] - current_perf["total_throughput"]) 
                                    / current_perf["total_throughput"]) * 100
        
        efficiency_improvement = optimized_perf["efficiency"] - current_perf["efficiency"]
        
        # Calculate fuel savings (estimated)
        fuel_savings = delay_improvement * 0.3  # 30% of delay reduction translates to fuel savings
        
        # Calculate emission reductions
        emission_reduction = delay_improvement * 0.25  # 25% of delay reduction reduces emissions
        
        return {
            "delay_reduction_percent": max(0, delay_improvement),
            "throughput_increase_percent": max(0, throughput_improvement),
            "efficiency_improvement": max(0, efficiency_improvement),
            "fuel_savings_percent": max(0, fuel_savings),
            "emission_reduction_percent": max(0, emission_reduction),
            "level_of_service_improvement": self._calculate_los_improvement(
                current_perf["level_of_service"], 
                optimized_perf["level_of_service"]
            )
        }
    
    def _calculate_los_improvement(self, current_los: str, optimized_los: str) -> str:
        """Calculate Level of Service improvement"""
        
        los_order = ["F", "E", "D", "C", "B", "A"]
        current_index = los_order.index(current_los)
        optimized_index = los_order.index(optimized_los)
        
        if optimized_index > current_index:
            return f"Improved from {current_los} to {optimized_los}"
        elif optimized_index < current_index:
            return f"Degraded from {current_los} to {optimized_los}"
        else:
            return f"Maintained at {current_los}"
    
    def _generate_simulation_recommendations(self, improvements: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on simulation results"""
        
        recommendations = []
        
        if improvements["delay_reduction_percent"] > 20:
            recommendations.append(f"Significant delay reduction of {improvements['delay_reduction_percent']:.1f}% achieved")
        
        if improvements["throughput_increase_percent"] > 15:
            recommendations.append(f"Throughput increased by {improvements['throughput_increase_percent']:.1f}%")
        
        if improvements["efficiency_improvement"] > 10:
            recommendations.append(f"Efficiency improved by {improvements['efficiency_improvement']:.1f} points")
        
        if improvements["fuel_savings_percent"] > 5:
            recommendations.append(f"Fuel consumption reduced by {improvements['fuel_savings_percent']:.1f}%")
        
        if improvements["emission_reduction_percent"] > 5:
            recommendations.append(f"Emissions reduced by {improvements['emission_reduction_percent']:.1f}%")
        
        if not recommendations:
            recommendations.append("Optimization shows marginal improvements - consider additional analysis")
        
        return recommendations
    
    async def get_simulation_history(self, intersection_id: str) -> List[Dict[str, Any]]:
        """Get simulation history for an intersection"""
        
        # This would typically query the database
        # For now, return cached simulations
        return self.simulation_cache.get(intersection_id, [])
    
    async def save_simulation_result(self, intersection_id: str, simulation_result: Dict[str, Any]):
        """Save simulation result to cache"""
        
        if intersection_id not in self.simulation_cache:
            self.simulation_cache[intersection_id] = []
        
        self.simulation_cache[intersection_id].append(simulation_result)
        
        # Keep only last 10 simulations
        if len(self.simulation_cache[intersection_id]) > 10:
            self.simulation_cache[intersection_id] = self.simulation_cache[intersection_id][-10:]
