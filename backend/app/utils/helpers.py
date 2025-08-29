"""
Helper utilities for EnergyOpti-Pro backend.
"""

import uuid
import hashlib
import secrets
import string
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def generate_api_key(length: int = 64) -> str:
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def calculate_hash(data: str, algorithm: str = "sha256") -> str:
    """Calculate hash of data using specified algorithm"""
    if algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

def sanitize_input(input_string: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not input_string:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}', '[', ']']
    sanitized = input_string
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data like API keys or passwords"""
    if not data or len(data) <= visible_chars:
        return "*" * len(data) if data else ""
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)

def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate JSON data structure and return validation result"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    return {
        "valid": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "total_fields": len(data),
        "required_fields": len(required_fields)
    }

def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def flatten_dict(data: Dict[str, Any], parent_key: str = "", separator: str = "_") -> Dict[str, Any]:
    """Flatten nested dictionary"""
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)

def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def remove_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {key: value for key, value in data.items() if value is not None}

def get_nested_value(data: Dict[str, Any], path: str, default: Any = None) -> Any:
    """Get nested value from dictionary using dot notation path"""
    keys = path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current

def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> Dict[str, Any]:
    """Set nested value in dictionary using dot notation path"""
    keys = path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data

def format_duration_human(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"

def is_business_day(date: datetime) -> bool:
    """Check if date is a business day (Monday-Friday)"""
    return date.weekday() < 5

def get_next_business_day(date: datetime) -> datetime:
    """Get next business day from given date"""
    next_day = date + timedelta(days=1)
    while not is_business_day(next_day):
        next_day += timedelta(days=1)
    return next_day

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0
    
    return ((new_value - old_value) / old_value) * 100

def round_to_significant_digits(value: float, significant_digits: int = 3) -> float:
    """Round number to specified significant digits"""
    if value == 0:
        return 0.0
    
    import math
    magnitude = math.floor(math.log10(abs(value)))
    scale = 10 ** (magnitude - significant_digits + 1)
    return round(value / scale) * scale
