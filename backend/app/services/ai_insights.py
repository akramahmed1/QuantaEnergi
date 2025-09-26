"""
AI Insights Service
Provides intelligent trading insights, recommendations, and market analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum
import json

logger = structlog.get_logger()

class InsightType(str, Enum):
    TRADING_SIGNAL = "trading_signal"
    RISK_ALERT = "risk_alert"
    MARKET_ANALYSIS = "market_analysis"
    ESG_INSIGHT = "esg_insight"
    OPTIMIZATION_RECOMMENDATION = "optimization_recommendation"

class SignalStrength(str, Enum):
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class TradingInsight:
    """AI-generated trading insight"""
    insight_id: str
    insight_type: InsightType
    commodity: str
    signal: str  # BUY, SELL, HOLD
    strength: SignalStrength
    confidence: float
    reasoning: str
    supporting_data: Dict[str, Any]
    timestamp: datetime
    expiry: datetime
    priority: int  # 1-5, 5 being highest

class AIInsightsEngine:
    """AI-powered insights and recommendations engine"""
    
    def __init__(self):
        self.insight_history = []
        self.model_performance = {}
        self.market_regimes = {}
        self.esg_trends = {}
        
    def analyze_market_conditions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market conditions using AI"""
        try:
            analysis = {
                'market_regime': self._detect_market_regime(market_data),
                'volatility_regime': self._detect_volatility_regime(market_data),
                'trend_direction': self._analyze_trend_direction(market_data),
                'correlation_structure': self._analyze_correlations(market_data),
                'liquidity_conditions': self._assess_liquidity(market_data),
                'esg_momentum': self._analyze_esg_trends(market_data),
                'risk_factors': self._identify_risk_factors(market_data),
                'opportunities': self._identify_opportunities(market_data)
            }
            
            logger.info("Market analysis completed", 
                       regime=analysis['market_regime'],
                       volatility=analysis['volatility_regime'])
            
            return analysis
            
        except Exception as e:
            logger.error("Market analysis failed", error=str(e))
            raise
    
    def generate_trading_signals(self, commodities: List[str], 
                                market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate AI-powered trading signals"""
        try:
            insights = []
            
            for commodity in commodities:
                # Technical analysis signals
                technical_signals = self._generate_technical_signals(commodity, market_data)
                insights.extend(technical_signals)
                
                # Fundamental analysis signals
                fundamental_signals = self._generate_fundamental_signals(commodity, market_data)
                insights.extend(fundamental_signals)
                
                # ESG-based signals
                esg_signals = self._generate_esg_signals(commodity, market_data)
                insights.extend(esg_signals)
                
                # Risk-based signals
                risk_signals = self._generate_risk_signals(commodity, market_data)
                insights.extend(risk_signals)
            
            # Sort by priority and confidence
            insights.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
            
            logger.info("Trading signals generated", count=len(insights))
            return insights
            
        except Exception as e:
            logger.error("Trading signal generation failed", error=str(e))
            raise
    
    def _detect_market_regime(self, market_data: Dict[str, Any]) -> str:
        """Detect current market regime using ML"""
        # Mock regime detection
        volatility = market_data.get('volatility', 0.02)
        trend = market_data.get('trend', 0)
        
        if volatility > 0.03:
            return "high_volatility"
        elif trend > 0.01:
            return "bull_market"
        elif trend < -0.01:
            return "bear_market"
        else:
            return "sideways"
    
    def _detect_volatility_regime(self, market_data: Dict[str, Any]) -> str:
        """Detect volatility regime"""
        volatility = market_data.get('volatility', 0.02)
        
        if volatility > 0.04:
            return "high_volatility"
        elif volatility > 0.02:
            return "medium_volatility"
        else:
            return "low_volatility"
    
    def _analyze_trend_direction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trend direction and strength"""
        trend = market_data.get('trend', 0)
        momentum = market_data.get('momentum', 0)
        
        return {
            'direction': 'bullish' if trend > 0 else 'bearish' if trend < 0 else 'neutral',
            'strength': abs(trend),
            'momentum': momentum,
            'sustainability': min(abs(trend) * 2, 1.0)
        }
    
    def _analyze_correlations(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze correlation structure"""
        # Mock correlation analysis
        return {
            'avg_correlation': 0.6,
            'correlation_regime': 'normal',
            'diversification_benefit': 0.4,
            'tail_risk': 0.2
        }
    
    def _assess_liquidity(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market liquidity conditions"""
        volume = market_data.get('volume', 1000000)
        spread = market_data.get('spread', 0.001)
        
        return {
            'liquidity_score': min(volume / 1000000, 1.0),
            'spread_conditions': 'tight' if spread < 0.002 else 'wide',
            'market_depth': 'deep' if volume > 2000000 else 'shallow'
        }
    
    def _analyze_esg_trends(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ESG trends and momentum"""
        esg_score = market_data.get('esg_score', 0.7)
        esg_momentum = market_data.get('esg_momentum', 0.05)
        
        return {
            'esg_score': esg_score,
            'esg_momentum': esg_momentum,
            'esg_trend': 'improving' if esg_momentum > 0 else 'declining',
            'esg_alpha': esg_momentum * 0.1
        }
    
    def _identify_risk_factors(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify key risk factors"""
        risk_factors = []
        
        volatility = market_data.get('volatility', 0.02)
        if volatility > 0.03:
            risk_factors.append({
                'factor': 'high_volatility',
                'severity': 'medium',
                'description': 'Elevated volatility detected'
            })
        
        correlation = market_data.get('correlation', 0.5)
        if correlation > 0.8:
            risk_factors.append({
                'factor': 'high_correlation',
                'severity': 'high',
                'description': 'High correlation reduces diversification benefits'
            })
        
        return risk_factors
    
    def _identify_opportunities(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify trading opportunities"""
        opportunities = []
        
        momentum = market_data.get('momentum', 0)
        if abs(momentum) > 0.02:
            opportunities.append({
                'type': 'momentum_opportunity',
                'strength': 'strong' if abs(momentum) > 0.05 else 'moderate',
                'description': f'Momentum signal detected: {momentum:.3f}'
            })
        
        esg_score = market_data.get('esg_score', 0.7)
        if esg_score > 0.8:
            opportunities.append({
                'type': 'esg_opportunity',
                'strength': 'strong',
                'description': 'High ESG score presents sustainable investment opportunity'
            })
        
        return opportunities
    
    def _generate_technical_signals(self, commodity: str, market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate technical analysis signals"""
        insights = []
        
        # Mock technical indicators
        rsi = market_data.get('rsi', 50)
        macd = market_data.get('macd', 0)
        bollinger_position = market_data.get('bollinger_position', 0.5)
        
        # RSI signals
        if rsi < 30:
            insights.append(TradingInsight(
                insight_id=f"rsi_oversold_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.TRADING_SIGNAL,
                commodity=commodity,
                signal="BUY",
                strength=SignalStrength.STRONG,
                confidence=0.85,
                reasoning=f"RSI oversold at {rsi:.1f}, potential reversal",
                supporting_data={'rsi': rsi, 'indicator': 'RSI'},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(hours=24),
                priority=4
            ))
        elif rsi > 70:
            insights.append(TradingInsight(
                insight_id=f"rsi_overbought_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.TRADING_SIGNAL,
                commodity=commodity,
                signal="SELL",
                strength=SignalStrength.MODERATE,
                confidence=0.75,
                reasoning=f"RSI overbought at {rsi:.1f}, potential correction",
                supporting_data={'rsi': rsi, 'indicator': 'RSI'},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(hours=24),
                priority=3
            ))
        
        # MACD signals
        if macd > 0.01:
            insights.append(TradingInsight(
                insight_id=f"macd_bullish_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.TRADING_SIGNAL,
                commodity=commodity,
                signal="BUY",
                strength=SignalStrength.MODERATE,
                confidence=0.70,
                reasoning=f"MACD bullish crossover at {macd:.3f}",
                supporting_data={'macd': macd, 'indicator': 'MACD'},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(hours=48),
                priority=3
            ))
        
        return insights
    
    def _generate_fundamental_signals(self, commodity: str, market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate fundamental analysis signals"""
        insights = []
        
        # Mock fundamental analysis
        pe_ratio = market_data.get('pe_ratio', 15)
        growth_rate = market_data.get('growth_rate', 0.05)
        
        if pe_ratio < 10 and growth_rate > 0.1:
            insights.append(TradingInsight(
                insight_id=f"fundamental_undervalued_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.TRADING_SIGNAL,
                commodity=commodity,
                signal="BUY",
                strength=SignalStrength.VERY_STRONG,
                confidence=0.90,
                reasoning=f"Undervalued with PE {pe_ratio} and growth {growth_rate:.1%}",
                supporting_data={'pe_ratio': pe_ratio, 'growth_rate': growth_rate},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(days=7),
                priority=5
            ))
        
        return insights
    
    def _generate_esg_signals(self, commodity: str, market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate ESG-based trading signals"""
        insights = []
        
        esg_score = market_data.get('esg_score', 0.7)
        esg_momentum = market_data.get('esg_momentum', 0.05)
        
        if esg_score > 0.8 and esg_momentum > 0.02:
            insights.append(TradingInsight(
                insight_id=f"esg_positive_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.ESG_INSIGHT,
                commodity=commodity,
                signal="BUY",
                strength=SignalStrength.STRONG,
                confidence=0.80,
                reasoning=f"Strong ESG performance: score {esg_score:.2f}, momentum {esg_momentum:.3f}",
                supporting_data={'esg_score': esg_score, 'esg_momentum': esg_momentum},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(days=14),
                priority=4
            ))
        
        return insights
    
    def _generate_risk_signals(self, commodity: str, market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate risk-based signals"""
        insights = []
        
        var_95 = market_data.get('var_95', 0.02)
        volatility = market_data.get('volatility', 0.02)
        
        if var_95 > 0.05 or volatility > 0.04:
            insights.append(TradingInsight(
                insight_id=f"risk_alert_{commodity}_{datetime.now().timestamp()}",
                insight_type=InsightType.RISK_ALERT,
                commodity=commodity,
                signal="HOLD",
                strength=SignalStrength.STRONG,
                confidence=0.85,
                reasoning=f"High risk detected: VaR {var_95:.3f}, volatility {volatility:.3f}",
                supporting_data={'var_95': var_95, 'volatility': volatility},
                timestamp=datetime.now(),
                expiry=datetime.now() + timedelta(hours=12),
                priority=5
            ))
        
        return insights
    
    def get_portfolio_insights(self, portfolio: Dict[str, float], 
                              market_data: Dict[str, Any]) -> List[TradingInsight]:
        """Generate portfolio-level insights"""
        try:
            insights = []
            
            # Portfolio concentration analysis
            max_weight = max(portfolio.values())
            if max_weight > 0.4:
                insights.append(TradingInsight(
                    insight_id=f"concentration_risk_{datetime.now().timestamp()}",
                    insight_type=InsightType.RISK_ALERT,
                    commodity="portfolio",
                    signal="REBALANCE",
                    strength=SignalStrength.MODERATE,
                    confidence=0.75,
                    reasoning=f"High concentration risk: max weight {max_weight:.1%}",
                    supporting_data={'max_weight': max_weight, 'portfolio': portfolio},
                    timestamp=datetime.now(),
                    expiry=datetime.now() + timedelta(days=3),
                    priority=3
                ))
            
            # Diversification analysis
            num_assets = len(portfolio)
            if num_assets < 3:
                insights.append(TradingInsight(
                    insight_id=f"diversification_{datetime.now().timestamp()}",
                    insight_type=InsightType.OPTIMIZATION_RECOMMENDATION,
                    commodity="portfolio",
                    signal="DIVERSIFY",
                    strength=SignalStrength.MODERATE,
                    confidence=0.70,
                    reasoning=f"Low diversification: only {num_assets} assets",
                    supporting_data={'num_assets': num_assets, 'portfolio': portfolio},
                    timestamp=datetime.now(),
                    expiry=datetime.now() + timedelta(days=7),
                    priority=2
                ))
            
            return insights
            
        except Exception as e:
            logger.error("Portfolio insights generation failed", error=str(e))
            raise
    
    def get_insights(self, commodities: List[str], 
                    market_data: Dict[str, Any],
                    portfolio: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """Main method to get all AI insights"""
        try:
            # Market analysis
            market_analysis = self.analyze_market_conditions(market_data)
            
            # Trading signals
            trading_signals = self.generate_trading_signals(commodities, market_data)
            
            # Portfolio insights
            portfolio_insights = []
            if portfolio:
                portfolio_insights = self.get_portfolio_insights(portfolio, market_data)
            
            # Combine all insights
            all_insights = trading_signals + portfolio_insights
            
            # Sort by priority and confidence
            all_insights.sort(key=lambda x: (x.priority, x.confidence), reverse=True)
            
            return {
                'market_analysis': market_analysis,
                'trading_signals': [self._insight_to_dict(insight) for insight in trading_signals],
                'portfolio_insights': [self._insight_to_dict(insight) for insight in portfolio_insights],
                'all_insights': [self._insight_to_dict(insight) for insight in all_insights],
                'summary': {
                    'total_insights': len(all_insights),
                    'high_priority': len([i for i in all_insights if i.priority >= 4]),
                    'buy_signals': len([i for i in all_insights if i.signal == 'BUY']),
                    'sell_signals': len([i for i in all_insights if i.signal == 'SELL']),
                    'risk_alerts': len([i for i in all_insights if i.insight_type == InsightType.RISK_ALERT])
                }
            }
            
        except Exception as e:
            logger.error("AI insights generation failed", error=str(e))
            raise
    
    def _insight_to_dict(self, insight: TradingInsight) -> Dict[str, Any]:
        """Convert insight to dictionary"""
        return {
            'insight_id': insight.insight_id,
            'insight_type': insight.insight_type.value,
            'commodity': insight.commodity,
            'signal': insight.signal,
            'strength': insight.strength.value,
            'confidence': insight.confidence,
            'reasoning': insight.reasoning,
            'supporting_data': insight.supporting_data,
            'timestamp': insight.timestamp.isoformat(),
            'expiry': insight.expiry.isoformat(),
            'priority': insight.priority
        }

# Global AI insights engine instance
ai_insights_engine = AIInsightsEngine()
