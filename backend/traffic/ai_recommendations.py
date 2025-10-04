"""
AI Recommendation Engine
Integrates with Gemini API to generate intelligent traffic optimization recommendations
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AIRecommendationEngine:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # For hackathon demo - use a placeholder
            self.api_key = "demo_key"
            print("Warning: GEMINI_API_KEY not found. Using demo mode.")
        
        # Configure Gemini
        if self.api_key != "demo_key":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    async def generate_recommendations(self, intersection_id: str, traffic_data: Dict[str, Any], 
                                    time_period: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate AI-powered traffic optimization recommendations"""
        
        if self.model is None:
            # Demo mode - return realistic recommendations
            return await self._generate_demo_recommendations(traffic_data, time_period)
        
        try:
            # Prepare context for Gemini
            context = self._prepare_context(intersection_id, traffic_data, time_period)
            
            # Generate prompt
            prompt = self._create_optimization_prompt(context)
            
            # Get AI response
            response = await self._get_ai_response(prompt)
            
            # Parse and structure recommendations
            recommendations = self._parse_ai_response(response)
            
            return recommendations
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
            # Fallback to demo recommendations
            return await self._generate_demo_recommendations(traffic_data, time_period)
    
    def _prepare_context(self, intersection_id: str, traffic_data: Dict[str, Any], 
                       time_period: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for AI analysis"""
        return {
            "intersection": {
                "id": intersection_id,
                "location": "Mass Ave & Magazine St, Boston, MA"
            },
            "time_period": time_period,
            "traffic_analysis": self._analyze_traffic_for_ai(traffic_data),
            "current_issues": self._identify_current_issues(traffic_data),
            "optimization_goals": [
                "Reduce average delay",
                "Increase throughput",
                "Improve safety",
                "Minimize fuel consumption"
            ]
        }
    
    def _analyze_traffic_for_ai(self, traffic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze traffic data for AI context"""
        analysis = {
            "total_volume": 0,
            "street_analysis": {},
            "bottlenecks": [],
            "efficiency_issues": []
        }
        
        # Handle different data structures
        # The traffic_data from get_traffic_data has this structure:
        # {"intersection_id": ..., "time_period": ..., "traffic_data": {...}, "streets": {...}}
        # But we need the street_data from the request, not the traffic_data field
        
        # First try to get street_data from the request
        street_data_dict = {}
        if hasattr(traffic_data, 'street_data'):
            street_data_dict = traffic_data.street_data
        elif isinstance(traffic_data, dict) and 'street_data' in traffic_data:
            street_data_dict = traffic_data['street_data']
        else:
            # Fallback to traffic_data structure
            traffic_data_field = traffic_data.get("traffic_data", {})
            if isinstance(traffic_data_field, dict) and 'traffic_data' in traffic_data_field:
                street_data_dict = traffic_data_field['traffic_data']
            else:
                street_data_dict = traffic_data_field
        
        for street_name, street_data in street_data_dict.items():
            if isinstance(street_data, dict):
                total_volume = sum(street_data.values())
            else:
                total_volume = 0
            analysis["total_volume"] += total_volume
            
            # Analyze each street
            street_analysis = {
                "total_volume": total_volume,
                "movements": street_data if isinstance(street_data, dict) else {},
                "primary_movement": max(street_data.items(), key=lambda x: x[1]) if isinstance(street_data, dict) and street_data else ("thru", 0),
                "efficiency_issues": []
            }
            
            # Identify issues
            if total_volume == 0:
                street_analysis["efficiency_issues"].append("Unused street - wasted signal time")
            elif total_volume > 100:
                street_analysis["efficiency_issues"].append("High volume - potential bottleneck")
            
            # Check for unused movements
            if isinstance(street_data, dict):
                for movement, volume in street_data.items():
                    if volume == 0 and movement != "u_turn":
                        street_analysis["efficiency_issues"].append(f"Unused {movement} movement")
            
            analysis["street_analysis"][street_name] = street_analysis
        
        return analysis
    
    def _identify_current_issues(self, traffic_data: Dict[str, Any]) -> List[str]:
        """Identify current traffic issues"""
        issues = []
        
        street_data = traffic_data.get("traffic_data", {})
        if not street_data:
            street_data = traffic_data.get("street_data", {})
        
        # Check for high volume streets
        for street_name, street_info in street_data.items():
            if isinstance(street_info, dict):
                total_volume = sum(street_info.values())
                if total_volume > 100:
                    issues.append(f"High traffic volume on {street_name} ({total_volume} vehicles)")
        
        # Check for unused streets
        for street_name, street_info in street_data.items():
            if isinstance(street_info, dict) and sum(street_info.values()) == 0:
                issues.append(f"Unused street: {street_name} - wasting signal time")
        
        # Check for imbalanced traffic
        street_volumes = [sum(street.values()) for street in street_data.values() if isinstance(street, dict)]
        if street_volumes:
            max_volume = max(street_volumes)
            min_volume = min(street_volumes)
            if max_volume > 0 and min_volume / max_volume < 0.1:
                issues.append("Highly imbalanced traffic distribution")
        
        return issues
    
    def _create_optimization_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for Gemini AI"""
        prompt = f"""
You are a Smart Traffic Management Specialist analyzing the intersection at {context['intersection']['location']}.

TRAFFIC DATA ANALYSIS:
Time Period: {context['time_period']['start_time']} - {context['time_period']['end_time']}
Total Volume: {context['traffic_analysis']['total_volume']} vehicles

STREET ANALYSIS:
"""
        
        for street_name, analysis in context['traffic_analysis']['street_analysis'].items():
            prompt += f"""
{street_name}:
- Total Volume: {analysis['total_volume']} vehicles
- Primary Movement: {analysis['primary_movement'][0]} ({analysis['primary_movement'][1]} vehicles)
- Issues: {', '.join(analysis['efficiency_issues']) if analysis['efficiency_issues'] else 'None'}
"""
        
        prompt += f"""
CURRENT ISSUES:
{chr(10).join(f"- {issue}" for issue in context['current_issues'])}

OPTIMIZATION GOALS:
{chr(10).join(f"- {goal}" for goal in context['optimization_goals'])}

Please provide specific, actionable traffic signal optimization recommendations. For each recommendation, include:
1. Specific action (e.g., "Extend green time for Mass Ave Southbound to 60 seconds")
2. Clear reasoning (e.g., "This street has the highest volume and needs priority")
3. Expected impact (e.g., "Reduces delay by 25% and increases throughput by 15%")
4. Implementation steps

Format your response as a JSON array with the following structure:
[
  {{
    "step": 1,
    "action": "Specific action to take",
    "reasoning": "Why this action is needed",
    "impact": "Expected performance improvement",
    "implementation": "How to implement this change"
  }}
]

Focus on practical, implementable solutions that address the specific traffic patterns observed.
"""
        
        return prompt
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Gemini AI"""
        try:
            response = await asyncio.to_thread(
                self.model.generate_content, prompt
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise e
    
    def _parse_ai_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured recommendations"""
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                recommendations = json.loads(json_str)
                
                # Validate and enhance recommendations
                for rec in recommendations:
                    if 'step' not in rec:
                        rec['step'] = len(recommendations)
                    if 'impact' not in rec:
                        rec['impact'] = "Improved traffic flow and reduced delays"
                
                return recommendations
            else:
                # Fallback parsing
                return self._parse_text_response(response)
                
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse text response when JSON parsing fails"""
        recommendations = []
        lines = response.split('\n')
        current_rec = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Step') or line.startswith('1.') or line.startswith('2.'):
                if current_rec:
                    recommendations.append(current_rec)
                current_rec = {'step': len(recommendations) + 1}
            elif line.startswith('Action:') or line.startswith('Action'):
                current_rec['action'] = line.split(':', 1)[1].strip()
            elif line.startswith('Reason:') or line.startswith('Reasoning'):
                current_rec['reasoning'] = line.split(':', 1)[1].strip()
            elif line.startswith('Impact:') or line.startswith('Expected'):
                current_rec['impact'] = line.split(':', 1)[1].strip()
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    async def _generate_demo_recommendations(self, traffic_data: Dict[str, Any], 
                                          time_period: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate demo recommendations when AI is not available"""
        
        # Analyze traffic data to generate realistic recommendations
        street_data = traffic_data.get("street_data", {})
        if not street_data:
            street_data = traffic_data.get("traffic_data", {})
        
        recommendations = []
        
        # Find highest volume street
        max_volume_street = None
        max_volume = 0
        for street_name, street_info in street_data.items():
            total_volume = sum(street_info.values())
            if total_volume > max_volume:
                max_volume = total_volume
                max_volume_street = street_name
        
        # Find unused streets
        unused_streets = []
        for street_name, street_info in street_data.items():
            if sum(street_info.values()) == 0:
                unused_streets.append(street_name)
        
        # Recommendation 1: Optimize high-volume street
        if max_volume_street and max_volume > 50:
            recommendations.append({
                "step": 1,
                "action": f"Extend green time for {max_volume_street} to 60 seconds",
                "reasoning": f"This street has the highest volume ({max_volume} vehicles) and needs priority to prevent congestion",
                "impact": f"Reduces delay by 30% and increases throughput by 25% by prioritizing the highest volume movement",
                "implementation": "Adjust signal timing in traffic control system to extend green phase"
            })
        
        # Recommendation 2: Optimize unused streets
        if unused_streets:
            for unused_street in unused_streets:
                recommendations.append({
                    "step": len(recommendations) + 1,
                    "action": f"Minimize signal time for {unused_street} to 5 seconds",
                    "reasoning": f"{unused_street} has zero traffic and is wasting signal cycle time",
                    "impact": f"Reduces overall cycle time by 20% and improves efficiency for active streets",
                    "implementation": "Set minimum green time for unused approach"
                })
        
        # Recommendation 3: Coordinate signal phases
        recommendations.append({
            "step": len(recommendations) + 1,
            "action": "Implement coordinated signal progression with 90-second cycle",
            "reasoning": "Coordinated timing prevents traffic from hitting multiple red lights",
            "impact": "Reduces travel time by 15% and improves fuel efficiency by 10%",
            "implementation": "Synchronize with adjacent intersections using traffic management system"
        })
        
        # Recommendation 4: Protected left turns
        left_turn_streets = []
        for street_name, street_info in street_data.items():
            if street_info.get("left", 0) > 20:
                left_turn_streets.append(street_name)
        
        if left_turn_streets:
            recommendations.append({
                "step": len(recommendations) + 1,
                "action": f"Add protected left-turn phase for {', '.join(left_turn_streets)}",
                "reasoning": f"High left-turn volumes ({sum(street_data[street].get('left', 0) for street in left_turn_streets)} vehicles) need dedicated time",
                "impact": "Eliminates left-turn conflicts and reduces accidents by 40%",
                "implementation": "Add left-turn arrow signal and adjust timing"
            })
        
        # Recommendation 5: Dynamic timing
        recommendations.append({
            "step": len(recommendations) + 1,
            "action": "Implement adaptive signal timing based on real-time traffic",
            "reasoning": "Traffic patterns change throughout the day and need dynamic adjustment",
            "impact": "Improves overall efficiency by 20% and reduces delays by 25%",
            "implementation": "Install traffic sensors and connect to adaptive control system"
        })
        
        return recommendations
    
    async def generate_optimized_rules(self, intersection_id: str, street_data: Dict[str, Any], 
                                     time_period: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate optimized traffic rules based on recommendations"""
        
        # Get recommendations
        recommendations = await self.generate_recommendations(intersection_id, street_data, time_period)
        
        # Generate optimized rules based on recommendations
        optimized_rules = []
        
        for rec in recommendations:
            if "extend green time" in rec["action"].lower():
                # Extract street name and timing
                street_name = self._extract_street_name(rec["action"])
                timing = self._extract_timing(rec["action"])
                
                if street_name and timing:
                    optimized_rules.append({
                        "street_name": street_name,
                        "direction": self._get_direction(street_name),
                        "signal_timing": timing,
                        "cycle_length": 90,
                        "phase_duration": timing
                    })
        
        # Default rules for streets not mentioned in recommendations
        default_rules = [
            {"street_name": "Mass Ave", "direction": "Northbound", "signal_timing": 30, "cycle_length": 90, "phase_duration": 30},
            {"street_name": "Mass Ave", "direction": "Southbound", "signal_timing": 45, "cycle_length": 90, "phase_duration": 45},
            {"street_name": "Magazine St", "direction": "Eastbound", "signal_timing": 15, "cycle_length": 90, "phase_duration": 15},
            {"street_name": "Driveway", "direction": "Westbound", "signal_timing": 5, "cycle_length": 90, "phase_duration": 5}
        ]
        
        # Merge optimized and default rules
        final_rules = optimized_rules.copy()
        for default_rule in default_rules:
            if not any(rule["street_name"] == default_rule["street_name"] and 
                     rule["direction"] == default_rule["direction"] for rule in optimized_rules):
                final_rules.append(default_rule)
        
        return final_rules
    
    def _extract_street_name(self, action: str) -> Optional[str]:
        """Extract street name from action text"""
        if "Mass Ave" in action:
            return "Mass Ave"
        elif "Magazine St" in action:
            return "Magazine St"
        elif "Driveway" in action:
            return "Driveway"
        return None
    
    def _extract_timing(self, action: str) -> Optional[int]:
        """Extract timing from action text"""
        import re
        match = re.search(r'(\d+)\s*seconds?', action)
        if match:
            return int(match.group(1))
        return None
    
    def _get_direction(self, street_name: str) -> str:
        """Get direction for street name"""
        if street_name == "Mass Ave":
            return "Southbound"  # Default to southbound for Mass Ave
        elif street_name == "Magazine St":
            return "Eastbound"
        elif street_name == "Driveway":
            return "Westbound"
        return "Unknown"
