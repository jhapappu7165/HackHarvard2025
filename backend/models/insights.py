from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Insight:
    """Cross-domain insight data model"""
    insight_type: str  # 'energy', 'weather', 'traffic', 'cross_domain'
    entity_id: Optional[int]
    entity_type: str  # 'building', 'intersection', 'city', 'system'
    title: str
    description: str
    priority: str = 'medium'
    category: Optional[str] = None
    potential_savings: Optional[float] = None
    confidence_score: Optional[float] = None
    data_sources: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'insight_type': self.insight_type,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'potential_savings': self.potential_savings,
            'confidence_score': self.confidence_score,
            'data_sources': self.data_sources,
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Insight':
        return Insight(
            id=data.get('id'),
            insight_type=data['insight_type'],
            entity_id=data.get('entity_id'),
            entity_type=data['entity_type'],
            title=data['title'],
            description=data['description'],
            priority=data.get('priority', 'medium'),
            category=data.get('category'),
            potential_savings=data.get('potential_savings'),
            confidence_score=data.get('confidence_score'),
            data_sources=data.get('data_sources'),
            metadata=data.get('metadata'),
            created_at=data.get('created_at')
        )