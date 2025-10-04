from typing import List, Dict
import numpy as np
from datetime import datetime, timedelta
from models.insights import Insight
from services.weather_normalizer import WeatherNormalizer
from services.correlation_analyzer import CorrelationAnalyzer
from utils.supabase_client import SupabaseClient
from config import Config
import logging

logger = logging.getLogger(__name__)

class InsightsEngine:
    """Generate cross-domain AI insights"""
    
    def __init__(self):
        self.db = SupabaseClient().get_client()
        self.weather_normalizer = WeatherNormalizer()
        self.correlation_analyzer = CorrelationAnalyzer()
        self.config = Config
    
    def generate_comprehensive_insights(self, building_id: int) -> List[Dict]:
        """Generate all types of insights for a building"""
        logger.info(f"Generating comprehensive insights for building {building_id}")
        
        insights = []
        
        try:
            # Get building info
            building_response = self.db.table('energy_buildings')\
                .select('*')\
                .eq('id', building_id)\
                .single()\
                .execute()
            
            if not building_response.data:
                logger.warning(f"Building {building_id} not found")
                return insights
            
            building = building_response.data
            
            # 1. Energy Efficiency Insights
            insights.extend(self._generate_efficiency_insights(building))
            
            # 2. Weather-Normalized Insights
            insights.extend(self._generate_weather_insights(building))
            
            # 3. Traffic Correlation Insights
            insights.extend(self._generate_traffic_insights(building))
            
            # 4. Anomaly Detection Insights
            insights.extend(self._generate_anomaly_insights(building))
            
            # 5. Cost Savings Opportunities
            insights.extend(self._generate_cost_insights(building))
            
            # Save all insights to database
            for insight in insights:
                try:
                    self.db.table('insights').insert(insight).execute()
                except Exception as e:
                    logger.error(f"Error saving insight: {str(e)}")
            
            logger.info(f"Generated {len(insights)} insights for building {building_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            return insights
    
    def _generate_efficiency_insights(self, building: Dict) -> List[Dict]:
        """Generate insights based on energy efficiency"""
        insights = []
        
        try:
            # Get recent energy readings
            energy_response = self.db.table('energy_readings')\
                .select('*')\
                .eq('building_id', building['id'])\
                .order('reading_date', desc=True)\
                .limit(12)\
                .execute()
            
            if not energy_response.data:
                return insights
            
            readings = energy_response.data
            
            # Calculate energy intensity (kBTU/sf)
            total_usage = sum(r['usage'] for r in readings)
            avg_monthly_usage = total_usage / len(readings)
            
            # Convert kWh to kBTU (1 kWh = 3.412 kBTU)
            usage_kbtu = avg_monthly_usage * 3.412
            intensity = usage_kbtu / building['square_feet'] if building['square_feet'] > 0 else 0
            
            # Benchmark: typical commercial building uses 50-150 kBTU/sf/year
            monthly_intensity = intensity * 12  # Annualized
            
            if monthly_intensity > 150:
                potential_savings = (monthly_intensity - 100) * building['square_feet'] / 3.412 * 0.15
                
                insight = Insight(
                    insight_type='energy',
                    entity_id=building['id'],
                    entity_type='building',
                    title=f"High Energy Intensity at {building['name']}",
                    description=f"This building uses {monthly_intensity:.1f} kBTU/sf/year, "
                               f"significantly above the benchmark of 100 kBTU/sf/year. "
                               f"Consider energy efficiency upgrades such as LED lighting, "
                               f"HVAC optimization, or building envelope improvements.",
                    priority='high',
                    category='Efficiency',
                    potential_savings=round(potential_savings, 2),
                    confidence_score=85.0,
                    data_sources=['energy'],
                    metadata={
                        'energy_intensity': round(monthly_intensity, 2),
                        'benchmark': 100,
                        'building_size': building['square_feet']
                    }
                )
                insights.append(insight.to_dict())
            
        except Exception as e:
            logger.error(f"Error generating efficiency insights: {str(e)}")
        
        return insights
    
    def _generate_weather_insights(self, building: Dict) -> List[Dict]:
        """Generate insights based on weather normalization"""
        insights = []
        
        try:
            # Calculate date range (last 12 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Get weather-normalized data
            normalized = self.weather_normalizer.normalize_energy_usage(
                building['id'],
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if 'error' in normalized:
                return insights
            
            weather_impact = abs(normalized.get('weather_impact_percent', 0))
            
            if weather_impact > 25:
                insight = Insight(
                    insight_type='cross_domain',
                    entity_id=building['id'],
                    entity_type='building',
                    title='High Weather Dependency Detected',
                    description=f"Weather accounts for {weather_impact:.1f}% of energy variance "
                               f"at {building['name']}. Consider insulation upgrades, "
                               f"weather stripping, or window replacements to reduce "
                               f"weather sensitivity and improve energy efficiency.",
                    priority='high' if weather_impact > 35 else 'medium',
                    category='Weather Impact',
                    potential_savings=round(normalized.get('original_usage', 0) * 0.15 * 0.15, 2),
                    confidence_score=normalized.get('r_squared', 0) * 100,
                    data_sources=['energy', 'weather'],
                    metadata=normalized
                )
                insights.append(insight.to_dict())
            
        except Exception as e:
            logger.error(f"Error generating weather insights: {str(e)}")
        
        return insights
    
    def _generate_traffic_insights(self, building: Dict) -> List[Dict]:
        """Generate insights based on traffic correlation"""
        insights = []
        
        try:
            correlation_data = self.correlation_analyzer.analyze_traffic_energy_correlation(
                building['id']
            )
            
            if 'error' in correlation_data:
                return insights
            
            correlation = abs(correlation_data.get('correlation', 0))
            significance = correlation_data.get('significance', '')
            
            if correlation > 0.6 and significance == 'significant':
                insight = Insight(
                    insight_type='cross_domain',
                    entity_id=building['id'],
                    entity_type='building',
                    title='Traffic-Energy Correlation Found',
                    description=f"Strong correlation (r={correlation:.2f}) detected between "
                               f"nearby traffic patterns and energy usage at {building['name']}. "
                               f"This suggests occupancy-driven consumption. Consider implementing "
                               f"smart HVAC scheduling or occupancy sensors to optimize energy use "
                               f"based on actual building occupancy patterns.",
                    priority='medium',
                    category='Traffic Impact',
                    potential_savings=None,
                    confidence_score=correlation * 100,
                    data_sources=['energy', 'traffic'],
                    metadata=correlation_data
                )
                insights.append(insight.to_dict())
            
        except Exception as e:
            logger.error(f"Error generating traffic insights: {str(e)}")
        
        return insights
    
    def _generate_anomaly_insights(self, building: Dict) -> List[Dict]:
        """Generate insights based on anomaly detection"""
        insights = []
        
        try:
            # Get energy readings
            energy_response = self.db.table('energy_readings')\
                .select('*')\
                .eq('building_id', building['id'])\
                .order('reading_date')\
                .execute()
            
            if not energy_response.data or len(energy_response.data) < 12:
                return insights
            
            readings = energy_response.data
            
            # Calculate monthly totals
            from collections import defaultdict
            monthly_usage = defaultdict(float)
            
            for reading in readings:
                date_key = reading['reading_date'][:7]  # YYYY-MM
                monthly_usage[date_key] += reading['usage']
            
            usage_values = list(monthly_usage.values())
            
            if len(usage_values) < 12:
                return insights
            
            # Detect anomalies using z-score
            mean_usage = np.mean(usage_values)
            std_usage = np.std(usage_values)
            
            for date_key, usage in monthly_usage.items():
                if std_usage > 0:
                    z_score = (usage - mean_usage) / std_usage
                    
                    if abs(z_score) > self.config.ANOMALY_ZSCORE_THRESHOLD:
                        anomaly_type = "spike" if z_score > 0 else "drop"
                        
                        insight = Insight(
                            insight_type='energy',
                            entity_id=building['id'],
                            entity_type='building',
                            title=f"Unusual Energy {anomaly_type.capitalize()} Detected",
                            description=f"Energy usage in {date_key} was {usage:.0f} kWh, "
                                       f"which is {abs(z_score):.1f} standard deviations from "
                                       f"the average. Investigate potential equipment issues, "
                                       f"operational changes, or data collection problems.",
                            priority='medium',
                            category='Maintenance',
                            potential_savings=None,
                            confidence_score=min(abs(z_score) * 20, 95),
                            data_sources=['energy'],
                            metadata={
                                'z_score': round(z_score, 2),
                                'usage': round(usage, 2),
                                'mean': round(mean_usage, 2),
                                'date': date_key
                            }
                        )
                        insights.append(insight.to_dict())
                        break  # Only report one anomaly to avoid spam
            
        except Exception as e:
            logger.error(f"Error generating anomaly insights: {str(e)}")
        
        return insights
    
    def _generate_cost_insights(self, building: Dict) -> List[Dict]:
        """Generate cost savings opportunities"""
        insights = []
        
        try:
            # Get recent cost data
            energy_response = self.db.table('energy_readings')\
                .select('*')\
                .eq('building_id', building['id'])\
                .order('reading_date', desc=True)\
                .limit(12)\
                .execute()
            
            if not energy_response.data:
                return insights
            
            readings = energy_response.data
            total_cost = sum(r['cost'] for r in readings)
            monthly_avg_cost = total_cost / len(readings)
            
            # If monthly cost is high, suggest optimization
            if monthly_avg_cost > 10000:
                potential_savings = monthly_avg_cost * 0.15  # 15% reduction potential
                
                insight = Insight(
                    insight_type='energy',
                    entity_id=building['id'],
                    entity_type='building',
                    title=f"Significant Cost Reduction Opportunity",
                    description=f"Average monthly energy cost of ${monthly_avg_cost:,.2f} "
                               f"at {building['name']} presents opportunity for savings. "
                               f"Implementing energy management strategies could reduce costs "
                               f"by approximately ${potential_savings:,.2f}/month.",
                    priority='high',
                    category='Cost Savings',
                    potential_savings=round(potential_savings * 12, 2),  # Annual savings
                    confidence_score=75.0,
                    data_sources=['energy'],
                    metadata={
                        'monthly_cost': round(monthly_avg_cost, 2),
                        'annual_cost': round(monthly_avg_cost * 12, 2)
                    }
                )
                insights.append(insight.to_dict())
            
        except Exception as e:
            logger.error(f"Error generating cost insights: {str(e)}")
        
        return insights