"""
Internationalization (i18n) and localization (l10n) support for EnergyOpti-Pro.

This module provides comprehensive support for Arabic language, RTL layout,
Islamic calendar integration, and multi-language content management.
"""

import os
import gettext
from typing import Optional, Dict, Any, List
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, date
import locale
from pathlib import Path
import json

# Islamic calendar support
try:
    import hijri_converter
    HIJRI_AVAILABLE = True
except ImportError:
    HIJRI_AVAILABLE = False

class LocaleMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic language detection and locale setting.
    
    This middleware:
    1. Detects user's preferred language from headers
    2. Sets the appropriate locale for the request
    3. Provides RTL detection for Arabic
    4. Integrates Islamic calendar support
    """
    
    def __init__(self, app, default_locale: str = "en", supported_locales: List[str] = None):
        super().__init__(app)
        self.default_locale = default_locale
        self.supported_locales = supported_locales or ["en", "ar"]
        
        # Initialize gettext translations
        self._setup_translations()
        
        # Islamic calendar configuration
        self.islamic_calendar = IslamicCalendar() if HIJRI_AVAILABLE else None
    
    def _setup_translations(self):
        """Setup gettext translations for supported languages."""
        self.translations = {}
        
        # Get the locales directory path
        locales_dir = Path(__file__).parent.parent / "locales"
        
        for lang in self.supported_locales:
            try:
                # Create translation object
                translation = gettext.translation(
                    'messages',
                    localedir=str(locales_dir),
                    languages=[lang] if lang != self.default_locale else None
                )
                self.translations[lang] = translation
            except FileNotFoundError:
                # Fallback to default if translation files not found
                self.translations[lang] = gettext.NullTranslations()
    
    async def dispatch(self, request: Request, call_next):
        """Process request and set locale context."""
        # Detect language from headers
        lang = self._detect_language(request)
        
        # Set locale for this request
        self._set_locale(lang)
        
        # Add locale info to request state
        request.state.locale = lang
        request.state.is_rtl = lang == "ar"
        request.state.translation = self.translations.get(lang, self.translations.get(self.default_locale))
        
        # Process request
        response = await call_next(request)
        
        # Add locale headers to response
        response.headers["Content-Language"] = lang
        if lang == "ar":
            response.headers["X-Text-Direction"] = "rtl"
        
        return response
    
    def _detect_language(self, request: Request) -> str:
        """Detect user's preferred language from request headers."""
        # Check Accept-Language header
        accept_lang = request.headers.get("Accept-Language", "")
        
        if accept_lang:
            # Parse Accept-Language header (e.g., "ar,en;q=0.9,en-US;q=0.8")
            languages = []
            for lang_part in accept_lang.split(","):
                lang_part = lang_part.strip()
                if ";" in lang_part:
                    lang, q = lang_part.split(";")
                    q = float(q.replace("q=", ""))
                    languages.append((lang.split("-")[0], q))
                else:
                    languages.append((lang_part.split("-")[0], 1.0))
            
            # Sort by quality and find first supported language
            languages.sort(key=lambda x: x[1], reverse=True)
            for lang, _ in languages:
                if lang in self.supported_locales:
                    return lang
        
        # Check X-Language header (custom header for explicit language selection)
        custom_lang = request.headers.get("X-Language")
        if custom_lang and custom_lang in self.supported_locales:
            return custom_lang
        
        # Check query parameter
        query_lang = request.query_params.get("lang")
        if query_lang and query_lang in self.supported_locales:
            return query_lang
        
        # Default to English
        return self.default_locale
    
    def _set_locale(self, lang: str):
        """Set the locale for the current request."""
        try:
            if lang == "ar":
                locale.setlocale(locale.LC_ALL, "ar_SA.UTF-8")
            else:
                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except locale.Error:
            # Fallback if locale not available
            pass

class IslamicCalendar:
    """Islamic calendar utilities for Arabic localization."""
    
    def __init__(self):
        self.hijri_converter = hijri_converter
    
    def gregorian_to_hijri(self, gregorian_date: date) -> Dict[str, int]:
        """Convert Gregorian date to Hijri date."""
        try:
            hijri = self.hijri_converter.Gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day).to_hijri()
            return {
                "year": hijri.year,
                "month": hijri.month,
                "day": hijri.day,
                "month_name": self._get_hijri_month_name(hijri.month),
                "day_name": self._get_hijri_day_name(gregorian_date.weekday())
            }
        except Exception:
            return None
    
    def hijri_to_gregorian(self, hijri_year: int, hijri_month: int, hijri_day: int) -> date:
        """Convert Hijri date to Gregorian date."""
        try:
            gregorian = self.hijri_converter.Hijri(hijri_year, hijri_month, hijri_day).to_gregorian()
            return date(gregorian.year, gregorian.month, gregorian.day)
        except Exception:
            return None
    
    def is_ramadan(self, date_to_check: date) -> bool:
        """Check if a date falls during Ramadan (9th month of Hijri calendar)."""
        hijri = self.gregorian_to_hijri(date_to_check)
        return hijri and hijri["month"] == 9
    
    def get_ramadan_timetable(self, year: int) -> Dict[str, Any]:
        """Get Ramadan timetable for a specific year."""
        # Calculate Ramadan start and end dates
        ramadan_start = self.hijri_to_gregorian(year, 9, 1)
        ramadan_end = self.hijri_to_gregorian(year, 9, 30)
        
        if not ramadan_start or not ramadan_end:
            return None
        
        return {
            "start_date": ramadan_start.isoformat(),
            "end_date": ramadan_end.isoformat(),
            "duration_days": 30,
            "year": year
        }
    
    def _get_hijri_month_name(self, month: int) -> str:
        """Get Arabic name for Hijri month."""
        month_names = {
            1: "محرم", 2: "صفر", 3: "ربيع الأول", 4: "ربيع الثاني",
            5: "جمادى الأولى", 6: "جمادى الآخرة", 7: "رجب", 8: "شعبان",
            9: "رمضان", 10: "شوال", 11: "ذو القعدة", 12: "ذو الحجة"
        }
        return month_names.get(month, "")
    
    def _get_hijri_day_name(self, weekday: int) -> str:
        """Get Arabic name for day of week."""
        day_names = [
            "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"
        ]
        return day_names[weekday]

class LocalizationManager:
    """Manager for localization operations and utilities."""
    
    def __init__(self, default_locale: str = "en"):
        self.default_locale = default_locale
        self.islamic_calendar = IslamicCalendar() if HIJRI_AVAILABLE else None
    
    def get_text(self, key: str, locale: str = None, **kwargs) -> str:
        """Get localized text for a given key."""
        if not locale:
            locale = self.default_locale
        
        # Get translation
        translation = gettext.translation(
            'messages',
            localedir=str(Path(__file__).parent.parent / "locales"),
            languages=[locale] if locale != self.default_locale else None
        )
        
        # Get translated text
        text = translation.gettext(key)
        
        # Format with kwargs if provided
        if kwargs:
            text = text.format(**kwargs)
        
        return text
    
    def get_currency_format(self, amount: float, locale: str = "en") -> str:
        """Format currency according to locale."""
        if locale == "ar":
            # Arabic currency format (right-to-left)
            return f"{amount:,.2f} ريال"
        else:
            # English currency format
            return f"${amount:,.2f}"
    
    def get_date_format(self, date_obj: date, locale: str = "en") -> str:
        """Format date according to locale."""
        if locale == "ar":
            # Arabic date format
            hijri = self.islamic_calendar.gregorian_to_hijri(date_obj) if self.islamic_calendar else None
            if hijri:
                return f"{hijri['day']} {hijri['month_name']} {hijri['year']}"
            else:
                return date_obj.strftime("%Y/%m/%d")
        else:
            # English date format
            return date_obj.strftime("%B %d, %Y")
    
    def get_number_format(self, number: float, locale: str = "en") -> str:
        """Format numbers according to locale."""
        if locale == "ar":
            # Arabic number format (right-to-left)
            return f"{number:,.2f}"
        else:
            # English number format
            return f"{number:,.2f}"
    
    def is_rtl(self, locale: str) -> bool:
        """Check if locale uses right-to-left text direction."""
        return locale == "ar"
    
    def get_supported_locales(self) -> List[Dict[str, Any]]:
        """Get list of supported locales with metadata."""
        return [
            {
                "code": "en",
                "name": "English",
                "native_name": "English",
                "direction": "ltr",
                "flag": "🇺🇸"
            },
            {
                "code": "ar",
                "name": "Arabic",
                "native_name": "العربية",
                "direction": "rtl",
                "flag": "🇸🇦"
            }
        ]

# Global localization manager instance
localization_manager = LocalizationManager()

# Utility functions for easy access
def get_text(key: str, locale: str = None, **kwargs) -> str:
    """Get localized text."""
    return localization_manager.get_text(key, locale, **kwargs)

def is_rtl(locale: str) -> bool:
    """Check if locale is RTL."""
    return localization_manager.is_rtl(locale)

def get_currency_format(amount: float, locale: str = "en") -> str:
    """Format currency for locale."""
    return localization_manager.get_currency_format(amount, locale)

def get_date_format(date_obj: date, locale: str = "en") -> str:
    """Format date for locale."""
    return localization_manager.get_date_format(date_obj, locale)

def get_supported_locales() -> List[Dict[str, Any]]:
    """Get supported locales."""
    return localization_manager.get_supported_locales() 