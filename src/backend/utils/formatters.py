"""
Formatting utilities for EnergyOpti-Pro backend.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import locale
import structlog

logger = structlog.get_logger()

def format_currency(amount: float, currency: str = "USD", locale_code: str = "en_US") -> str:
    """Format currency amount with proper locale formatting"""
    try:
        locale.setlocale(locale.LC_ALL, locale_code)
        return locale.currency(amount, grouping=True, symbol=currency)
    except (locale.Error, ValueError):
        # Fallback formatting
        return f"{currency} {amount:,.2f}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format percentage value"""
    return f"{value:.{decimal_places}f}%"

def format_timestamp(timestamp: Union[str, datetime], format_type: str = "iso") -> str:
    """Format timestamp in various formats"""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if format_type == "iso":
        return timestamp.isoformat()
    elif format_type == "human":
        return timestamp.strftime("%B %d, %Y at %I:%M %p")
    elif format_type == "short":
        return timestamp.strftime("%Y-%m-%d %H:%M")
    elif format_type == "date_only":
        return timestamp.strftime("%Y-%m-%d")
    else:
        return timestamp.isoformat()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def format_number_with_commas(number: Union[int, float]) -> str:
    """Format number with comma separators"""
    return f"{number:,}"

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        return f"{days}d {remaining_hours}h"

def format_portfolio_metrics(metrics: Dict[str, Any]) -> Dict[str, str]:
    """Format portfolio metrics for display"""
    formatted = {}
    
    for key, value in metrics.items():
        if isinstance(value, float):
            if "return" in key.lower() or "ratio" in key.lower():
                formatted[key] = format_percentage(value * 100, 2)
            elif "volatility" in key.lower():
                formatted[key] = format_percentage(value * 100, 2)
            elif "score" in key.lower():
                formatted[key] = f"{value:.1f}"
            else:
                formatted[key] = f"{value:.4f}"
        else:
            formatted[key] = str(value)
    
    return formatted

def format_trading_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format trading data for display"""
    formatted_data = []
    
    for item in data:
        formatted_item = {}
        for key, value in item.items():
            if key == "timestamp":
                formatted_item[key] = format_timestamp(value, "human")
            elif key == "price":
                formatted_item[key] = format_currency(value, "USD")
            elif key == "volume":
                formatted_item[key] = format_number_with_commas(value)
            elif key == "change":
                if isinstance(value, (int, float)):
                    formatted_item[key] = format_percentage(value * 100, 2)
                else:
                    formatted_item[key] = value
            else:
                formatted_item[key] = value
        
        formatted_data.append(formatted_item)
    
    return formatted_data

def format_error_message(error: Exception, include_traceback: bool = False) -> Dict[str, Any]:
    """Format error message for API response"""
    formatted = {
        "error": str(error),
        "error_type": type(error).__name__,
        "timestamp": format_timestamp(datetime.now(), "iso")
    }
    
    if include_traceback:
        import traceback
        formatted["traceback"] = traceback.format_exc()
    
    return formatted

def format_success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """Format success response for API"""
    return {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": format_timestamp(datetime.now(), "iso")
    }

def format_pagination_response(data: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
    """Format paginated response for API"""
    total_pages = (total + per_page - 1) // per_page
    
    return {
        "data": data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        },
        "timestamp": format_timestamp(datetime.now(), "iso")
    }
