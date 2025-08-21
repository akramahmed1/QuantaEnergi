"""
Unified utilities for market data services.

This module eliminates duplication by providing shared functionality for:
- Data validation and transformation
- Common calculations and formulas
- Shared constants and enums
- Utility functions used across services
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
import uuid
import json

# Common enums used across services
class MarketStatus(Enum):
    """Market status values."""
    OPEN = "open"
    CLOSED = "closed"
    PRE_MARKET = "pre_market"
    AFTER_HOURS = "after_hours"
    HOLIDAY = "holiday"
    WEEKEND = "weekend"

class DataQuality(Enum):
    """Data quality indicators."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNKNOWN = "unknown"

class Currency(Enum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CAD = "CAD"
    AUD = "AUD"
    CHF = "CHF"
    CNY = "CNY"
    SAR = "SAR"  # Saudi Riyal
    AED = "AED"  # UAE Dirham
    QAR = "QAR"  # Qatari Riyal
    KWD = "KWD"  # Kuwaiti Dinar
    BHD = "BHD"  # Bahraini Dinar
    OMR = "OMR"  # Omani Rial

class Unit(Enum):
    """Measurement units."""
    MEGAWATT = "MW"
    MEGAWATT_HOUR = "MWh"
    GIGAWATT = "GW"
    GIGAWATT_HOUR = "GWh"
    KILOWATT = "kW"
    KILOWATT_HOUR = "kWh"
    MILLION_BTU = "MMBtu"
    THERM = "therm"
    BARREL = "bbl"
    CUBIC_FOOT = "cf"
    CUBIC_METER = "m³"
    TON = "ton"
    METRIC_TON = "t"

# Common data structures
@dataclass
class MarketDataPoint:
    """Base market data point structure."""
    timestamp: datetime
    value: float
    unit: Unit
    currency: Optional[Currency] = None
    quality: DataQuality = DataQuality.GOOD
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class TimeSeriesData:
    """Time series data structure."""
    data_points: List[MarketDataPoint]
    start_time: datetime
    end_time: datetime
    interval: timedelta
    total_points: int
    
    def __post_init__(self):
        """Validate time series data."""
        if self.start_time >= self.end_time:
            raise ValueError("Start time must be before end time")
        
        if len(self.data_points) != self.total_points:
            raise ValueError("Data points count mismatch")
    
    def get_value_at(self, timestamp: datetime) -> Optional[float]:
        """Get value at specific timestamp."""
        for point in self.data_points:
            if point.timestamp == timestamp:
                return point.value
        return None
    
    def get_range(self, start: datetime, end: datetime) -> 'TimeSeriesData':
        """Get subset of data within time range."""
        filtered_points = [
            point for point in self.data_points
            if start <= point.timestamp <= end
        ]
        
        return TimeSeriesData(
            data_points=filtered_points,
            start_time=start,
            end_time=end,
            interval=self.interval,
            total_points=len(filtered_points)
        )

# Utility functions
def generate_unique_id(prefix: str = "") -> str:
    """
    Generate unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        
    Returns:
        Unique identifier string
    """
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{unique_part}" if prefix else unique_part

def validate_time_range(start_time: datetime, end_time: datetime, max_days: int = 365) -> None:
    """
    Validate time range parameters.
    
    Args:
        start_time: Start time
        end_time: End time
        max_days: Maximum allowed range in days
        
    Raises:
        ValueError: If time range is invalid
    """
    if start_time >= end_time:
        raise ValueError("Start time must be before end time")
    
    if end_time > datetime.now() + timedelta(days=max_days):
        raise ValueError(f"End time cannot be more than {max_days} days in the future")
    
    if start_time < datetime.now() - timedelta(days=max_days):
        raise ValueError(f"Start time cannot be more than {max_days} days in the past")

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate required fields in data dictionary.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Raises:
        ValueError: If required fields are missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise ValueError(f"Missing required fields: {missing_fields}")

def convert_currency(amount: float, from_currency: Currency, to_currency: Currency, rate: float) -> float:
    """
    Convert amount between currencies.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency
        to_currency: Target currency
        rate: Exchange rate (to_currency / from_currency)
        
    Returns:
        Converted amount
    """
    if from_currency == to_currency:
        return amount
    
    return amount * rate

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        old_value: Original value
        new_value: New value
        
    Returns:
        Percentage change
    """
    if old_value == 0:
        return float('inf') if new_value > 0 else float('-inf') if new_value < 0 else 0
    
    return ((new_value - old_value) / old_value) * 100

def calculate_moving_average(values: List[float], window: int) -> List[float]:
    """
    Calculate moving average over a window.
    
    Args:
        values: List of values
        window: Window size for moving average
        
    Returns:
        List of moving averages
    """
    if window > len(values):
        return []
    
    moving_averages = []
    for i in range(len(values) - window + 1):
        window_values = values[i:i + window]
        average = sum(window_values) / len(window_values)
        moving_averages.append(average)
    
    return moving_averages

def format_number(value: float, decimal_places: int = 2, use_commas: bool = True) -> str:
    """
    Format number with specified decimal places and optional comma separators.
    
    Args:
        value: Number to format
        decimal_places: Number of decimal places
        use_commas: Whether to use comma separators for thousands
        
    Returns:
        Formatted number string
    """
    formatted = f"{value:.{decimal_places}f}"
    
    if use_commas:
        parts = formatted.split('.')
        parts[0] = f"{int(parts[0]):,}"
        formatted = '.'.join(parts)
    
    return formatted

def parse_datetime(date_string: str, formats: Optional[List[str]] = None) -> datetime:
    """
    Parse datetime string with multiple format support.
    
    Args:
        date_string: Date string to parse
        formats: List of date formats to try
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If date string cannot be parsed
    """
    if formats is None:
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%m/%d/%Y",
            "%d/%m/%Y"
        ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_string}")

def is_business_day(check_date: date) -> bool:
    """
    Check if date is a business day (Monday-Friday).
    
    Args:
        check_date: Date to check
        
    Returns:
        True if business day, False otherwise
    """
    return check_date.weekday() < 5

def get_next_business_day(check_date: date) -> date:
    """
    Get next business day.
    
    Args:
        check_date: Starting date
        
    Returns:
        Next business day
    """
    next_day = check_date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day

def get_previous_business_day(check_date: date) -> date:
    """
    Get previous business day.
    
    Args:
        check_date: Starting date
        
    Returns:
        Previous business day
    """
    prev_day = check_date - timedelta(days=1)
    while not is_business_day(prev_day):
        prev_day -= timedelta(days=1)
    return prev_day

# Data validation utilities
def validate_numeric_range(value: float, min_value: float, max_value: float, field_name: str) -> None:
    """
    Validate numeric value is within range.
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of field for error message
        
    Raises:
        ValueError: If value is outside range
    """
    if not min_value <= value <= max_value:
        raise ValueError(f"{field_name} must be between {min_value} and {max_value}, got {value}")

def validate_string_length(value: str, min_length: int, max_length: int, field_name: str) -> None:
    """
    Validate string length is within range.
    
    Args:
        value: String to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
        field_name: Name of field for error message
        
    Raises:
        ValueError: If string length is outside range
    """
    if not min_length <= len(value) <= max_length:
        raise ValueError(f"{field_name} length must be between {min_length} and {max_length}, got {len(value)}")

def validate_email_format(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email string to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

# Data transformation utilities
def flatten_nested_dict(data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """
    Flatten nested dictionary structure.
    
    Args:
        data: Nested dictionary to flatten
        prefix: Prefix for flattened keys
        
    Returns:
        Flattened dictionary
    """
    flattened = {}
    
    for key, value in data.items():
        new_key = f"{prefix}.{key}" if prefix else key
        
        if isinstance(value, dict):
            flattened.update(flatten_nested_dict(value, new_key))
        else:
            flattened[new_key] = value
    
    return flattened

def group_by_field(data: List[Dict[str, Any]], field: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Group data by specified field.
    
    Args:
        data: List of dictionaries to group
        field: Field name to group by
        
    Returns:
        Grouped data dictionary
    """
    grouped = {}
    
    for item in data:
        key = item.get(field)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    
    return grouped

def sort_by_field(data: List[Dict[str, Any]], field: str, reverse: bool = False) -> List[Dict[str, Any]]:
    """
    Sort data by specified field.
    
    Args:
        data: List of dictionaries to sort
        field: Field name to sort by
        reverse: Whether to sort in reverse order
        
    Returns:
        Sorted data list
    """
    return sorted(data, key=lambda x: x.get(field, 0), reverse=reverse)

# Error handling utilities
class MarketDataValidationError(Exception):
    """Validation error for market data."""
    pass

class MarketDataProcessingError(Exception):
    """Processing error for market data."""
    pass

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default value on division by zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value to return on division by zero
        
    Returns:
        Division result or default value
    """
    try:
        return numerator / denominator
    except ZeroDivisionError:
        return default

def safe_parse_float(value: Any, default: float = 0.0) -> float:
    """
    Safely parse float value, returning default on failure.
    
    Args:
        value: Value to parse
        default: Default value to return on parsing failure
        
    Returns:
        Parsed float or default value
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_parse_int(value: Any, default: int = 0) -> int:
    """
    Safely parse integer value, returning default on failure.
    
    Args:
        value: Value to parse
        default: Default value to return on parsing failure
        
    Returns:
        Parsed integer or default value
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default 