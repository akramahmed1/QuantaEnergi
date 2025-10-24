"""
Crypto Risk Domain - Molecule-like crypto risk analysis
Advanced cryptocurrency risk modeling and analysis
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import random

logger = logging.getLogger(__name__)

class CryptoAssetType(Enum):
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    ALTCOIN = "altcoin"
    STABLECOIN = "stablecoin"
    DEFI_TOKEN = "defi_token"
    NFT = "nft"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class CryptoAsset:
    """Cryptocurrency asset structure"""
    symbol: str
    asset_type: CryptoAssetType
    market_cap: float
    volume_24h: float
    price: float
    price_change_24h: float
    price_change_7d: float
    price_change_30d: float
    volatility: float
    liquidity_score: float
    technical_score: float
    fundamental_score: float
    social_sentiment: float
    regulatory_score: float
    last_updated: datetime

class CryptoRiskModel:
    """Molecule-inspired crypto risk modeling engine"""
    
    def __init__(self):
        self.risk_models = {}
        self.correlation_models = {}
        self.volatility_models = {}
        self.regulatory_models = {}
        
    def analyze_crypto_risk(self, crypto_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive crypto risk analysis"""
        try:
            # Parse crypto data
            crypto_asset = self._parse_crypto_data(crypto_data)
            
            # Calculate risk metrics
            market_risk = self._calculate_market_risk(crypto_asset)
            technical_risk = self._calculate_technical_risk(crypto_asset)
            fundamental_risk = self._calculate_fundamental_risk(crypto_asset)
            regulatory_risk = self._calculate_regulatory_risk(crypto_asset)
            liquidity_risk = self._calculate_liquidity_risk(crypto_asset)
            
            # Calculate composite risk score
            composite_risk = self._calculate_composite_risk(
                market_risk, technical_risk, fundamental_risk, regulatory_risk, liquidity_risk
            )
            
            # Risk classification
            risk_level = self._classify_risk_level(composite_risk)
            
            # Correlation analysis
            correlation_analysis = self._analyze_correlations(crypto_asset)
            
            # Volatility analysis
            volatility_analysis = self._analyze_volatility(crypto_asset)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(composite_risk, risk_level)
            
            return {
                "crypto_symbol": crypto_asset.symbol,
                "asset_type": crypto_asset.asset_type.value,
                "risk_analysis": {
                    "composite_risk_score": composite_risk,
                    "risk_level": risk_level.value,
                    "market_risk": market_risk,
                    "technical_risk": technical_risk,
                    "fundamental_risk": fundamental_risk,
                    "regulatory_risk": regulatory_risk,
                    "liquidity_risk": liquidity_risk
                },
                "correlation_analysis": correlation_analysis,
                "volatility_analysis": volatility_analysis,
                "recommendations": recommendations,
                "risk_factors": self._identify_risk_factors(crypto_asset),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing crypto risk: {str(e)}")
            raise
    
    def _parse_crypto_data(self, crypto_data: Dict[str, Any]) -> CryptoAsset:
        """Parse crypto data into asset structure"""
        return CryptoAsset(
            symbol=crypto_data.get("symbol", "BTC"),
            asset_type=CryptoAssetType(crypto_data.get("asset_type", "bitcoin")),
            market_cap=float(crypto_data.get("market_cap", 1000000000)),
            volume_24h=float(crypto_data.get("volume_24h", 100000000)),
            price=float(crypto_data.get("price", 50000)),
            price_change_24h=float(crypto_data.get("price_change_24h", 0.0)),
            price_change_7d=float(crypto_data.get("price_change_7d", 0.0)),
            price_change_30d=float(crypto_data.get("price_change_30d", 0.0)),
            volatility=float(crypto_data.get("volatility", 0.2)),
            liquidity_score=float(crypto_data.get("liquidity_score", 0.5)),
            technical_score=float(crypto_data.get("technical_score", 0.5)),
            fundamental_score=float(crypto_data.get("fundamental_score", 0.5)),
            social_sentiment=float(crypto_data.get("social_sentiment", 0.5)),
            regulatory_score=float(crypto_data.get("regulatory_score", 0.5)),
            last_updated=datetime.now()
        )
    
    def _calculate_market_risk(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Calculate market-related risk factors"""
        # Price volatility risk
        volatility_risk = min(1.0, asset.volatility * 2)  # Scale volatility to 0-1
        
        # Market cap risk
        if asset.market_cap > 100e9:
            market_cap_risk = 0.1
        elif asset.market_cap > 10e9:
            market_cap_risk = 0.3
        elif asset.market_cap > 1e9:
            market_cap_risk = 0.6
        else:
            market_cap_risk = 0.9
        
        # Price momentum risk
        momentum_risk = 0.0
        if abs(asset.price_change_24h) > 0.1:  # >10% daily change
            momentum_risk += 0.3
        if abs(asset.price_change_7d) > 0.2:  # >20% weekly change
            momentum_risk += 0.3
        if abs(asset.price_change_30d) > 0.5:  # >50% monthly change
            momentum_risk += 0.4
        
        momentum_risk = min(1.0, momentum_risk)
        
        # Volume risk
        volume_risk = 0.0
        if asset.volume_24h < asset.market_cap * 0.01:  # Low volume
            volume_risk = 0.7
        elif asset.volume_24h < asset.market_cap * 0.05:  # Medium volume
            volume_risk = 0.3
        
        return {
            "volatility_risk": volatility_risk,
            "market_cap_risk": market_cap_risk,
            "momentum_risk": momentum_risk,
            "volume_risk": volume_risk,
            "overall_market_risk": (volatility_risk + market_cap_risk + momentum_risk + volume_risk) / 4
        }
    
    def _calculate_technical_risk(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Calculate technical analysis risk factors"""
        # Technical score risk
        technical_risk = 1.0 - asset.technical_score
        
        # Price level risk (simplified)
        price_level_risk = 0.5  # Default neutral
        
        # Trend risk
        trend_risk = 0.0
        if asset.price_change_24h < -0.05:  # Strong downtrend
            trend_risk = 0.8
        elif asset.price_change_24h < -0.02:  # Moderate downtrend
            trend_risk = 0.5
        elif asset.price_change_24h > 0.05:  # Strong uptrend
            trend_risk = 0.3
        elif asset.price_change_24h > 0.02:  # Moderate uptrend
            trend_risk = 0.1
        
        return {
            "technical_score_risk": technical_risk,
            "price_level_risk": price_level_risk,
            "trend_risk": trend_risk,
            "overall_technical_risk": (technical_risk + price_level_risk + trend_risk) / 3
        }
    
    def _calculate_fundamental_risk(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Calculate fundamental analysis risk factors"""
        # Fundamental score risk
        fundamental_risk = 1.0 - asset.fundamental_score
        
        # Asset type risk
        asset_type_risk = 0.0
        if asset.asset_type == CryptoAssetType.BITCOIN:
            asset_type_risk = 0.2
        elif asset.asset_type == CryptoAssetType.ETHEREUM:
            asset_type_risk = 0.3
        elif asset.asset_type == CryptoAssetType.ALTCOIN:
            asset_type_risk = 0.7
        elif asset.asset_type == CryptoAssetType.DEFI_TOKEN:
            asset_type_risk = 0.8
        elif asset.asset_type == CryptoAssetType.NFT:
            asset_type_risk = 0.9
        
        # Market adoption risk
        adoption_risk = 0.0
        if asset.market_cap < 1e9:
            adoption_risk = 0.8
        elif asset.market_cap < 10e9:
            adoption_risk = 0.5
        elif asset.market_cap < 100e9:
            adoption_risk = 0.2
        
        return {
            "fundamental_score_risk": fundamental_risk,
            "asset_type_risk": asset_type_risk,
            "adoption_risk": adoption_risk,
            "overall_fundamental_risk": (fundamental_risk + asset_type_risk + adoption_risk) / 3
        }
    
    def _calculate_regulatory_risk(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Calculate regulatory risk factors"""
        # Regulatory score risk
        regulatory_risk = 1.0 - asset.regulatory_score
        
        # Asset type regulatory risk
        type_regulatory_risk = 0.0
        if asset.asset_type == CryptoAssetType.BITCOIN:
            type_regulatory_risk = 0.3
        elif asset.asset_type == CryptoAssetType.ETHEREUM:
            type_regulatory_risk = 0.4
        elif asset.asset_type == CryptoAssetType.ALTCOIN:
            type_regulatory_risk = 0.6
        elif asset.asset_type == CryptoAssetType.DEFI_TOKEN:
            type_regulatory_risk = 0.8
        elif asset.asset_type == CryptoAssetType.NFT:
            type_regulatory_risk = 0.7
        
        # Global regulatory risk (simplified)
        global_regulatory_risk = 0.4  # Default moderate risk
        
        return {
            "regulatory_score_risk": regulatory_risk,
            "type_regulatory_risk": type_regulatory_risk,
            "global_regulatory_risk": global_regulatory_risk,
            "overall_regulatory_risk": (regulatory_risk + type_regulatory_risk + global_regulatory_risk) / 3
        }
    
    def _calculate_liquidity_risk(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Calculate liquidity risk factors"""
        # Liquidity score risk
        liquidity_risk = 1.0 - asset.liquidity_score
        
        # Volume-based liquidity risk
        volume_liquidity_risk = 0.0
        if asset.volume_24h < asset.market_cap * 0.01:  # Very low volume
            volume_liquidity_risk = 0.9
        elif asset.volume_24h < asset.market_cap * 0.05:  # Low volume
            volume_liquidity_risk = 0.6
        elif asset.volume_24h < asset.market_cap * 0.1:  # Medium volume
            volume_liquidity_risk = 0.3
        
        # Market cap liquidity risk
        market_cap_liquidity_risk = 0.0
        if asset.market_cap < 100e6:  # <$100M
            market_cap_liquidity_risk = 0.8
        elif asset.market_cap < 1e9:  # <$1B
            market_cap_liquidity_risk = 0.5
        elif asset.market_cap < 10e9:  # <$10B
            market_cap_liquidity_risk = 0.2
        
        return {
            "liquidity_score_risk": liquidity_risk,
            "volume_liquidity_risk": volume_liquidity_risk,
            "market_cap_liquidity_risk": market_cap_liquidity_risk,
            "overall_liquidity_risk": (liquidity_risk + volume_liquidity_risk + market_cap_liquidity_risk) / 3
        }
    
    def _calculate_composite_risk(self, market_risk: Dict, technical_risk: Dict, 
                                fundamental_risk: Dict, regulatory_risk: Dict, 
                                liquidity_risk: Dict) -> float:
        """Calculate composite risk score"""
        # Weighted average of all risk components
        weights = {
            "market": 0.3,
            "technical": 0.2,
            "fundamental": 0.2,
            "regulatory": 0.15,
            "liquidity": 0.15
        }
        
        composite_risk = (
            market_risk["overall_market_risk"] * weights["market"] +
            technical_risk["overall_technical_risk"] * weights["technical"] +
            fundamental_risk["overall_fundamental_risk"] * weights["fundamental"] +
            regulatory_risk["overall_regulatory_risk"] * weights["regulatory"] +
            liquidity_risk["overall_liquidity_risk"] * weights["liquidity"]
        )
        
        return min(1.0, composite_risk)
    
    def _classify_risk_level(self, risk_score: float) -> RiskLevel:
        """Classify risk level based on score"""
        if risk_score > 0.8:
            return RiskLevel.CRITICAL
        elif risk_score > 0.6:
            return RiskLevel.HIGH
        elif risk_score > 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _analyze_correlations(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Analyze correlations with other assets"""
        # Simplified correlation analysis
        correlations = {}
        
        if asset.asset_type == CryptoAssetType.BITCOIN:
            correlations = {
                "btc_correlation": 1.0,
                "eth_correlation": random.uniform(0.6, 0.8),
                "altcoin_correlation": random.uniform(0.4, 0.7),
                "stock_market_correlation": random.uniform(-0.2, 0.3),
                "gold_correlation": random.uniform(-0.1, 0.2),
                "dollar_correlation": random.uniform(-0.3, -0.1)
            }
        elif asset.asset_type == CryptoAssetType.ETHEREUM:
            correlations = {
                "btc_correlation": random.uniform(0.6, 0.8),
                "eth_correlation": 1.0,
                "altcoin_correlation": random.uniform(0.5, 0.8),
                "stock_market_correlation": random.uniform(-0.1, 0.4),
                "gold_correlation": random.uniform(-0.1, 0.3),
                "dollar_correlation": random.uniform(-0.2, 0.1)
            }
        else:
            correlations = {
                "btc_correlation": random.uniform(0.3, 0.7),
                "eth_correlation": random.uniform(0.4, 0.8),
                "altcoin_correlation": random.uniform(0.6, 0.9),
                "stock_market_correlation": random.uniform(-0.1, 0.5),
                "gold_correlation": random.uniform(-0.2, 0.4),
                "dollar_correlation": random.uniform(-0.3, 0.2)
            }
        
        # Calculate correlation strength
        avg_correlation = np.mean(list(correlations.values()))
        if avg_correlation > 0.7:
            correlation_strength = "strong"
        elif avg_correlation > 0.4:
            correlation_strength = "moderate"
        else:
            correlation_strength = "weak"
        
        return {
            "correlations": correlations,
            "correlation_strength": correlation_strength,
            "average_correlation": float(avg_correlation)
        }
    
    def _analyze_volatility(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Analyze volatility patterns"""
        # Historical volatility analysis
        volatility_percentiles = {
            "volatility_percentile_25": asset.volatility * 0.7,
            "volatility_percentile_50": asset.volatility,
            "volatility_percentile_75": asset.volatility * 1.3,
            "volatility_percentile_95": asset.volatility * 1.8
        }
        
        # Volatility regime classification
        if asset.volatility < 0.3:
            volatility_regime = "low"
        elif asset.volatility < 0.6:
            volatility_regime = "medium"
        elif asset.volatility < 1.0:
            volatility_regime = "high"
        else:
            volatility_regime = "extreme"
        
        # Volatility risk assessment
        volatility_risk = min(1.0, asset.volatility * 1.5)
        
        return {
            "current_volatility": asset.volatility,
            "volatility_percentiles": volatility_percentiles,
            "volatility_regime": volatility_regime,
            "volatility_risk": volatility_risk,
            "volatility_trend": "stable"  # Simplified
        }
    
    def _identify_risk_factors(self, asset: CryptoAsset) -> List[str]:
        """Identify specific risk factors"""
        risk_factors = []
        
        # Market risk factors
        if asset.volatility > 0.8:
            risk_factors.append("High price volatility")
        if asset.market_cap < 1e9:
            risk_factors.append("Small market capitalization")
        if asset.volume_24h < asset.market_cap * 0.05:
            risk_factors.append("Low trading volume")
        
        # Technical risk factors
        if asset.technical_score < 0.3:
            risk_factors.append("Weak technical indicators")
        if abs(asset.price_change_24h) > 0.1:
            risk_factors.append("High price momentum")
        
        # Fundamental risk factors
        if asset.fundamental_score < 0.3:
            risk_factors.append("Weak fundamentals")
        if asset.asset_type in [CryptoAssetType.ALTCOIN, CryptoAssetType.DEFI_TOKEN]:
            risk_factors.append("High-risk asset type")
        
        # Regulatory risk factors
        if asset.regulatory_score < 0.3:
            risk_factors.append("Regulatory uncertainty")
        if asset.asset_type == CryptoAssetType.DEFI_TOKEN:
            risk_factors.append("DeFi regulatory risk")
        
        # Liquidity risk factors
        if asset.liquidity_score < 0.3:
            risk_factors.append("Low liquidity")
        if asset.volume_24h < asset.market_cap * 0.01:
            risk_factors.append("Very low trading volume")
        
        return risk_factors
    
    def _generate_recommendations(self, risk_score: float, risk_level: RiskLevel) -> List[str]:
        """Generate trading recommendations based on risk analysis"""
        recommendations = []
        
        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "🚨 CRITICAL RISK: Avoid new positions",
                "Consider reducing exposure by 75-90%",
                "Implement strict stop-loss orders at 5-10%",
                "Monitor regulatory developments closely",
                "Consider hedging with stablecoins or fiat"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "⚠️ HIGH RISK: Limit position sizes",
                "Use conservative position sizing (1-2% of portfolio)",
                "Set stop-loss orders at 10-15%",
                "Diversify across different crypto assets",
                "Consider hedging strategies"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "📊 MEDIUM RISK: Standard risk management",
                "Use moderate position sizing (2-5% of portfolio)",
                "Set stop-loss orders at 15-20%",
                "Monitor key technical levels",
                "Consider partial hedging for large positions"
            ])
        else:  # LOW
            recommendations.extend([
                "✅ LOW RISK: Standard operations",
                "Continue monitoring for risk escalation",
                "Maintain normal position sizing",
                "Set standard stop-loss orders at 20-25%"
            ])
        
        # Additional recommendations based on risk score
        if risk_score > 0.7:
            recommendations.append("Consider reducing overall crypto allocation")
        if risk_score > 0.5:
            recommendations.append("Increase monitoring frequency")
        if risk_score < 0.3:
            recommendations.append("Opportunity for increased allocation")
        
        return recommendations

class CryptoPortfolioRiskAnalyzer:
    """Portfolio-level crypto risk analysis"""
    
    def __init__(self):
        self.crypto_risk_model = CryptoRiskModel()
        
    def analyze_portfolio_risk(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk for a crypto portfolio"""
        try:
            positions = portfolio_data.get("positions", [])
            total_value = portfolio_data.get("total_value", 0)
            
            if not positions or total_value <= 0:
                return {"error": "Invalid portfolio data"}
            
            # Analyze individual positions
            position_risks = []
            total_risk_exposure = 0
            
            for position in positions:
                position_value = position.get("value", 0)
                weight = position_value / total_value if total_value > 0 else 0
                
                # Get risk analysis for this position
                risk_analysis = self.crypto_risk_model.analyze_crypto_risk(position)
                position_risk = risk_analysis["risk_analysis"]["composite_risk_score"]
                
                position_risks.append({
                    "symbol": position.get("symbol", "UNKNOWN"),
                    "weight": weight,
                    "risk_score": position_risk,
                    "risk_level": risk_analysis["risk_analysis"]["risk_level"],
                    "value": position_value
                })
                
                # Calculate weighted risk exposure
                total_risk_exposure += position_risk * weight
            
            # Portfolio-level analysis
            portfolio_risk_level = self._classify_portfolio_risk(total_risk_exposure)
            
            # Concentration analysis
            concentration_analysis = self._analyze_concentration(positions, total_value)
            
            # Correlation analysis
            correlation_analysis = self._analyze_portfolio_correlations(positions)
            
            # Generate portfolio recommendations
            portfolio_recommendations = self._generate_portfolio_recommendations(
                total_risk_exposure, portfolio_risk_level, concentration_analysis
            )
            
            return {
                "portfolio_risk_analysis": {
                    "total_risk_exposure": total_risk_exposure,
                    "portfolio_risk_level": portfolio_risk_level,
                    "position_count": len(positions),
                    "total_value": total_value
                },
                "position_risks": position_risks,
                "concentration_analysis": concentration_analysis,
                "correlation_analysis": correlation_analysis,
                "portfolio_recommendations": portfolio_recommendations,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio risk: {str(e)}")
            raise
    
    def _classify_portfolio_risk(self, risk_exposure: float) -> str:
        """Classify portfolio risk level"""
        if risk_exposure > 0.8:
            return "CRITICAL"
        elif risk_exposure > 0.6:
            return "HIGH"
        elif risk_exposure > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _analyze_concentration(self, positions: List[Dict], total_value: float) -> Dict[str, Any]:
        """Analyze portfolio concentration"""
        if not positions or total_value <= 0:
            return {"error": "No positions to analyze"}
        
        # Calculate weights
        weights = [pos.get("value", 0) / total_value for pos in positions]
        
        # Calculate concentration metrics
        max_weight = max(weights)
        top_5_weight = sum(sorted(weights, reverse=True)[:5])
        herfindahl_index = sum(w**2 for w in weights)
        
        # Concentration risk classification
        if max_weight > 0.5:
            concentration_risk = "CRITICAL"
        elif max_weight > 0.3:
            concentration_risk = "HIGH"
        elif max_weight > 0.2:
            concentration_risk = "MEDIUM"
        else:
            concentration_risk = "LOW"
        
        return {
            "max_position_weight": max_weight,
            "top_5_weight": top_5_weight,
            "herfindahl_index": herfindahl_index,
            "concentration_risk": concentration_risk,
            "position_count": len(positions)
        }
    
    def _analyze_portfolio_correlations(self, positions: List[Dict]) -> Dict[str, Any]:
        """Analyze portfolio correlations"""
        # Simplified correlation analysis
        symbols = [pos.get("symbol", "UNKNOWN") for pos in positions]
        
        # Calculate average correlation (simplified)
        if len(symbols) <= 1:
            avg_correlation = 0.0
        else:
            # Simplified correlation calculation
            avg_correlation = random.uniform(0.3, 0.8)
        
        # Correlation risk classification
        if avg_correlation > 0.7:
            correlation_risk = "HIGH"
        elif avg_correlation > 0.5:
            correlation_risk = "MEDIUM"
        else:
            correlation_risk = "LOW"
        
        return {
            "average_correlation": avg_correlation,
            "correlation_risk": correlation_risk,
            "diversification_score": 1.0 - avg_correlation
        }
    
    def _generate_portfolio_recommendations(self, risk_exposure: float, 
                                          portfolio_risk_level: str, 
                                          concentration_analysis: Dict) -> List[str]:
        """Generate portfolio-level recommendations"""
        recommendations = []
        
        # Risk-based recommendations
        if portfolio_risk_level == "CRITICAL":
            recommendations.extend([
                "🚨 CRITICAL: Immediate portfolio rebalancing required",
                "Reduce overall crypto allocation by 50-75%",
                "Focus on large-cap, established cryptocurrencies",
                "Implement strict risk management rules"
            ])
        elif portfolio_risk_level == "HIGH":
            recommendations.extend([
                "⚠️ HIGH: Portfolio risk management needed",
                "Reduce position sizes and increase diversification",
                "Consider hedging strategies",
                "Monitor correlations closely"
            ])
        elif portfolio_risk_level == "MEDIUM":
            recommendations.extend([
                "📊 MEDIUM: Standard portfolio management",
                "Maintain current allocation with monitoring",
                "Consider rebalancing if correlations increase"
            ])
        else:
            recommendations.extend([
                "✅ LOW: Portfolio risk is acceptable",
                "Continue current strategy with monitoring",
                "Consider opportunities for optimization"
            ])
        
        # Concentration-based recommendations
        if concentration_analysis.get("concentration_risk") == "CRITICAL":
            recommendations.append("Reduce concentration in largest positions")
        elif concentration_analysis.get("concentration_risk") == "HIGH":
            recommendations.append("Consider diversifying largest positions")
        
        # Diversification recommendations
        if concentration_analysis.get("position_count", 0) < 5:
            recommendations.append("Consider adding more positions for diversification")
        
        return recommendations
