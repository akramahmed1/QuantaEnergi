"""
Comprehensive tests for Arabic i18n system.

These tests verify:
- Language detection and switching
- Islamic calendar functionality
- RTL layout support
- Arabic text formatting
- Localization features
"""

import pytest
from datetime import date, datetime
from unittest.mock import patch, MagicMock

from src.energyopti_pro.core.i18n import (
    LocaleMiddleware, IslamicCalendar, LocalizationManager,
    get_text, is_rtl, get_currency_format, get_date_format,
    get_supported_locales, localization_manager
)

class TestLocaleMiddleware:
    """Test the FastAPI locale middleware."""
    
    def test_middleware_initialization(self):
        """Test middleware initialization with default settings."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        assert middleware.default_locale == "en"
        assert middleware.supported_locales == ["en", "ar"]
        assert middleware.translations is not None
    
    def test_middleware_initialization_custom(self):
        """Test middleware initialization with custom settings."""
        app = MagicMock()
        middleware = LocaleMiddleware(
            app, 
            default_locale="ar", 
            supported_locales=["ar", "en", "fr"]
        )
        
        assert middleware.default_locale == "ar"
        assert middleware.supported_locales == ["ar", "en", "fr"]
    
    def test_language_detection_accept_language(self):
        """Test language detection from Accept-Language header."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        # Mock request with Accept-Language header
        request = MagicMock()
        request.headers = {"Accept-Language": "ar,en;q=0.9"}
        
        detected_lang = middleware._detect_language(request)
        assert detected_lang == "ar"
    
    def test_language_detection_quality_values(self):
        """Test language detection with quality values."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        # Mock request with quality values
        request = MagicMock()
        request.headers = {"Accept-Language": "en;q=0.8,ar;q=0.9,fr;q=0.7"}
        
        detected_lang = middleware._detect_language(request)
        assert detected_lang == "ar"  # Highest quality value
    
    def test_language_detection_custom_header(self):
        """Test language detection from custom X-Language header."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        # Mock request with custom header
        request = MagicMock()
        request.headers = {"X-Language": "ar"}
        
        detected_lang = middleware._detect_language(request)
        assert detected_lang == "ar"
    
    def test_language_detection_query_param(self):
        """Test language detection from query parameter."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        # Mock request with query parameter
        request = MagicMock()
        request.query_params = {"lang": "ar"}
        
        detected_lang = middleware._detect_language(request)
        assert detected_lang == "ar"
    
    def test_language_detection_fallback(self):
        """Test language detection fallback to default."""
        app = MagicMock()
        middleware = LocaleMiddleware(app)
        
        # Mock request with no language indicators
        request = MagicMock()
        request.headers = {}
        request.query_params = {}
        
        detected_lang = middleware._detect_language(request)
        assert detected_lang == "en"  # Default fallback

class TestIslamicCalendar:
    """Test Islamic calendar functionality."""
    
    def test_islamic_calendar_initialization(self):
        """Test Islamic calendar initialization."""
        calendar = IslamicCalendar()
        assert calendar.hijri_converter is not None
    
    @patch('src.energyopti_pro.core.i18n.hijri_converter')
    def test_gregorian_to_hijri_conversion(self, mock_hijri):
        """Test conversion from Gregorian to Hijri date."""
        # Mock hijri converter
        mock_gregorian = MagicMock()
        mock_hijri_instance = MagicMock()
        mock_hijri_instance.to_hijri.return_value = MagicMock(
            year=1445, month=9, day=15
        )
        mock_gregorian.return_value = mock_hijri_instance
        
        calendar = IslamicCalendar()
        calendar.hijri_converter = mock_hijri
        
        test_date = date(2024, 3, 25)
        result = calendar.gregorian_to_hijri(test_date)
        
        assert result is not None
        assert result["year"] == 1445
        assert result["month"] == 9
        assert result["day"] == 15
        assert "month_name" in result
        assert "day_name" in result
    
    @patch('src.energyopti_pro.core.i18n.hijri_converter')
    def test_hijri_to_gregorian_conversion(self, mock_hijri):
        """Test conversion from Hijri to Gregorian date."""
        # Mock hijri converter
        mock_hijri_instance = MagicMock()
        mock_hijri_instance.to_gregorian.return_value = MagicMock(
            year=2024, month=3, day=25
        )
        mock_hijri.Hijri.return_value = mock_hijri_instance
        
        calendar = IslamicCalendar()
        calendar.hijri_converter = mock_hijri
        
        result = calendar.hijri_to_gregorian(1445, 9, 15)
        
        assert result is not None
        assert result.year == 2024
        assert result.month == 3
        assert result.day == 25
    
    @patch('src.energyopti_pro.core.i18n.hijri_converter')
    def test_ramadan_detection(self, mock_hijri):
        """Test Ramadan detection."""
        # Mock hijri converter
        mock_gregorian = MagicMock()
        mock_hijri_instance = MagicMock()
        mock_hijri_instance.to_hijri.return_value = MagicMock(
            year=1445, month=9, day=15
        )
        mock_gregorian.return_value = mock_hijri_instance
        
        calendar = IslamicCalendar()
        calendar.hijri_converter = mock_hijri
        
        test_date = date(2024, 3, 25)
        is_ramadan = calendar.is_ramadan(test_date)
        
        assert is_ramadan is True
    
    def test_ramadan_timetable(self):
        """Test Ramadan timetable generation."""
        calendar = IslamicCalendar()
        
        # Mock the conversion methods
        with patch.object(calendar, 'hijri_to_gregorian') as mock_convert:
            mock_convert.side_effect = [
                date(2024, 3, 10),  # Start date
                date(2024, 4, 9)    # End date
            ]
            
            result = calendar.get_ramadan_timetable(1445)
            
            assert result is not None
            assert result["year"] == 1445
            assert result["duration_days"] == 30
            assert "start_date" in result
            assert "end_date" in result
    
    def test_hijri_month_names(self):
        """Test Arabic month names."""
        calendar = IslamicCalendar()
        
        # Test some month names
        assert calendar._get_hijri_month_name(1) == "محرم"
        assert calendar._get_hijri_month_name(9) == "رمضان"
        assert calendar._get_hijri_month_name(12) == "ذو الحجة"
    
    def test_hijri_day_names(self):
        """Test Arabic day names."""
        calendar = IslamicCalendar()
        
        # Test some day names (0 = Monday in Python)
        assert calendar._get_hijri_day_name(0) == "الاثنين"
        assert calendar._get_hijri_day_name(4) == "الجمعة"
        assert calendar._get_hijri_day_name(6) == "الأحد"

class TestLocalizationManager:
    """Test the localization manager."""
    
    def test_localization_manager_initialization(self):
        """Test localization manager initialization."""
        manager = LocalizationManager()
        
        assert manager.default_locale == "en"
        assert manager.islamic_calendar is not None
    
    def test_get_text_basic(self):
        """Test basic text retrieval."""
        manager = LocalizationManager()
        
        # This will use the default gettext behavior
        # In a real test environment, we'd have actual translation files
        text = manager.get_text("test_key")
        assert text == "test_key"  # Default behavior when no translation
    
    def test_get_text_with_parameters(self):
        """Test text retrieval with parameters."""
        manager = LocalizationManager()
        
        # Test with format parameters
        text = manager.get_text("Hello {name}", "en", name="World")
        assert text == "Hello World"
    
    def test_currency_formatting(self):
        """Test currency formatting for different locales."""
        manager = LocalizationManager()
        
        # Test English formatting
        en_format = manager.get_currency_format(1234.56, "en")
        assert "$1,234.56" in en_format
        
        # Test Arabic formatting
        ar_format = manager.get_currency_format(1234.56, "ar")
        assert "ريال" in ar_format
        assert "1,234.56" in ar_format
    
    def test_date_formatting(self):
        """Test date formatting for different locales."""
        manager = LocalizationManager()
        
        test_date = date(2024, 3, 25)
        
        # Test English formatting
        en_format = manager.get_date_format(test_date, "en")
        assert "March 25, 2024" in en_format
        
        # Test Arabic formatting (with mocked Islamic calendar)
        with patch.object(manager.islamic_calendar, 'gregorian_to_hijri') as mock_convert:
            mock_convert.return_value = {
                "day": 15,
                "month_name": "رمضان",
                "year": 1445
            }
            
            ar_format = manager.get_date_format(test_date, "ar")
            assert "رمضان" in ar_format
    
    def test_number_formatting(self):
        """Test number formatting for different locales."""
        manager = LocalizationManager()
        
        # Test English formatting
        en_format = manager.get_number_format(1234.56, "en")
        assert "1,234.56" in en_format
        
        # Test Arabic formatting
        ar_format = manager.get_number_format(1234.56, "ar")
        assert "1,234.56" in ar_format
    
    def test_rtl_detection(self):
        """Test RTL detection."""
        manager = LocalizationManager()
        
        assert manager.is_rtl("en") is False
        assert manager.is_rtl("ar") is True
        assert manager.is_rtl("fr") is False
    
    def test_supported_locales(self):
        """Test supported locales list."""
        manager = LocalizationManager()
        
        locales = manager.get_supported_locales()
        
        assert len(locales) == 2
        assert any(loc["code"] == "en" for loc in locales)
        assert any(loc["code"] == "ar" for loc in locales)
        
        # Check Arabic locale properties
        arabic_locale = next(loc for loc in locales if loc["code"] == "ar")
        assert arabic_locale["direction"] == "rtl"
        assert arabic_locale["native_name"] == "العربية"
        assert arabic_locale["flag"] == "🇸🇦"

class TestUtilityFunctions:
    """Test utility functions for easy access."""
    
    def test_get_text_utility(self):
        """Test get_text utility function."""
        # Test basic functionality
        text = get_text("test_key")
        assert text == "test_key"
        
        # Test with parameters
        text = get_text("Hello {name}", "en", name="World")
        assert text == "Hello World"
    
    def test_is_rtl_utility(self):
        """Test is_rtl utility function."""
        assert is_rtl("en") is False
        assert is_rtl("ar") is True
    
    def test_get_currency_format_utility(self):
        """Test get_currency_format utility function."""
        # Test English
        en_format = get_currency_format(1234.56, "en")
        assert "$1,234.56" in en_format
        
        # Test Arabic
        ar_format = get_currency_format(1234.56, "ar")
        assert "ريال" in ar_format
    
    def test_get_date_format_utility(self):
        """Test get_date_format utility function."""
        test_date = date(2024, 3, 25)
        
        # Test English
        en_format = get_date_format(test_date, "en")
        assert "March 25, 2024" in en_format
    
    def test_get_supported_locales_utility(self):
        """Test get_supported_locales utility function."""
        locales = get_supported_locales()
        
        assert len(locales) == 2
        assert any(loc["code"] == "en" for loc in locales)
        assert any(loc["code"] == "ar" for loc in locales)

class TestArabicSpecificFeatures:
    """Test Arabic-specific features and capabilities."""
    
    def test_arabic_text_processing(self):
        """Test Arabic text processing capabilities."""
        # Test RTL detection
        assert is_rtl("ar") is True
        
        # Test Arabic locale metadata
        locales = get_supported_locales()
        arabic_locale = next(loc for loc in locales if loc["code"] == "ar")
        
        assert arabic_locale["direction"] == "rtl"
        assert arabic_locale["native_name"] == "العربية"
        assert arabic_locale["flag"] == "🇸🇦"
    
    def test_islamic_calendar_integration(self):
        """Test Islamic calendar integration."""
        # Test that Islamic calendar is available
        assert localization_manager.islamic_calendar is not None
        
        # Test calendar functionality
        calendar = localization_manager.islamic_calendar
        assert hasattr(calendar, 'gregorian_to_hijri')
        assert hasattr(calendar, 'hijri_to_gregorian')
        assert hasattr(calendar, 'is_ramadan')
        assert hasattr(calendar, 'get_ramadan_timetable')
    
    def test_arabic_currency_support(self):
        """Test Arabic currency support."""
        # Test Arabic currency formatting
        ar_format = get_currency_format(1234.56, "ar")
        assert "ريال" in ar_format
        
        # Test that it's different from English
        en_format = get_currency_format(1234.56, "en")
        assert ar_format != en_format
    
    def test_rtl_layout_support(self):
        """Test RTL layout support."""
        # Test RTL detection
        assert is_rtl("ar") is True
        assert is_rtl("en") is False
        
        # Test layout information
        locales = get_supported_locales()
        arabic_locale = next(loc for loc in locales if loc["code"] == "ar")
        
        assert arabic_locale["direction"] == "rtl"
        assert arabic_locale["code"] == "ar"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 