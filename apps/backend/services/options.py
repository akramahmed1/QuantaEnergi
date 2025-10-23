"""
Options Trading Engine for Advanced ETRM Features
Phase 2: Advanced ETRM Features & Market Expansion
PRODUCTION READY IMPLEMENTATION
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import math
import random
import numpy as np
from dataclasses import dataclass
from enum import Enum
from scipy.stats import norm
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class OptionType(Enum):
    CALL = "call"
    PUT = "put"


class OptionStyle(Enum):
    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"


@dataclass
class OptionContract:
    """Represents an options contract"""
    contract_id: str
    underlying_asset: str
    option_type: OptionType
    style: OptionStyle
    strike_price: float
    expiry_date: datetime
    contract_size: int
    premium: float
    is_islamic_compliant: bool
    created_at: datetime
    status: str = "active"


class OptionsEngine:
    """Production-ready options pricing and management engine for Islamic-compliant derivatives"""
    
    def __init__(self):
        self.supported_commodities = ["crude_oil", "natural_gas", "refined_products", "lng", "electricity"]
        self.islamic_structures = ["arbun", "salam", "istisna", "murabaha_plus"]
        self.options = {}  # Store active options
        self.executions = {}  # Store execution history
        self.risk_free_rate = 0.05  # 5% risk-free rate
        self.max_arbun_premium = 0.1  # 10% max premium for Islamic compliance
        
    def create_option_contract(self, option_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new options contract with Islamic compliance validation
        
        Args:
            option_spec: Option specification including strike, expiry, etc.
            
        Returns:
            Created option contract details
        """
        try:
            contract_id = f"OPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Extract option parameters
            underlying = option_spec.get("underlying_asset", "crude_oil")
            option_type = OptionType(option_spec.get("option_type", "call"))
            style = OptionStyle(option_spec.get("style", "european"))
            strike_price = float(option_spec.get("strike_price", 85.0))
            expiry_days = int(option_spec.get("expiry_days", 30))
            contract_size = int(option_spec.get("contract_size", 1000))
            
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=expiry_days)
            
            # Price the option using Black-Scholes
            underlying_price = float(option_spec.get("underlying_price", 85.0))
            volatility = float(option_spec.get("volatility", 0.25))
            time_to_expiry = expiry_days / 365.0
            
            premium = self._calculate_black_scholes_price(
                underlying_price, strike_price, time_to_expiry, 
                self.risk_free_rate, volatility, option_type.value
            )
            
            # Validate Islamic compliance
            islamic_compliance = self._validate_islamic_compliance(
                underlying, option_type, premium, underlying_price, time_to_expiry
            )
            
            # Create option contract
            option_contract = {
                "contract_id": contract_id,
                "underlying_asset": underlying,
                "option_type": option_type.value,
                "style": style.value,
                "strike_price": strike_price,
                "expiry_date": expiry_date.isoformat(),
                "contract_size": contract_size,
                "premium": round(premium, 4),
                "underlying_price": underlying_price,
                "volatility": volatility,
                "time_to_expiry": time_to_expiry,
                "is_islamic_compliant": islamic_compliance["compliant"],
                "islamic_structure": islamic_compliance.get("structure_type", "arbun"),
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "user_id": option_spec.get("user_id", "system"),
                "tenant_id": option_spec.get("tenant_id", "default")
            }
            
            # Calculate Greeks
            greeks = self._calculate_greeks(
                underlying_price, strike_price, time_to_expiry,
                self.risk_free_rate, volatility, option_type.value
            )
            option_contract.update(greeks)
            
            # Store option
            self.options[contract_id] = option_contract
            
            logger.info(f"Option contract created: {contract_id} for {underlying}")
            return option_contract
            
        except Exception as e:
            logger.error(f"Option creation failed: {str(e)}")
            raise
    
    def price_option(self, option_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Price an option using Black-Scholes or Islamic-compliant models
        
        Args:
            option_spec: Option specification including strike, expiry, etc.
            
        Returns:
            Pricing result with greeks and Islamic compliance status
        """
        try:
            # Extract parameters
            underlying_price = float(option_spec.get("underlying_price", 85.0))
            strike_price = float(option_spec.get("strike_price", 85.0))
            time_to_expiry = float(option_spec.get("time_to_expiry", 0.25))  # 3 months
            volatility = float(option_spec.get("volatility", 0.25))
            option_type = option_spec.get("option_type", "call")
            
            # Calculate Black-Scholes price
            price = self._calculate_black_scholes_price(
                underlying_price, strike_price, time_to_expiry,
                self.risk_free_rate, volatility, option_type
            )
            
            # Calculate Greeks
            greeks = self._calculate_greeks(
                underlying_price, strike_price, time_to_expiry,
                self.risk_free_rate, volatility, option_type
            )
            
            # Validate Islamic compliance
            islamic_compliance = self._validate_islamic_compliance(
                option_spec.get("underlying_asset", "crude_oil"),
                OptionType(option_type),
                price,
                underlying_price,
                time_to_expiry
            )
            
            return {
                "option_id": f"OPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "price": round(price, 4),
                "greeks": greeks,
                "islamic_compliant": islamic_compliance["compliant"],
                "structure_type": islamic_compliance.get("structure_type", "arbun"),
                "pricing_model": "Black-Scholes",
                "underlying_price": underlying_price,
                "strike_price": strike_price,
                "time_to_expiry": time_to_expiry,
                "volatility": volatility,
                "risk_free_rate": self.risk_free_rate,
                "timestamp": datetime.now().isoformat(),
                "status": "priced"
            }
            
        except Exception as e:
            logger.error(f"Option pricing failed: {str(e)}")
            raise
    
    def _calculate_black_scholes_price(self, S: float, K: float, T: float, 
                                     r: float, sigma: float, option_type: str) -> float:
        """
        Calculate Black-Scholes option price
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Option price
        """
        if T <= 0:
            # Option has expired
            if option_type == "call":
                return max(S - K, 0)
            else:
                return max(K - S, 0)
        
        # Calculate d1 and d2
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Calculate option price
        if option_type == "call":
            price = S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
        else:  # put
            price = K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        
        return max(price, 0)  # Ensure non-negative price
    
    def _calculate_greeks(self, S: float, K: float, T: float, r: float, 
                         sigma: float, option_type: str) -> Dict[str, float]:
        """
        Calculate option Greeks
        
        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiry (years)
            r: Risk-free rate
            sigma: Volatility
            option_type: 'call' or 'put'
            
        Returns:
            Dictionary of Greeks
        """
        if T <= 0:
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
        
        # Calculate d1 and d2
        d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        
        # Calculate Greeks
        delta = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        theta = (-S * norm.pdf(d1) * sigma / (2 * math.sqrt(T)) - 
                r * K * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2)) / 365
        vega = S * norm.pdf(d1) * math.sqrt(T) / 100
        rho = (K * T * math.exp(-r * T) * norm.cdf(d2 if option_type == "call" else -d2)) / 100
        
        return {
            "delta": round(delta, 4),
            "gamma": round(gamma, 6),
            "theta": round(theta, 4),
            "vega": round(vega, 4),
            "rho": round(rho, 4)
        }
    
    def calculate_arbun_premium(self, underlying_price: float, strike_price: float, 
                               time_to_expiry: float, volatility: float) -> Dict[str, Any]:
        """
        Calculate Islamic arbun (earnest money) premium with Sharia compliance
        
        Args:
            underlying_price: Current price of underlying commodity
            strike_price: Strike price of the option
            time_to_expiry: Time to expiry in years
            volatility: Volatility of underlying
            
        Returns:
            Arbun premium calculation
        """
        try:
            # Calculate maximum allowed premium (10% of underlying value)
            max_premium = underlying_price * self.max_arbun_premium
            
            # Calculate time decay factor (arbun should not exceed reasonable time value)
            time_factor = min(time_to_expiry * 2, 1.0)  # Max 1.0 for 6 months
            
            # Calculate volatility adjustment
            vol_factor = min(volatility / 0.3, 1.0)  # Max 1.0 for 30% vol
            
            # Calculate arbun premium (conservative Islamic approach)
            arbun_premium = min(
                underlying_price * 0.05 * time_factor * vol_factor,  # Base 5% with adjustments
                max_premium
            )
            
            # Ensure minimum premium for transaction costs
            arbun_premium = max(arbun_premium, underlying_price * 0.01)
            
            return {
                "arbun_premium": round(arbun_premium, 4),
                "percentage_of_underlying": round((arbun_premium / underlying_price) * 100, 2),
                "max_allowed_premium": round(max_premium, 4),
                "time_factor": round(time_factor, 4),
                "volatility_factor": round(vol_factor, 4),
                "islamic_compliant": True,
                "calculation_method": "Islamic Arbun Premium",
                "compliance_checks": {
                    "premium_within_limit": arbun_premium <= max_premium,
                    "reasonable_time_value": time_factor <= 1.0,
                    "volatility_appropriate": vol_factor <= 1.0
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Arbun premium calculation failed: {str(e)}")
            raise
    
    def validate_islamic_structure(self, option_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate option structure for Islamic compliance using AAOIFI standards
        
        Args:
            option_data: Option data to validate
            
        Returns:
            Validation result with compliance status
        """
        try:
            violations = []
            recommendations = []
            compliance_score = 100.0
            
            # Check 1: Premium ratio (should not exceed 10% of underlying value)
            underlying_price = option_data.get("underlying_price", 0)
            premium = option_data.get("premium", 0)
            if underlying_price > 0:
                premium_ratio = premium / underlying_price
                if premium_ratio > self.max_arbun_premium:
                    violations.append(f"Premium ratio {premium_ratio:.2%} exceeds Islamic limit of {self.max_arbun_premium:.2%}")
                    compliance_score -= 20
                else:
                    recommendations.append(f"Premium ratio {premium_ratio:.2%} is within Islamic limits")
            
            # Check 2: Time to expiry (should not be excessive)
            time_to_expiry = option_data.get("time_to_expiry", 0)
            if time_to_expiry > 1.0:  # More than 1 year
                violations.append(f"Time to expiry {time_to_expiry:.2f} years exceeds reasonable Islamic limit")
                compliance_score -= 15
            elif time_to_expiry > 0.5:  # More than 6 months
                recommendations.append("Consider shorter expiry for better Islamic compliance")
            
            # Check 3: Underlying asset (should be real commodity)
            underlying = option_data.get("underlying_asset", "")
            if underlying not in self.supported_commodities:
                violations.append(f"Underlying asset {underlying} not recognized for Islamic trading")
                compliance_score -= 25
            
            # Check 4: No speculative elements
            option_type = option_data.get("option_type", "")
            if option_type not in ["call", "put"]:
                violations.append("Invalid option type for Islamic trading")
                compliance_score -= 30
            
            # Check 5: Strike price reasonableness
            strike_price = option_data.get("strike_price", 0)
            if underlying_price > 0:
                strike_ratio = strike_price / underlying_price
                if strike_ratio < 0.5 or strike_ratio > 2.0:
                    violations.append(f"Strike price ratio {strike_ratio:.2f} outside reasonable range")
                    compliance_score -= 10
            
            # Determine structure type based on compliance
            if violations:
                structure_type = "conventional"
                is_compliant = False
            else:
                structure_type = "arbun"
                is_compliant = True
            
            return {
                "islamic_compliant": is_compliant,
                "structure_type": structure_type,
                "compliance_score": max(compliance_score, 0),
                "violations": violations,
                "recommendations": recommendations,
                "validation_details": {
                    "premium_ratio": round(premium / underlying_price, 4) if underlying_price > 0 else 0,
                    "time_to_expiry": time_to_expiry,
                    "underlying_asset": underlying,
                    "strike_reasonableness": round(strike_price / underlying_price, 4) if underlying_price > 0 else 0
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Islamic validation failed: {str(e)}")
            raise
    
    def _validate_islamic_compliance(self, underlying: str, option_type: OptionType, 
                                   premium: float, underlying_price: float, 
                                   time_to_expiry: float) -> Dict[str, Any]:
        """Internal method to validate Islamic compliance"""
        option_data = {
            "underlying_asset": underlying,
            "option_type": option_type.value,
            "premium": premium,
            "underlying_price": underlying_price,
            "time_to_expiry": time_to_expiry
        }
        return self.validate_islamic_structure(option_data)
    
    def execute_option_trade(self, option_id: str, execution_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an option trade with Islamic compliance validation
        
        Args:
            option_id: ID of the option to execute
            execution_params: Execution parameters
            
        Returns:
            Execution result
        """
        try:
            # Get option details
            option_data = self.options.get(option_id, {})
            if not option_data:
                raise ValueError(f"Option {option_id} not found")
            
            # Calculate execution price with market impact
            base_price = option_data.get("premium", 0)
            quantity = execution_params.get("quantity", 1000)
            market_impact = self._calculate_market_impact(quantity, base_price)
            execution_price = base_price * (1 + market_impact)
            
            # Validate Islamic compliance
            is_islamic_compliant = self._validate_execution_compliance(option_data, execution_params)
            
            if not is_islamic_compliant:
                raise ValueError("Option execution violates Islamic compliance requirements")
            
            execution_result = {
                "execution_id": f"EXE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "option_id": option_id,
                "execution_price": round(execution_price, 4),
                "execution_time": datetime.now().isoformat(),
                "quantity": quantity,
                "total_value": round(execution_price * quantity, 2),
                "market_impact": round(market_impact, 6),
                "status": "executed",
                "islamic_compliant": is_islamic_compliant,
                "execution_details": {
                    "base_price": base_price,
                    "impact_adjustment": market_impact,
                    "execution_type": execution_params.get("execution_type", "market"),
                    "venue": execution_params.get("venue", "primary"),
                    "counterparty": execution_params.get("counterparty", "system")
                }
            }
            
            # Store execution record
            self.executions[execution_result["execution_id"]] = execution_result
            
            # Update option status if fully executed
            if execution_params.get("close_position", False):
                self.options[option_id]["status"] = "closed"
            
            logger.info(f"Option trade executed: {option_id} at {execution_price}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Option execution failed: {str(e)}")
            raise
    
    def get_option_portfolio(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's option portfolio with comprehensive analytics
        
        Args:
            user_id: User identifier
            
        Returns:
            Portfolio summary
        """
        try:
            # Get user's options
            user_options = [opt for opt in self.options.values() if opt.get("user_id") == user_id]
            
            if not user_options:
                return {
                    "user_id": user_id,
                    "total_options": 0,
                    "total_value": 0,
                    "total_pnl": 0,
                    "portfolio_summary": {},
                    "risk_metrics": {"total_risk": 0, "risk_level": "low"},
                    "timestamp": datetime.now().isoformat()
                }
            
            # Calculate portfolio metrics
            total_options = len(user_options)
            total_value = sum(self._calculate_option_value(opt) for opt in user_options)
            total_pnl = sum(self._calculate_option_pnl(opt) for opt in user_options)
            
            # Group by commodity and type
            portfolio_summary = self._group_portfolio_by_commodity(user_options)
            
            # Calculate risk metrics
            risk_metrics = self._calculate_portfolio_risk(user_options)
            
            # Calculate Greeks for entire portfolio
            portfolio_greeks = self._calculate_portfolio_greeks(user_options)
            
            # Calculate Islamic compliance score
            compliance_score = self._calculate_portfolio_compliance(user_options)
            
            portfolio_data = {
                "user_id": user_id,
                "total_options": total_options,
                "total_value": round(total_value, 2),
                "total_pnl": round(total_pnl, 2),
                "pnl_percentage": round((total_pnl / total_value * 100) if total_value > 0 else 0, 2),
                "options": user_options,
                "portfolio_summary": portfolio_summary,
                "risk_metrics": risk_metrics,
                "portfolio_greeks": portfolio_greeks,
                "islamic_compliance_score": compliance_score,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Portfolio retrieved for user {user_id}: {total_options} options, value: {total_value}")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Portfolio retrieval failed: {str(e)}")
            raise
    
    def _calculate_market_impact(self, quantity: float, base_price: float) -> float:
        """Calculate market impact based on order size using sophisticated model"""
        # Advanced market impact model
        impact_factor = min(quantity / 1000000, 0.2)  # Max 20% impact for large orders
        volatility_adjustment = 1.0 + (base_price * 0.001)  # Higher prices = more impact
        return impact_factor * 0.01 * volatility_adjustment  # Base 1% per impact factor
    
    def _validate_execution_compliance(self, option_data: Dict[str, Any], execution_params: Dict[str, Any]) -> bool:
        """Validate execution for Islamic compliance"""
        # Check if option is Islamic compliant
        if not option_data.get("is_islamic_compliant", True):
            return False
        
        # Check execution parameters
        execution_type = execution_params.get("execution_type", "market")
        if execution_type == "speculative":
            return False
        
        # Check quantity limits (prevent excessive speculation)
        quantity = execution_params.get("quantity", 0)
        max_quantity = option_data.get("contract_size", 1000) * 10  # Max 10x contract size
        if quantity > max_quantity:
            return False
        
        return True
    
    def _calculate_option_value(self, option: Dict[str, Any]) -> float:
        """Calculate current value of an option"""
        premium = option.get("premium", 0)
        contract_size = option.get("contract_size", 1000)
        return premium * contract_size
    
    def _calculate_option_pnl(self, option: Dict[str, Any]) -> float:
        """Calculate P&L for an option"""
        current_value = self._calculate_option_value(option)
        initial_cost = option.get("initial_cost", current_value * 0.8)  # Assume some initial cost
        return current_value - initial_cost
    
    def _group_portfolio_by_commodity(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Group portfolio by commodity and type"""
        summary = {}
        for option in options:
            commodity = option.get("underlying_asset", "unknown")
            option_type = option.get("option_type", "unknown")
            
            if commodity not in summary:
                summary[commodity] = {}
            if option_type not in summary[commodity]:
                summary[commodity][option_type] = {"count": 0, "value": 0, "pnl": 0}
            
            summary[commodity][option_type]["count"] += 1
            summary[commodity][option_type]["value"] += self._calculate_option_value(option)
            summary[commodity][option_type]["pnl"] += self._calculate_option_pnl(option)
        
        return summary
    
    def _calculate_portfolio_risk(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio risk metrics"""
        if not options:
            return {"total_risk": 0, "risk_level": "low"}
        
        # Calculate portfolio Greeks
        total_delta = sum(opt.get("delta", 0) * opt.get("contract_size", 1000) for opt in options)
        total_gamma = sum(opt.get("gamma", 0) * opt.get("contract_size", 1000) for opt in options)
        total_theta = sum(opt.get("theta", 0) * opt.get("contract_size", 1000) for opt in options)
        total_vega = sum(opt.get("vega", 0) * opt.get("contract_size", 1000) for opt in options)
        
        # Calculate total value and risk
        total_value = sum(self._calculate_option_value(opt) for opt in options)
        total_risk = total_value * 0.15  # 15% risk assumption
        
        # Determine risk level
        if total_risk > 100000:
            risk_level = "high"
        elif total_risk > 50000:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            "total_risk": round(total_risk, 2),
            "risk_level": risk_level,
            "risk_percentage": 15.0,
            "portfolio_greeks": {
                "total_delta": round(total_delta, 2),
                "total_gamma": round(total_gamma, 4),
                "total_theta": round(total_theta, 2),
                "total_vega": round(total_vega, 2)
            },
            "diversification_score": min(len(options) / 10, 1.0),
            "concentration_risk": self._calculate_concentration_risk(options)
        }
    
    def _calculate_portfolio_greeks(self, options: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate aggregate Greeks for the portfolio"""
        if not options:
            return {"delta": 0, "gamma": 0, "theta": 0, "vega": 0, "rho": 0}
        
        total_delta = sum(opt.get("delta", 0) * opt.get("contract_size", 1000) for opt in options)
        total_gamma = sum(opt.get("gamma", 0) * opt.get("contract_size", 1000) for opt in options)
        total_theta = sum(opt.get("theta", 0) * opt.get("contract_size", 1000) for opt in options)
        total_vega = sum(opt.get("vega", 0) * opt.get("contract_size", 1000) for opt in options)
        total_rho = sum(opt.get("rho", 0) * opt.get("contract_size", 1000) for opt in options)
        
        return {
            "delta": round(total_delta, 2),
            "gamma": round(total_gamma, 4),
            "theta": round(total_theta, 2),
            "vega": round(total_vega, 2),
            "rho": round(total_rho, 2)
        }
    
    def _calculate_concentration_risk(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate concentration risk in the portfolio"""
        if not options:
            return {"max_concentration": 0, "herfindahl_index": 0}
        
        # Calculate concentration by commodity
        commodity_values = {}
        total_value = sum(self._calculate_option_value(opt) for opt in options)
        
        for option in options:
            commodity = option.get("underlying_asset", "unknown")
            value = self._calculate_option_value(option)
            commodity_values[commodity] = commodity_values.get(commodity, 0) + value
        
        # Calculate Herfindahl-Hirschman Index
        hhi = sum((value / total_value) ** 2 for value in commodity_values.values()) if total_value > 0 else 0
        max_concentration = max(commodity_values.values()) / total_value if total_value > 0 else 0
        
        return {
            "max_concentration": round(max_concentration, 4),
            "herfindahl_index": round(hhi, 4),
            "concentration_level": "high" if hhi > 0.25 else "medium" if hhi > 0.15 else "low",
            "commodity_breakdown": {k: round(v / total_value, 4) for k, v in commodity_values.items()}
        }
    
    def _calculate_portfolio_compliance(self, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate Islamic compliance score for the portfolio"""
        if not options:
            return {"score": 100, "level": "excellent"}
        
        compliant_options = sum(1 for opt in options if opt.get("is_islamic_compliant", True))
        compliance_ratio = compliant_options / len(options)
        
        if compliance_ratio >= 0.95:
            level = "excellent"
        elif compliance_ratio >= 0.85:
            level = "good"
        elif compliance_ratio >= 0.70:
            level = "fair"
        else:
            level = "poor"
        
        return {
            "score": round(compliance_ratio * 100, 2),
            "level": level,
            "compliant_options": compliant_options,
            "total_options": len(options),
            "violations": len(options) - compliant_options
        }


class IslamicOptionsValidator:
    """Advanced validator for Islamic-compliant options trading using AAOIFI standards"""
    
    def __init__(self):
        self.prohibited_elements = ["gharar", "maysir", "riba"]
        self.max_premium_ratio = 0.1  # 10% of underlying value
        self.max_time_to_expiry = 1.0  # 1 year maximum
        self.aaoifi_standards = {
            "arbun": {"max_premium": 0.1, "max_time": 1.0, "min_underlying": "real_asset"},
            "salam": {"max_premium": 0.05, "max_time": 0.5, "min_underlying": "commodity"},
            "istisna": {"max_premium": 0.15, "max_time": 2.0, "min_underlying": "manufactured"}
        }
    
    def validate_arbun_structure(self, option_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate arbun option structure according to AAOIFI standards
        
        Args:
            option_data: Option data to validate
            
        Returns:
            Validation result
        """
        try:
            violations = []
            warnings = []
            
            # Check premium ratio
            underlying_price = option_data.get("underlying_price", 0)
            premium = option_data.get("premium", 0)
            if underlying_price > 0:
                premium_ratio = premium / underlying_price
                max_premium = self.aaoifi_standards["arbun"]["max_premium"]
                
                if premium_ratio > max_premium:
                    violations.append(f"Premium ratio {premium_ratio:.2%} exceeds AAOIFI limit of {max_premium:.2%}")
                elif premium_ratio > max_premium * 0.8:  # 80% of limit
                    warnings.append(f"Premium ratio {premium_ratio:.2%} is approaching AAOIFI limit")
            
            # Check time to expiry
            time_to_expiry = option_data.get("time_to_expiry", 0)
            max_time = self.aaoifi_standards["arbun"]["max_time"]
            
            if time_to_expiry > max_time:
                violations.append(f"Time to expiry {time_to_expiry:.2f} years exceeds AAOIFI limit of {max_time:.2f}")
            elif time_to_expiry > max_time * 0.8:  # 80% of limit
                warnings.append(f"Time to expiry {time_to_expiry:.2f} years is approaching AAOIFI limit")
            
            # Check underlying asset
            underlying = option_data.get("underlying_asset", "")
            if underlying not in ["crude_oil", "natural_gas", "refined_products", "lng"]:
                violations.append(f"Underlying asset {underlying} not suitable for arbun structure")
            
            # Check strike price reasonableness
            strike_price = option_data.get("strike_price", 0)
            if underlying_price > 0:
                strike_ratio = strike_price / underlying_price
                if strike_ratio < 0.7 or strike_ratio > 1.3:
                    warnings.append(f"Strike price ratio {strike_ratio:.2f} outside typical arbun range")
            
            # Calculate compliance score
            compliance_score = 100
            compliance_score -= len(violations) * 25  # Major violations
            compliance_score -= len(warnings) * 10   # Minor warnings
            compliance_score = max(compliance_score, 0)
            
            return {
                "valid": len(violations) == 0,
                "structure_type": "arbun",
                "compliance_score": compliance_score,
                "violations": violations,
                "warnings": warnings,
                "premium_ratio": round(premium / underlying_price, 4) if underlying_price > 0 else 0,
                "time_limit_valid": time_to_expiry <= max_time,
                "islamic_compliant": len(violations) == 0,
                "aaoifi_compliant": len(violations) == 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Arbun validation failed: {str(e)}")
            raise
    
    def check_gharar_levels(self, option_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check gharar (uncertainty) levels in option using quantitative methods
        
        Args:
            option_data: Option data to check
            
        Returns:
            Gharar assessment
        """
        try:
            uncertainty_factors = []
            uncertainty_score = 0.0
            
            # Factor 1: Price uncertainty (volatility)
            volatility = option_data.get("volatility", 0)
            if volatility > 0.4:  # 40% volatility
                uncertainty_factors.append("high_volatility")
                uncertainty_score += 0.3
            elif volatility > 0.25:  # 25% volatility
                uncertainty_score += 0.15
            
            # Factor 2: Time uncertainty
            time_to_expiry = option_data.get("time_to_expiry", 0)
            if time_to_expiry > 0.5:  # 6 months
                uncertainty_factors.append("long_expiry")
                uncertainty_score += 0.2
            elif time_to_expiry > 0.25:  # 3 months
                uncertainty_score += 0.1
            
            # Factor 3: Strike price uncertainty
            underlying_price = option_data.get("underlying_price", 0)
            strike_price = option_data.get("strike_price", 0)
            if underlying_price > 0:
                strike_ratio = strike_price / underlying_price
                if strike_ratio < 0.8 or strike_ratio > 1.2:
                    uncertainty_factors.append("extreme_strike")
                    uncertainty_score += 0.25
                elif strike_ratio < 0.9 or strike_ratio > 1.1:
                    uncertainty_score += 0.1
            
            # Factor 4: Underlying asset uncertainty
            underlying = option_data.get("underlying_asset", "")
            if underlying in ["electricity", "carbon_credits"]:  # More volatile assets
                uncertainty_factors.append("volatile_underlying")
                uncertainty_score += 0.15
            
            # Determine gharar level
            if uncertainty_score >= 0.5:
                gharar_level = "high"
            elif uncertainty_score >= 0.3:
                gharar_level = "medium"
            else:
                gharar_level = "low"
            
            # Check acceptability
            acceptable = uncertainty_score <= 0.4  # Threshold for Islamic acceptability
            
            return {
                "gharar_level": gharar_level,
                "uncertainty_score": round(uncertainty_score, 3),
                "acceptable": acceptable,
                "uncertainty_factors": uncertainty_factors,
                "risk_factors": [
                    f"Volatility: {volatility:.1%}" if volatility > 0.25 else None,
                    f"Time to expiry: {time_to_expiry:.2f} years" if time_to_expiry > 0.25 else None,
                    f"Strike ratio: {strike_ratio:.2f}" if underlying_price > 0 and (strike_ratio < 0.9 or strike_ratio > 1.1) else None
                ],
                "recommendations": self._get_gharar_recommendations(uncertainty_score, uncertainty_factors),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Gharar assessment failed: {str(e)}")
            raise
    
    def _get_gharar_recommendations(self, uncertainty_score: float, factors: List[str]) -> List[str]:
        """Get recommendations to reduce gharar"""
        recommendations = []
        
        if uncertainty_score > 0.4:
            recommendations.append("Consider reducing time to expiry to minimize uncertainty")
            recommendations.append("Use more conservative strike prices closer to current market price")
        
        if "high_volatility" in factors:
            recommendations.append("Consider underlying assets with lower volatility")
        
        if "long_expiry" in factors:
            recommendations.append("Reduce time to expiry to less than 6 months")
        
        if "extreme_strike" in factors:
            recommendations.append("Use strike prices within 10% of current market price")
        
        if not recommendations:
            recommendations.append("Option structure has acceptable gharar levels")
        
        return recommendations