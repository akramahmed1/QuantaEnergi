"""
A/B Testing Framework for EnergyOpti-Pro.

Provides comprehensive A/B testing capabilities for:
- Pricing model variations
- UI/UX improvements
- Feature rollouts
- Marketing campaigns
- User engagement optimization
"""

import asyncio
import json
import random
import hashlib
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from enum import Enum
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
import numpy as np
from scipy import stats

logger = structlog.get_logger()

class TestType(Enum):
    """Types of A/B tests."""
    PRICING = "pricing"
    UI_UX = "ui_ux"
    FEATURE = "feature"
    MARKETING = "marketing"
    ENGAGEMENT = "engagement"
    PERFORMANCE = "performance"

class TestStatus(Enum):
    """Status of A/B tests."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    STOPPED = "stopped"

class VariantType(Enum):
    """Types of test variants."""
    CONTROL = "control"
    TREATMENT = "treatment"
    VARIANT_A = "variant_a"
    VARIANT_B = "variant_b"
    VARIANT_C = "variant_c"

@dataclass
class ABTest:
    """A/B test configuration."""
    test_id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    variants: List[str]
    traffic_split: Dict[str, float]
    start_date: datetime
    end_date: Optional[datetime]
    target_audience: Dict[str, Any]
    success_metrics: List[str]
    minimum_sample_size: int
    confidence_level: float
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class TestVariant:
    """Test variant configuration."""
    variant_id: str
    test_id: str
    variant_type: VariantType
    name: str
    configuration: Dict[str, Any]
    traffic_percentage: float
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class TestParticipant:
    """Test participant record."""
    participant_id: str
    test_id: str
    variant_id: str
    user_id: str
    session_id: str
    assigned_at: datetime
    last_interaction: datetime
    conversion_events: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TestResult:
    """A/B test results."""
    test_id: str
    variant_id: str
    variant_name: str
    participant_count: int
    conversion_count: int
    conversion_rate: float
    revenue: float
    avg_order_value: float
    engagement_score: float
    statistical_significance: float
    confidence_interval: Tuple[float, float]
    p_value: float
    effect_size: float
    winner: bool = False

class ABTestingService:
    """A/B testing service for EnergyOpti-Pro."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.active_tests: Dict[str, ABTest] = {}
        self.test_variants: Dict[str, Dict[str, TestVariant]] = {}
        self.participants: Dict[str, Dict[str, TestParticipant]] = {}
        
        # Load active tests
        asyncio.create_task(self._load_active_tests())
    
    async def _load_active_tests(self):
        """Load active tests from database."""
        try:
            # This would load from database in production
            logger.info("Loading active A/B tests")
        except Exception as e:
            logger.error(f"Failed to load active tests: {e}")
    
    async def create_test(
        self,
        name: str,
        description: str,
        test_type: TestType,
        variants: List[str],
        traffic_split: Dict[str, float],
        start_date: datetime,
        end_date: Optional[datetime],
        target_audience: Dict[str, Any],
        success_metrics: List[str],
        minimum_sample_size: int = 1000,
        confidence_level: float = 0.95
    ) -> ABTest:
        """Create a new A/B test."""
        test_id = self._generate_test_id(name)
        
        # Validate traffic split
        if not self._validate_traffic_split(traffic_split):
            raise ValueError("Traffic split must sum to 1.0")
        
        # Validate variants
        if len(variants) != len(traffic_split):
            raise ValueError("Number of variants must match traffic split keys")
        
        test = ABTest(
            test_id=test_id,
            name=name,
            description=description,
            test_type=test_type,
            status=TestStatus.DRAFT,
            variants=variants,
            traffic_split=traffic_split,
            start_date=start_date,
            end_date=end_date,
            target_audience=target_audience,
            success_metrics=success_metrics,
            minimum_sample_size=minimum_sample_size,
            confidence_level=confidence_level
        )
        
        # Create test variants
        await self._create_test_variants(test)
        
        # Store test
        self.active_tests[test_id] = test
        
        logger.info(f"Created A/B test: {test_id} - {name}")
        return test
    
    def _generate_test_id(self, name: str) -> str:
        """Generate unique test ID."""
        timestamp = str(int(time.time()))
        name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
        return f"ab_test_{name_hash}_{timestamp}"
    
    def _validate_traffic_split(self, traffic_split: Dict[str, float]) -> bool:
        """Validate traffic split percentages."""
        total = sum(traffic_split.values())
        return abs(total - 1.0) < 0.001  # Allow small floating point errors
    
    async def _create_test_variants(self, test: ABTest):
        """Create test variants."""
        variants = {}
        
        for variant_name, traffic_percentage in test.traffic_split.items():
            variant_type = self._get_variant_type(variant_name)
            
            variant = TestVariant(
                variant_id=f"{test.test_id}_{variant_name}",
                test_id=test.test_id,
                variant_type=variant_type,
                name=variant_name,
                configuration=self._get_default_configuration(test.test_type, variant_name),
                traffic_percentage=traffic_percentage
            )
            
            variants[variant_name] = variant
        
        self.test_variants[test.test_id] = variants
        logger.info(f"Created {len(variants)} variants for test {test.test_id}")
    
    def _get_variant_type(self, variant_name: str) -> VariantType:
        """Get variant type based on name."""
        if variant_name == "control":
            return VariantType.CONTROL
        elif variant_name == "treatment":
            return VariantType.TREATMENT
        elif variant_name == "variant_a":
            return VariantType.VARIANT_A
        elif variant_name == "variant_b":
            return VariantType.VARIANT_B
        elif variant_name == "variant_c":
            return VariantType.VARIANT_C
        else:
            return VariantType.TREATMENT
    
    def _get_default_configuration(self, test_type: TestType, variant_name: str) -> Dict[str, Any]:
        """Get default configuration for a variant."""
        if test_type == TestType.PRICING:
            if variant_name == "control":
                return {"pricing_model": "standard", "discount": 0.0}
            else:
                return {"pricing_model": "premium", "discount": 0.1}
        
        elif test_type == TestType.UI_UX:
            if variant_name == "control":
                return {"theme": "light", "layout": "traditional"}
            else:
                return {"theme": "dark", "layout": "modern"}
        
        elif test_type == TestType.FEATURE:
            if variant_name == "control":
                return {"feature_enabled": False}
            else:
                return {"feature_enabled": True}
        
        else:
            return {"variant": variant_name}
    
    async def start_test(self, test_id: str) -> bool:
        """Start an A/B test."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        if test.status != TestStatus.DRAFT:
            raise ValueError(f"Test {test_id} cannot be started from status {test.status}")
        
        # Validate test configuration
        if not self._validate_test_configuration(test):
            raise ValueError(f"Test {test_id} configuration is invalid")
        
        # Update test status
        test.status = TestStatus.ACTIVE
        test.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Started A/B test: {test_id}")
        return True
    
    def _validate_test_configuration(self, test: ABTest) -> bool:
        """Validate test configuration before starting."""
        # Check if test has variants
        if not test.variants:
            return False
        
        # Check if traffic split is valid
        if not self._validate_traffic_split(test.traffic_split):
            return False
        
        # Check if start date is in the future
        if test.start_date <= datetime.now(timezone.utc):
            return False
        
        # Check if minimum sample size is reasonable
        if test.minimum_sample_size < 100:
            return False
        
        return True
    
    async def assign_variant(
        self,
        test_id: str,
        user_id: str,
        session_id: str,
        user_attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Assign a user to a test variant."""
        if test_id not in self.active_tests:
            return None
        
        test = self.active_tests[test_id]
        
        if test.status != TestStatus.ACTIVE:
            return None
        
        # Check if user is eligible for the test
        if not self._is_user_eligible(test, user_attributes or {}):
            return None
        
        # Check if user is already participating
        existing_participant = await self._get_existing_participant(test_id, user_id)
        if existing_participant:
            return existing_participant.variant_id
        
        # Assign variant using consistent hashing
        variant_name = self._assign_variant_consistent(test_id, user_id)
        
        if variant_name not in self.test_variants[test_id]:
            logger.error(f"Variant {variant_name} not found for test {test_id}")
            return None
        
        variant = self.test_variants[test_id][variant_name]
        
        # Create participant record
        participant = TestParticipant(
            participant_id=f"{test_id}_{user_id}_{session_id}",
            test_id=test_id,
            variant_id=variant.variant_id,
            user_id=user_id,
            session_id=session_id,
            assigned_at=datetime.now(timezone.utc),
            last_interaction=datetime.now(timezone.utc)
        )
        
        # Store participant
        if test_id not in self.participants:
            self.participants[test_id] = {}
        self.participants[test_id][participant.participant_id] = participant
        
        logger.info(f"Assigned user {user_id} to variant {variant_name} in test {test_id}")
        return variant.variant_id
    
    def _is_user_eligible(self, test: ABTest, user_attributes: Dict[str, Any]) -> bool:
        """Check if user is eligible for the test."""
        # Check target audience criteria
        for criteria, value in test.target_audience.items():
            if criteria not in user_attributes:
                return False
            
            user_value = user_attributes[criteria]
            
            # Handle different types of criteria
            if isinstance(value, dict):
                if "min" in value and user_value < value["min"]:
                    return False
                if "max" in value and user_value > value["max"]:
                    return False
                if "values" in value and user_value not in value["values"]:
                    return False
            elif user_value != value:
                return False
        
        return True
    
    async def _get_existing_participant(self, test_id: str, user_id: str) -> Optional[TestParticipant]:
        """Get existing participant for a user in a test."""
        if test_id not in self.participants:
            return None
        
        for participant in self.participants[test_id].values():
            if participant.user_id == user_id:
                return participant
        
        return None
    
    def _assign_variant_consistent(self, test_id: str, user_id: str) -> str:
        """Assign variant using consistent hashing."""
        # Create a hash of test_id + user_id for consistent assignment
        hash_input = f"{test_id}_{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        # Use modulo to get consistent assignment
        random.seed(hash_value)
        rand_value = random.random()
        
        # Assign based on traffic split
        cumulative = 0.0
        for variant_name, percentage in self.active_tests[test_id].traffic_split.items():
            cumulative += percentage
            if rand_value <= cumulative:
                return variant_name
        
        # Fallback to first variant
        return list(self.active_tests[test_id].traffic_split.keys())[0]
    
    async def record_event(
        self,
        test_id: str,
        user_id: str,
        event_name: str,
        event_data: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """Record an event for a test participant."""
        if test_id not in self.participants:
            return False
        
        # Find participant
        participant = None
        for p in self.participants[test_id].values():
            if p.user_id == user_id:
                participant = p
                break
        
        if not participant:
            return False
        
        # Update last interaction
        participant.last_interaction = datetime.now(timezone.utc)
        
        # Record conversion event
        event = {
            "event_name": event_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": event_data or {},
            "session_id": session_id
        }
        
        participant.conversion_events.append(event)
        
        # Update metrics
        if event_name in self.active_tests[test_id].success_metrics:
            if "conversions" not in participant.metrics:
                participant.metrics["conversions"] = 0
            participant.metrics["conversions"] += 1
        
        logger.info(f"Recorded event {event_name} for user {user_id} in test {test_id}")
        return True
    
    async def get_test_results(self, test_id: str) -> List[TestResult]:
        """Get results for an A/B test."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        if test.status != TestStatus.ACTIVE and test.status != TestStatus.COMPLETED:
            raise ValueError(f"Cannot get results for test in status {test.status}")
        
        results = []
        
        for variant_name, variant in self.test_variants[test_id].items():
            # Calculate metrics for this variant
            variant_participants = self._get_variant_participants(test_id, variant.variant_id)
            
            if not variant_participants:
                continue
            
            # Calculate conversion metrics
            conversion_count = sum(1 for p in variant_participants if p.conversion_events)
            conversion_rate = conversion_count / len(variant_participants) if variant_participants else 0
            
            # Calculate revenue metrics
            revenue = sum(p.metrics.get("revenue", 0) for p in variant_participants)
            avg_order_value = revenue / conversion_count if conversion_count > 0 else 0
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(variant_participants)
            
            # Calculate statistical significance
            statistical_significance = self._calculate_statistical_significance(
                test_id, variant_name, conversion_rate
            )
            
            result = TestResult(
                test_id=test_id,
                variant_id=variant.variant_id,
                variant_name=variant_name,
                participant_count=len(variant_participants),
                conversion_count=conversion_count,
                conversion_rate=conversion_rate,
                revenue=revenue,
                avg_order_value=avg_order_value,
                engagement_score=engagement_score,
                statistical_significance=statistical_significance,
                confidence_interval=(0.0, 0.0),  # Placeholder
                p_value=0.0,  # Placeholder
                effect_size=0.0  # Placeholder
            )
            
            results.append(result)
        
        # Determine winner
        if results:
            best_result = max(results, key=lambda r: r.conversion_rate)
            best_result.winner = True
        
        return results
    
    def _get_variant_participants(self, test_id: str, variant_id: str) -> List[TestParticipant]:
        """Get all participants for a specific variant."""
        if test_id not in self.participants:
            return []
        
        return [
            p for p in self.participants[test_id].values()
            if p.variant_id == variant_id
        ]
    
    def _calculate_engagement_score(self, participants: List[TestParticipant]) -> float:
        """Calculate engagement score for participants."""
        if not participants:
            return 0.0
        
        total_score = 0.0
        
        for participant in participants:
            # Base score from participation
            score = 1.0
            
            # Bonus for conversions
            if participant.conversion_events:
                score += len(participant.conversion_events) * 0.5
            
            # Bonus for recent activity
            time_since_last = datetime.now(timezone.utc) - participant.last_interaction
            if time_since_last < timedelta(hours=1):
                score += 0.3
            elif time_since_last < timedelta(hours=24):
                score += 0.1
            
            total_score += score
        
        return total_score / len(participants)
    
    def _calculate_statistical_significance(
        self,
        test_id: str,
        variant_name: str,
        conversion_rate: float
    ) -> float:
        """Calculate statistical significance for a variant."""
        # This is a simplified calculation
        # In production, you'd use proper statistical tests
        
        if variant_name == "control":
            return 0.0
        
        control_variant = self.test_variants[test_id].get("control")
        if not control_variant:
            return 0.0
        
        control_participants = self._get_variant_participants(test_id, control_variant.variant_id)
        if not control_participants:
            return 0.0
        
        control_conversions = sum(1 for p in control_participants if p.conversion_events)
        control_rate = control_conversions / len(control_participants)
        
        # Simple significance calculation
        if control_rate == 0:
            return 1.0 if conversion_rate > 0 else 0.0
        
        improvement = (conversion_rate - control_rate) / control_rate
        return min(abs(improvement), 1.0)
    
    async def stop_test(self, test_id: str) -> bool:
        """Stop an A/B test."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        if test.status != TestStatus.ACTIVE:
            raise ValueError(f"Test {test_id} cannot be stopped from status {test.status}")
        
        # Update test status
        test.status = TestStatus.STOPPED
        test.end_date = datetime.now(timezone.utc)
        test.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Stopped A/B test: {test_id}")
        return True
    
    async def complete_test(self, test_id: str) -> bool:
        """Mark an A/B test as completed."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        if test.status != TestStatus.ACTIVE:
            raise ValueError(f"Test {test_id} cannot be completed from status {test.status}")
        
        # Check if minimum sample size is reached
        total_participants = sum(
            len(self._get_variant_participants(test_id, variant.variant_id))
            for variant in self.test_variants[test_id].values()
        )
        
        if total_participants < test.minimum_sample_size:
            logger.warning(f"Test {test_id} has insufficient participants: {total_participants}")
            return False
        
        # Update test status
        test.status = TestStatus.COMPLETED
        test.end_date = datetime.now(timezone.utc)
        test.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Completed A/B test: {test_id}")
        return True
    
    async def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """Get comprehensive status of an A/B test."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        # Calculate participant counts
        variant_stats = {}
        total_participants = 0
        
        for variant_name, variant in self.test_variants[test_id].items():
            participants = self._get_variant_participants(test_id, variant.variant_id)
            participant_count = len(participants)
            total_participants += participant_count
            
            variant_stats[variant_name] = {
                "participant_count": participant_count,
                "traffic_percentage": variant.traffic_percentage,
                "is_active": variant.is_active
            }
        
        return {
            "test_id": test_id,
            "name": test.name,
            "status": test.status.value,
            "test_type": test.test_type.value,
            "start_date": test.start_date.isoformat(),
            "end_date": test.end_date.isoformat() if test.end_date else None,
            "total_participants": total_participants,
            "minimum_sample_size": test.minimum_sample_size,
            "confidence_level": test.confidence_level,
            "variants": variant_stats,
            "progress_percentage": min(total_participants / test.minimum_sample_size, 1.0) * 100
        }
    
    async def export_test_data(self, test_id: str, format: str = "json") -> str:
        """Export test data for analysis."""
        if test_id not in self.active_tests:
            raise ValueError(f"Test {test_id} not found")
        
        test = self.active_tests[test_id]
        
        export_data = {
            "test_info": {
                "test_id": test.test_id,
                "name": test.name,
                "description": test.description,
                "test_type": test.test_type.value,
                "status": test.status.value,
                "start_date": test.start_date.isoformat(),
                "end_date": test.end_date.isoformat() if test.end_date else None
            },
            "variants": {},
            "participants": {},
            "results": await self.get_test_results(test_id)
        }
        
        # Add variant information
        for variant_name, variant in self.test_variants[test_id].items():
            export_data["variants"][variant_name] = {
                "variant_id": variant.variant_id,
                "variant_type": variant.variant_type.value,
                "name": variant.name,
                "configuration": variant.configuration,
                "traffic_percentage": variant.traffic_percentage
            }
        
        # Add participant information
        if test_id in self.participants:
            for participant_id, participant in self.participants[test_id].items():
                export_data["participants"][participant_id] = {
                    "user_id": participant.user_id,
                    "variant_id": participant.variant_id,
                    "assigned_at": participant.assigned_at.isoformat(),
                    "last_interaction": participant.last_interaction.isoformat(),
                    "conversion_events": participant.conversion_events,
                    "metrics": participant.metrics
                }
        
        if format == "json":
            return json.dumps(export_data, default=str, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def cleanup_completed_tests(self, days_old: int = 30):
        """Clean up old completed tests."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)
        
        tests_to_remove = []
        
        for test_id, test in self.active_tests.items():
            if (test.status == TestStatus.COMPLETED and 
                test.end_date and 
                test.end_date < cutoff_date):
                tests_to_remove.append(test_id)
        
        for test_id in tests_to_remove:
            del self.active_tests[test_id]
            if test_id in self.test_variants:
                del self.test_variants[test_id]
            if test_id in self.participants:
                del self.participants[test_id]
            
            logger.info(f"Cleaned up old test: {test_id}")
    
    def get_active_tests_count(self) -> int:
        """Get count of active tests."""
        return sum(1 for test in self.active_tests.values() if test.status == TestStatus.ACTIVE)
    
    def get_total_participants(self) -> int:
        """Get total participants across all tests."""
        total = 0
        for test_participants in self.participants.values():
            total += len(test_participants)
        return total
