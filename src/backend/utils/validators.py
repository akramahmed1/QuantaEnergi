"""
Validation utilities for EnergyOpti-Pro backend.
"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def validate_currency(currency: str) -> bool:
    """Validate currency code format (ISO 4217)"""
    if not currency:
        return False
    
    # ISO 4217 currency codes are 3 uppercase letters
    pattern = r'^[A-Z]{3}$'
    return bool(re.match(pattern, currency))

def validate_timestamp(timestamp: str) -> bool:
    """Validate ISO 8601 timestamp format"""
    try:
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False

def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format"""
    if not uuid_string:
        return False
    
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_string.lower()))

def validate_percentage(value: float) -> bool:
    """Validate percentage value (0-100)"""
    return 0.0 <= value <= 100.0

def validate_positive_number(value: float) -> bool:
    """Validate positive number"""
    return value > 0

def validate_portfolio_weights(weights: List[float]) -> bool:
    """Validate portfolio weights sum to 1.0"""
    if not weights:
        return False
    
    total = sum(weights)
    return abs(total - 1.0) < 0.001  # Allow small floating point errors

def validate_trading_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate trading data structure"""
    errors = []
    
    required_fields = ['symbol', 'price', 'volume', 'timestamp']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    if 'price' in data and not isinstance(data['price'], (int, float)):
        errors.append("Price must be a number")
    
    if 'volume' in data and not isinstance(data['volume'], (int, float)):
        errors.append("Volume must be a number")
    
    if 'timestamp' in data and not validate_timestamp(data['timestamp']):
        errors.append("Invalid timestamp format")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }

def sanitize_input(input_string: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    if len(sanitized) > 1000:
        sanitized = sanitized[:1000]
    
    return sanitized.strip()

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    if not api_key:
        return False
    
    # API keys should be at least 32 characters and contain alphanumeric + special chars
    if len(api_key) < 32:
        return False
    
    # Should contain at least one letter, one number, and one special character
    has_letter = bool(re.search(r'[a-zA-Z]', api_key))
    has_number = bool(re.search(r'\d', api_key))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', api_key))
    
    return has_letter and has_number and has_special
