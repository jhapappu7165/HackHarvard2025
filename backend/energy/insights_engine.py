from typing import List, Dict
from utils.analysis import EnergyAnalyzer
from models import Insight
import numpy as np

class InsightsEngine:
    
    def __init__(self):
        self.analyzer = EnergyAnalyzer()
    
    def generate_insights(self, building_data: Dict, energy_readings: List[Dict]) -> List[Insight]:
        """Generate AI insights based on energy data - mimicking MassEnergyInsight logic"""
        insights = []
        
        # 1. Efficiency Analysis (kBTU/sf)
        if energy_readings:
            latest_usage = energy_readings[-1]['usage']
            efficiency = self.analyzer.calculate_efficiency(
                latest_usage, 
                building_data['square_feet']
            )
            
            # High energy intensity warning
            if efficiency > 100:  # kBTU/sf threshold
                insights.append(Insight(
                    building_id=building_data['id'],
                    insight_type='efficiency_warning',
                    title=f"{building_data['name']} has high energy intensity",
                    description=f"This building uses {efficiency:.1f} kBTU/sf, which is above the "
                               f"recommended threshold. Consider energy efficiency upgrades.",
                    priority='high',
                    potential_savings=latest_usage * 0.15 * 0.15  # 15% reduction * $0.15/kWh
                ))
        
        # 2. Anomaly Detection
        anomalies = self.analyzer.detect_anomalies(energy_readings)
        if anomalies:
            anomaly_month = energy_readings[anomalies[-1]]
            insights.append(Insight(
                building_id=building_data['id'],
                insight_type='usage_anomaly',
                title=f"Unusual energy spike detected in {anomaly_month['month']} {anomaly_month['year']}",
                description=f"Energy usage was {anomaly_month['usage']:.0f} kWh, significantly "
                           f"higher than typical patterns. Investigate potential equipment issues "
                           f"or operational changes.",
                priority='medium',
                potential_savings=None
            ))
        
        # 3. Trend Analysis
        trend, percent_change = self.analyzer.calculate_trend(energy_readings)
        if trend == 'increasing' and abs(percent_change) > 10:
            insights.append(Insight(
                building_id=building_data['id'],
                insight_type='rising_usage',
                title=f"Energy usage increasing at {building_data['name']}",
                description=f"Energy consumption has increased by {abs(percent_change):.1f}% "
                           f"over the analysis period. This trend suggests potential equipment "
                           f"degradation or changes in building use patterns.",
                priority='medium',
                potential_savings=energy_readings[-1]['usage'] * 0.1 * 0.15
            ))
        elif trend == 'decreasing' and abs(percent_change) > 10:
            insights.append(Insight(
                building_id=building_data['id'],
                insight_type='improving_efficiency',
                title=f"Positive trend: Energy usage decreasing",
                description=f"Energy consumption has decreased by {abs(percent_change):.1f}% "
                           f"over the analysis period. Recent efficiency improvements are working!",
                priority='low',
                potential_savings=None
            ))
        
        # 4. Old Building Alert
        if building_data['year_built'] < 1980:
            insights.append(Insight(
                building_id=building_data['id'],
                insight_type='retrofit_opportunity',
                title=f"Retrofit opportunity for older building",
                description=f"Built in {building_data['year_built']}, this building likely lacks "
                           f"modern insulation and efficient HVAC systems. A comprehensive energy "
                           f"audit could identify 20-30% energy savings opportunities.",
                priority='high',
                potential_savings=sum([r['usage'] for r in energy_readings[-12:]]) * 0.25 * 0.15
            ))
        
        # 5. High Cost Alert
        recent_costs = [r['cost'] for r in energy_readings[-12:]]
        total_annual_cost = sum(recent_costs)
        if total_annual_cost > 50000:
            insights.append(Insight(
                building_id=building_data['id'],
                insight_type='high_cost',
                title=f"High energy costs identified",
                description=f"Annual energy costs of ${total_annual_cost:,.0f} make this building "
                           f"a priority for energy efficiency investments. This building is in the "
                           f"top tier for energy spending.",
                priority='high',
                potential_savings=total_annual_cost * 0.2
            ))
        
        return insights
    
    def generate_portfolio_insights(self, all_buildings: List[Dict], 
                                   all_readings: Dict[int, List[Dict]]) -> List[Insight]:
        """Generate portfolio-level insights"""
        insights = []
        
        # Calculate efficiency rankings
        building_efficiencies = []
        for building in all_buildings:
            building_id = building['id']
            if building_id in all_readings and all_readings[building_id]:
                latest = all_readings[building_id][-1]
                efficiency = self.analyzer.calculate_efficiency(
                    latest['usage'],
                    building['square_feet']
                )
                building_efficiencies.append({
                    'building': building,
                    'efficiency': efficiency,
                    'usage': latest['usage']
                })
        
        # Sort by efficiency (higher = worse)
        building_efficiencies.sort(key=lambda x: x['efficiency'], reverse=True)
        
        # Identify "Buildings to Target" (high usage + low efficiency)
        if len(building_efficiencies) >= 3:
            # Top 20% least efficient + high usage
            top_targets = [b for b in building_efficiencies[:max(3, len(building_efficiencies)//5)]
                          if b['usage'] > np.median([be['usage'] for be in building_efficiencies])]
            
            if top_targets:
                target_names = ", ".join([b['building']['name'] for b in top_targets[:3]])
                insights.append(Insight(
                    building_id=None,
                    insight_type='portfolio_priority',
                    title="Priority buildings identified for energy efficiency",
                    description=f"The following buildings are both high energy consumers and have "
                               f"poor efficiency: {target_names}. These should be prioritized for "
                               f"efficiency upgrades to maximize savings.",
                    priority='high',
                    potential_savings=sum([b['usage'] for b in top_targets]) * 0.2 * 0.15
                ))
        
        # Overall portfolio trend
        all_recent_usage = []
        for readings in all_readings.values():
            if len(readings) >= 12:
                all_recent_usage.extend([r['usage'] for r in readings[-12:]])
        
        if all_recent_usage:
            total_usage = sum(all_recent_usage)
            insights.append(Insight(
                building_id=None,
                insight_type='portfolio_summary',
                title="Portfolio Energy Summary",
                description=f"Your total portfolio consumed {total_usage:,.0f} kWh over the last "
                           f"12 months across {len(all_buildings)} buildings. "
                           f"Total estimated annual cost: ${total_usage * 0.15:,.0f}",
                priority='low',
                potential_savings=None
            ))
        
        return insights