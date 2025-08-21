"""
Arabic i18n and Islamic calendar API endpoints for EnergyOpti-Pro.

This module provides endpoints for:
- Language switching and localization
- Islamic calendar operations
- RTL layout support
- Arabic-specific features
"""

from fastapi import APIRouter, Depends, Request, Query
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from ...core.i18n import (
    get_text, is_rtl, get_currency_format, get_date_format,
    get_supported_locales, localization_manager
)
from ...api.dependencies import get_current_user, require_trader
from ...db.schemas import User

router = APIRouter()

# Pydantic Models
class LanguageSwitchRequest(BaseModel):
    language: str
    user_id: Optional[int] = None

class IslamicDateRequest(BaseModel):
    gregorian_date: date
    include_hijri: bool = True
    include_ramadan_info: bool = False

class RamadanTimetableRequest(BaseModel):
    year: int
    include_prayer_times: bool = True

class LocalizedTextRequest(BaseModel):
    text_key: str
    language: str
    parameters: Optional[Dict[str, Any]] = None

# Language and Localization Endpoints
@router.get("/languages", response_model=List[Dict[str, Any]])
async def get_supported_languages():
    """Get list of supported languages with metadata."""
    return get_supported_locales()

@router.post("/language/switch", response_model=Dict[str, Any])
async def switch_language(
    request: LanguageSwitchRequest,
    current_user: User = Depends(require_trader)
):
    """Switch user's preferred language."""
    
    if request.language not in ["en", "ar"]:
        return {
            "success": False,
            "message": "Unsupported language",
            "supported_languages": ["en", "ar"]
        }
    
    # In a real implementation, save user's language preference to database
    # For now, return success response
    return {
        "success": True,
        "message": get_text("Language changed successfully", request.language),
        "language": request.language,
        "is_rtl": is_rtl(request.language),
        "welcome_message": get_text("Welcome to EnergyOpti-Pro", request.language)
    }

@router.get("/text/{text_key}", response_model=Dict[str, Any])
async def get_localized_text(
    text_key: str,
    language: str = Query("en"),
    current_user: User = Depends(require_trader)
):
    """Get localized text for a given key and language."""
    
    if language not in ["en", "ar"]:
        return {
            "success": False,
            "message": "Unsupported language",
            "supported_languages": ["en", "ar"]
        }
    
    try:
        localized_text = get_text(text_key, language)
        return {
            "success": True,
            "text_key": text_key,
            "language": language,
            "localized_text": localized_text,
            "is_rtl": is_rtl(language)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting localized text: {str(e)}",
            "text_key": text_key,
            "language": language
        }

@router.post("/text/batch", response_model=Dict[str, Any])
async def get_batch_localized_texts(
    request: LocalizedTextRequest,
    current_user: User = Depends(require_trader)
):
    """Get multiple localized texts in batch."""
    
    if request.language not in ["en", "ar"]:
        return {
            "success": False,
            "message": "Unsupported language",
            "supported_languages": ["en", "ar"]
        }
    
    try:
        localized_text = get_text(
            request.text_key, 
            request.language, 
            **(request.parameters or {})
        )
        
        return {
            "success": True,
            "text_key": request.text_key,
            "language": request.language,
            "localized_text": localized_text,
            "is_rtl": is_rtl(request.language),
            "parameters": request.parameters
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting localized text: {str(e)}",
            "text_key": request.text_key,
            "language": request.language
        }

# Islamic Calendar Endpoints
@router.post("/islamic/convert", response_model=Dict[str, Any])
async def convert_to_islamic_date(
    request: IslamicDateRequest,
    current_user: User = Depends(require_trader)
):
    """Convert Gregorian date to Islamic (Hijri) date."""
    
    try:
        islamic_calendar = localization_manager.islamic_calendar
        
        if not islamic_calendar:
            return {
                "success": False,
                "message": "Islamic calendar not available",
                "gregorian_date": request.gregorian_date.isoformat()
            }
        
        # Convert to Hijri
        hijri_date = islamic_calendar.gregorian_to_hijri(request.gregorian_date)
        
        if not hijri_date:
            return {
                "success": False,
                "message": "Error converting date",
                "gregorian_date": request.gregorian_date.isoformat()
            }
        
        # Check if it's Ramadan
        is_ramadan = islamic_calendar.is_ramadan(request.gregorian_date)
        
        result = {
            "success": True,
            "gregorian_date": request.gregorian_date.isoformat(),
            "hijri_date": hijri_date,
            "is_ramadan": is_ramadan
        }
        
        # Add Ramadan info if requested
        if request.include_ramadan_info and is_ramadan:
            current_year = request.gregorian_date.year
            ramadan_info = islamic_calendar.get_ramadan_timetable(current_year)
            if ramadan_info:
                result["ramadan_info"] = ramadan_info
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error converting date: {str(e)}",
            "gregorian_date": request.gregorian_date.isoformat()
        }

@router.get("/islamic/ramadan/{year}", response_model=Dict[str, Any])
async def get_ramadan_timetable(
    year: int,
    include_prayer_times: bool = Query(True),
    current_user: User = Depends(require_trader)
):
    """Get Ramadan timetable for a specific year."""
    
    try:
        islamic_calendar = localization_manager.islamic_calendar
        
        if not islamic_calendar:
            return {
                "success": False,
                "message": "Islamic calendar not available",
                "year": year
            }
        
        ramadan_info = islamic_calendar.get_ramadan_timetable(year)
        
        if not ramadan_info:
            return {
                "success": False,
                "message": "Could not calculate Ramadan dates for this year",
                "year": year
            }
        
        result = {
            "success": True,
            "year": year,
            "ramadan_info": ramadan_info
        }
        
        # Add prayer times if requested (mock data for now)
        if include_prayer_times:
            result["prayer_times"] = {
                "fajr": "04:30",
                "dhuhr": "12:15",
                "asr": "15:45",
                "maghrib": "18:30",
                "isha": "20:00"
            }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting Ramadan timetable: {str(e)}",
            "year": year
        }

@router.get("/islamic/current", response_model=Dict[str, Any])
async def get_current_islamic_date(
    current_user: User = Depends(require_trader)
):
    """Get current Islamic date."""
    
    try:
        islamic_calendar = localization_manager.islamic_calendar
        
        if not islamic_calendar:
            return {
                "success": False,
                "message": "Islamic calendar not available"
            }
        
        today = date.today()
        hijri_date = islamic_calendar.gregorian_to_hijri(today)
        is_ramadan = islamic_calendar.is_ramadan(today)
        
        return {
            "success": True,
            "gregorian_date": today.isoformat(),
            "hijri_date": hijri_date,
            "is_ramadan": is_ramadan,
            "current_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error getting current Islamic date: {str(e)}"
        }

# RTL and Layout Support
@router.get("/layout/rtl", response_model=Dict[str, Any])
async def get_rtl_layout_info(
    language: str = Query("en"),
    current_user: User = Depends(require_trader)
):
    """Get RTL layout information for a language."""
    
    is_rtl_layout = is_rtl(language)
    
    return {
        "success": True,
        "language": language,
        "is_rtl": is_rtl_layout,
        "layout_direction": "rtl" if is_rtl_layout else "ltr",
        "text_alignment": "right" if is_rtl_layout else "left",
        "navigation_side": "right" if is_rtl_layout else "left"
    }

# Formatting Endpoints
@router.get("/format/currency", response_model=Dict[str, Any])
async def format_currency(
    amount: float = Query(...),
    language: str = Query("en"),
    current_user: User = Depends(require_trader)
):
    """Format currency according to locale."""
    
    try:
        formatted_currency = get_currency_format(amount, language)
        
        return {
            "success": True,
            "amount": amount,
            "language": language,
            "formatted_currency": formatted_currency,
            "is_rtl": is_rtl(language)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error formatting currency: {str(e)}",
            "amount": amount,
            "language": language
        }

@router.get("/format/date", response_model=Dict[str, Any])
async def format_date(
    date_str: str = Query(...),
    language: str = Query("en"),
    current_user: User = Depends(require_trader)
):
    """Format date according to locale."""
    
    try:
        # Parse date string
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        formatted_date = get_date_format(date_obj, language)
        
        return {
            "success": True,
            "date": date_str,
            "parsed_date": date_obj.isoformat(),
            "language": language,
            "formatted_date": formatted_date,
            "is_rtl": is_rtl(language)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Error formatting date: {str(e)}",
            "date": date_str,
            "language": language
        }

# Arabic-Specific Features
@router.get("/arabic/features", response_model=Dict[str, Any])
async def get_arabic_features(
    current_user: User = Depends(require_trader)
):
    """Get Arabic-specific features and capabilities."""
    
    return {
        "success": True,
        "language": "ar",
        "features": {
            "rtl_support": True,
            "islamic_calendar": True,
            "arabic_numerals": True,
            "arabic_currency": True,
            "ramadan_timetable": True,
            "prayer_times": True,
            "hijri_dates": True,
            "arabic_validation": True
        },
        "islamic_calendar_available": localization_manager.islamic_calendar is not None,
        "supported_currencies": ["SAR", "AED", "QAR", "KWD", "BHD", "OMR"],
        "supported_regions": ["ME", "GCC", "Levant", "North Africa"]
    }

# Health Check for i18n System
@router.get("/health", response_model=Dict[str, Any])
async def i18n_health_check():
    """Health check for the i18n system."""
    
    try:
        # Test basic functionality
        en_text = get_text("Welcome", "en")
        ar_text = get_text("Welcome", "ar")
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "english_support": bool(en_text),
                "arabic_support": bool(ar_text),
                "islamic_calendar": localization_manager.islamic_calendar is not None,
                "rtl_detection": True
            },
            "test_results": {
                "english_welcome": en_text,
                "arabic_welcome": ar_text,
                "rtl_detection": {
                    "en": is_rtl("en"),
                    "ar": is_rtl("ar")
                }
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        } 