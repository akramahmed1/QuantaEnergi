"""
Internationalization (i18n) system for EnergyOpti-Pro.

Supports multiple languages including Arabic, English, and other regional languages
for the Middle East market expansion.
"""

import json
import os
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import structlog
from babel import Locale, dates, numbers
from babel.messages import Catalog, Message
from babel.messages.pofile import read_po, write_po
from babel.messages.mofile import write_mo
import yaml

logger = structlog.get_logger()

class I18nService:
    """Internationalization service for EnergyOpti-Pro."""
    
    def __init__(self, default_locale: str = "en", locales_dir: str = "locales"):
        self.default_locale = default_locale
        self.locales_dir = Path(locales_dir)
        self.supported_locales = ["en", "ar", "fr", "de", "es", "tr", "ur", "fa"]
        self.current_locale = default_locale
        self.translations: Dict[str, Dict[str, str]] = {}
        self.catalogs: Dict[str, Catalog] = {}
        
        # Initialize locales directory
        self.locales_dir.mkdir(exist_ok=True)
        
        # Load translations
        self._load_translations()
        self._load_catalogs()
    
    def _load_translations(self):
        """Load translation files for all supported locales."""
        for locale in self.supported_locales:
            locale_dir = self.locales_dir / locale
            locale_dir.mkdir(exist_ok=True)
            
            # Load JSON translations
            json_file = locale_dir / "translations.json"
            if json_file.exists():
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.translations[locale] = json.load(f)
            else:
                # Create default translations
                self.translations[locale] = self._get_default_translations(locale)
                self._save_translations(locale)
    
    def _load_catalogs(self):
        """Load Babel message catalogs."""
        for locale in self.supported_locales:
            locale_dir = self.locales_dir / locale
            po_file = locale_dir / "LC_MESSAGES" / "messages.po"
            
            if po_file.exists():
                with open(po_file, 'r', encoding='utf-8') as f:
                    self.catalogs[locale] = read_po(f, locale=locale)
            else:
                # Create default catalog
                self.catalogs[locale] = self._create_default_catalog(locale)
                self._save_catalog(locale)
    
    def _get_default_translations(self, locale: str) -> Dict[str, str]:
        """Get default translations for a locale."""
        if locale == "ar":
            return {
                "welcome": "مرحباً بك في EnergyOpti-Pro",
                "dashboard": "لوحة التحكم",
                "trading": "التداول",
                "portfolio": "المحفظة",
                "analytics": "التحليلات",
                "settings": "الإعدادات",
                "logout": "تسجيل الخروج",
                "energy_trading": "تداول الطاقة",
                "sharia_compliant": "متوافق مع الشريعة الإسلامية",
                "quantum_optimization": "التحسين الكمي",
                "blockchain_security": "أمان البلوكتشين",
                "real_time_data": "بيانات فورية",
                "carbon_credits": "رصيد الكربون",
                "sukuk_trading": "تداول الصكوك",
                "green_bonds": "السندات الخضراء",
                "zakat_calculation": "حساب الزكاة",
                "halal_screening": "الفحص الحلال",
                "islamic_finance": "التمويل الإسلامي",
                "esg_investment": "الاستثمار المستدام",
                "market_analysis": "تحليل السوق",
                "risk_management": "إدارة المخاطر",
                "performance_tracking": "تتبع الأداء",
                "compliance_reporting": "تقارير الامتثال",
                "partnership_integration": "تكامل الشراكة",
                "white_label_solution": "الحل المخصص",
                "api_documentation": "توثيق API",
                "support": "الدعم",
                "help": "المساعدة",
                "about": "حول",
                "contact": "اتصل بنا",
                "privacy_policy": "سياسة الخصوصية",
                "terms_of_service": "شروط الخدمة"
            }
        elif locale == "fr":
            return {
                "welcome": "Bienvenue sur EnergyOpti-Pro",
                "dashboard": "Tableau de bord",
                "trading": "Trading",
                "portfolio": "Portefeuille",
                "analytics": "Analyses",
                "settings": "Paramètres",
                "logout": "Déconnexion",
                "energy_trading": "Trading d'énergie",
                "sharia_compliant": "Conforme à la charia",
                "quantum_optimization": "Optimisation quantique",
                "blockchain_security": "Sécurité blockchain",
                "real_time_data": "Données en temps réel",
                "carbon_credits": "Crédits carbone",
                "sukuk_trading": "Trading de sukuk",
                "green_bonds": "Obligations vertes",
                "zakat_calculation": "Calcul de la zakat",
                "halal_screening": "Filtrage halal",
                "islamic_finance": "Finance islamique",
                "esg_investment": "Investissement ESG",
                "market_analysis": "Analyse de marché",
                "risk_management": "Gestion des risques",
                "performance_tracking": "Suivi des performances",
                "compliance_reporting": "Rapports de conformité",
                "partnership_integration": "Intégration de partenariat",
                "white_label_solution": "Solution white-label",
                "api_documentation": "Documentation API",
                "support": "Support",
                "help": "Aide",
                "about": "À propos",
                "contact": "Contact",
                "privacy_policy": "Politique de confidentialité",
                "terms_of_service": "Conditions de service"
            }
        else:  # English and other languages
            return {
                "welcome": "Welcome to EnergyOpti-Pro",
                "dashboard": "Dashboard",
                "trading": "Trading",
                "portfolio": "Portfolio",
                "analytics": "Analytics",
                "settings": "Settings",
                "logout": "Logout",
                "energy_trading": "Energy Trading",
                "sharia_compliant": "Sharia Compliant",
                "quantum_optimization": "Quantum Optimization",
                "blockchain_security": "Blockchain Security",
                "real_time_data": "Real-time Data",
                "carbon_credits": "Carbon Credits",
                "sukuk_trading": "Sukuk Trading",
                "green_bonds": "Green Bonds",
                "zakat_calculation": "Zakat Calculation",
                "halal_screening": "Halal Screening",
                "islamic_finance": "Islamic Finance",
                "esg_investment": "ESG Investment",
                "market_analysis": "Market Analysis",
                "risk_management": "Risk Management",
                "performance_tracking": "Performance Tracking",
                "compliance_reporting": "Compliance Reporting",
                "partnership_integration": "Partnership Integration",
                "white_label_solution": "White-label Solution",
                "api_documentation": "API Documentation",
                "support": "Support",
                "help": "Help",
                "about": "About",
                "contact": "Contact",
                "privacy_policy": "Privacy Policy",
                "terms_of_service": "Terms of Service"
            }
    
    def _create_default_catalog(self, locale: str) -> Catalog:
        """Create a default Babel message catalog."""
        catalog = Catalog(locale=locale)
        
        # Add default messages
        default_translations = self._get_default_translations(locale)
        for msg_id, msg_string in default_translations.items():
            message = Message(msg_id, msg_string)
            catalog.add(message)
        
        return catalog
    
    def _save_translations(self, locale: str):
        """Save translations to JSON file."""
        locale_dir = self.locales_dir / locale
        locale_dir.mkdir(exist_ok=True)
        
        json_file = locale_dir / "translations.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.translations[locale], f, ensure_ascii=False, indent=2)
    
    def _save_catalog(self, locale: str):
        """Save Babel message catalog."""
        locale_dir = self.locales_dir / locale / "LC_MESSAGES"
        locale_dir.mkdir(parents=True, exist_ok=True)
        
        po_file = locale_dir / "messages.po"
        mo_file = locale_dir / "messages.mo"
        
        with open(po_file, 'w', encoding='utf-8') as f:
            write_po(f, self.catalogs[locale])
        
        with open(mo_file, 'wb') as f:
            write_mo(f, self.catalogs[locale])
    
    def set_locale(self, locale: str):
        """Set the current locale."""
        if locale in self.supported_locales:
            self.current_locale = locale
            logger.info(f"Locale changed to {locale}")
        else:
            logger.warning(f"Unsupported locale: {locale}, falling back to {self.default_locale}")
            self.current_locale = self.default_locale
    
    def get_text(self, key: str, locale: Optional[str] = None) -> str:
        """Get translated text for a key."""
        target_locale = locale or self.current_locale
        
        if target_locale in self.translations and key in self.translations[target_locale]:
            return self.translations[target_locale][key]
        
        # Fallback to default locale
        if key in self.translations[self.default_locale]:
            return self.translations[self.default_locale][key]
        
        # Return key if no translation found
        return key
    
    def format_date(self, date: datetime, locale: Optional[str] = None, format: str = "medium") -> str:
        """Format date according to locale."""
        target_locale = locale or self.current_locale
        try:
            locale_obj = Locale(target_locale)
            return dates.format_date(date, format=format, locale=locale_obj)
        except Exception as e:
            logger.error(f"Failed to format date for locale {target_locale}: {e}")
            return date.strftime("%Y-%m-%d")
    
    def format_number(self, number: Union[int, float], locale: Optional[str] = None) -> str:
        """Format number according to locale."""
        target_locale = locale or self.current_locale
        try:
            locale_obj = Locale(target_locale)
            return numbers.format_number(number, locale=locale_obj)
        except Exception as e:
            logger.error(f"Failed to format number for locale {target_locale}: {e}")
            return str(number)
    
    def format_currency(self, amount: float, currency: str, locale: Optional[str] = None) -> str:
        """Format currency according to locale."""
        target_locale = locale or self.current_locale
        try:
            locale_obj = Locale(target_locale)
            return numbers.format_currency(amount, currency, locale=locale_obj)
        except Exception as e:
            logger.error(f"Failed to format currency for locale {target_locale}: {e}")
            return f"{amount:.2f} {currency}"
    
    def get_locale_info(self, locale: str) -> Dict[str, Any]:
        """Get information about a locale."""
        try:
            locale_obj = Locale(locale)
            return {
                "locale": locale,
                "language": locale_obj.language,
                "territory": locale_obj.territory,
                "display_name": locale_obj.display_name,
                "english_name": locale_obj.english_name,
                "date_formats": {
                    "short": dates.get_date_format("short", locale=locale_obj).pattern,
                    "medium": dates.get_date_format("medium", locale=locale_obj).pattern,
                    "long": dates.get_date_format("long", locale=locale_obj).pattern
                },
                "number_formats": {
                    "decimal": numbers.get_decimal_format(locale=locale_obj).pattern,
                    "currency": numbers.get_currency_format(locale=locale_obj).pattern
                }
            }
        except Exception as e:
            logger.error(f"Failed to get locale info for {locale}: {e}")
            return {"locale": locale, "error": str(e)}
    
    def add_translation(self, key: str, translations: Dict[str, str]):
        """Add or update translations for a key."""
        for locale, text in translations.items():
            if locale in self.supported_locales:
                if locale not in self.translations:
                    self.translations[locale] = {}
                self.translations[locale][key] = text
        
        # Save updated translations
        for locale in translations.keys():
            if locale in self.supported_locales:
                self._save_translations(locale)
    
    def remove_translation(self, key: str, locales: Optional[List[str]] = None):
        """Remove translations for a key."""
        target_locales = locales or self.supported_locales
        
        for locale in target_locales:
            if locale in self.translations and key in self.translations[locale]:
                del self.translations[locale][key]
                self._save_translations(locale)
    
    def export_translations(self, locale: str, format: str = "json") -> str:
        """Export translations for a locale."""
        if locale not in self.translations:
            raise ValueError(f"Locale {locale} not found")
        
        if format == "json":
            return json.dumps(self.translations[locale], ensure_ascii=False, indent=2)
        elif format == "yaml":
            return yaml.dump(self.translations[locale], default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_translations(self, locale: str, data: str, format: str = "json"):
        """Import translations for a locale."""
        if format == "json":
            translations = json.loads(data)
        elif format == "yaml":
            translations = yaml.safe_load(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        if locale not in self.supported_locales:
            raise ValueError(f"Unsupported locale: {locale}")
        
        self.translations[locale].update(translations)
        self._save_translations(locale)
        logger.info(f"Imported {len(translations)} translations for locale {locale}")
    
    def get_missing_translations(self, locale: str) -> List[str]:
        """Get keys that are missing translations for a locale."""
        if locale not in self.translations:
            return []
        
        default_keys = set(self.translations[self.default_locale].keys())
        locale_keys = set(self.translations[locale].keys())
        
        return list(default_keys - locale_keys)
    
    def validate_translations(self, locale: str) -> Dict[str, Any]:
        """Validate translations for a locale."""
        if locale not in self.translations:
            return {"valid": False, "error": f"Locale {locale} not found"}
        
        validation_result = {
            "valid": True,
            "locale": locale,
            "total_keys": len(self.translations[self.default_locale]),
            "translated_keys": len(self.translations[locale]),
            "missing_keys": [],
            "empty_translations": [],
            "warnings": []
        }
        
        # Check for missing translations
        missing_keys = self.get_missing_translations(locale)
        validation_result["missing_keys"] = missing_keys
        
        if missing_keys:
            validation_result["valid"] = False
            validation_result["warnings"].append(f"Missing {len(missing_keys)} translations")
        
        # Check for empty translations
        for key, value in self.translations[locale].items():
            if not value or value.strip() == "":
                validation_result["empty_translations"].append(key)
                validation_result["warnings"].append(f"Empty translation for key: {key}")
        
        if validation_result["empty_translations"]:
            validation_result["valid"] = False
        
        return validation_result
    
    async def auto_translate(self, key: str, target_locale: str, source_text: str) -> str:
        """Auto-translate text using external translation service."""
        # This would integrate with Google Translate, DeepL, or other services
        # For now, return the source text
        logger.info(f"Auto-translation requested for key '{key}' to locale '{target_locale}'")
        return source_text
    
    def get_rtl_support(self, locale: str) -> bool:
        """Check if locale supports right-to-left text."""
        rtl_locales = ["ar", "fa", "ur", "he"]
        return locale in rtl_locales
    
    def get_text_direction(self, locale: str) -> str:
        """Get text direction for a locale."""
        return "rtl" if self.get_rtl_support(locale) else "ltr"

# Global i18n service instance
i18n_service = I18nService()

# Convenience functions
def get_text(key: str, locale: Optional[str] = None) -> str:
    """Get translated text for a key."""
    return i18n_service.get_text(key, locale)

def set_locale(locale: str):
    """Set the current locale."""
    i18n_service.set_locale(locale)

def format_date(date: datetime, locale: Optional[str] = None, format: str = "medium") -> str:
    """Format date according to locale."""
    return i18n_service.format_date(date, locale, format)

def format_number(number: Union[int, float], locale: Optional[str] = None) -> str:
    """Format number according to locale."""
    return i18n_service.format_number(number, locale)

def format_currency(amount: float, currency: str, locale: Optional[str] = None) -> str:
    """Format currency according to locale."""
    return i18n_service.format_currency(amount, currency, locale)

def get_rtl_support(locale: str) -> bool:
    """Check if locale supports right-to-left text."""
    return i18n_service.get_rtl_support(locale)

def get_text_direction(locale: str) -> str:
    """Get text direction for a locale."""
    return i18n_service.get_text_direction(locale) 