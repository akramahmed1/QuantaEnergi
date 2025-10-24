"""
Advanced Cryptocurrency Modeling Service for QuantaEnergi
Comprehensive crypto analysis, pricing, and risk management
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
import aiohttp
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoAssetType(Enum):
    """Cryptocurrency asset types"""
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"
    ALTCOIN = "altcoin"
    DEFI_TOKEN = "defi_token"
    NFT = "nft"
    STABLECOIN = "stablecoin"

class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class TradingSignal(Enum):
    """Trading signals"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class CryptoAsset:
    """Cryptocurrency asset structure"""
    symbol: str
    name: str
    asset_type: CryptoAssetType
    current_price: float
    market_cap: float
    volume_24h: float
    price_change_24h: float
    volatility: float
    risk_level: RiskLevel
    last_updated: datetime

class AdvancedCryptoModelingService:
    """
    Advanced cryptocurrency modeling and analysis service
    """
    
    def __init__(self):
        self.crypto_assets = {}
        self.price_history = {}
        self.technical_indicators = {}
        self.correlation_matrix = {}
        self.portfolio_optimization = {}
        self.risk_models = {}
        self.trading_signals = {}
        self.market_sentiment = {}
        
    def add_crypto_asset(self, asset: CryptoAsset) -> Dict[str, Any]:
        """Add cryptocurrency asset to tracking"""
        try:
            self.crypto_assets[asset.symbol] = asset
            
            # Initialize price history
            self.price_history[asset.symbol] = []
            
            # Initialize technical indicators
            self.technical_indicators[asset.symbol] = {}
            
            return {
                "status": "success",
                "asset_symbol": asset.symbol,
                "asset_name": asset.name,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Asset addition error: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_price_data(self, symbol: str, price_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update price data for cryptocurrency"""
        try:
            if symbol not in self.crypto_assets:
                return {"status": "error", "message": f"Asset {symbol} not found"}
            
            # Update asset price
            asset = self.crypto_assets[symbol]
            asset.current_price = price_data.get("price", asset.current_price)
            asset.volume_24h = price_data.get("volume_24h", asset.volume_24h)
            asset.price_change_24h = price_data.get("price_change_24h", asset.price_change_24h)
            asset.last_updated = datetime.now()
            
            # Add to price history
            price_point = {
                "timestamp": datetime.now().isoformat(),
                "price": asset.current_price,
                "volume": asset.volume_24h,
                "change": asset.price_change_24h
            }
            
            self.price_history[symbol].append(price_point)
            
            # Keep only last 1000 data points
            if len(self.price_history[symbol]) > 1000:
                self.price_history[symbol] = self.price_history[symbol][-1000:]
            
            # Update technical indicators
            self._update_technical_indicators(symbol)
            
            # Update risk assessment
            self._update_risk_assessment(symbol)
            
            return {
                "status": "success",
                "symbol": symbol,
                "updated_price": asset.current_price,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Price data update error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _update_technical_indicators(self, symbol: str):
        """Update technical indicators for cryptocurrency"""
        try:
            if symbol not in self.price_history or len(self.price_history[symbol]) < 20:
                return
            
            prices = [point["price"] for point in self.price_history[symbol]]
            
            # Calculate moving averages
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
            
            # Calculate RSI
            rsi = self._calculate_rsi(prices)
            
            # Calculate MACD
            macd = self._calculate_macd(prices)
            
            # Calculate Bollinger Bands
            bollinger_bands = self._calculate_bollinger_bands(prices)
            
            # Calculate volatility
            volatility = self._calculate_volatility(prices)
            
            # Store indicators
            self.technical_indicators[symbol] = {
                "sma_20": sma_20,
                "sma_50": sma_50,
                "rsi": rsi,
                "macd": macd,
                "bollinger_bands": bollinger_bands,
                "volatility": volatility,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Technical indicators update error: {e}")
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        try:
            if len(prices) < period + 1:
                return 50.0  # Neutral RSI
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return round(rsi, 2)
            
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return 50.0
    
    def _calculate_macd(self, prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            if len(prices) < slow_period:
                return {"macd": 0, "signal": 0, "histogram": 0}
            
            prices_array = np.array(prices)
            
            # Calculate EMAs
            ema_fast = self._calculate_ema(prices_array, fast_period)
            ema_slow = self._calculate_ema(prices_array, slow_period)
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line (EMA of MACD)
            signal_line = self._calculate_ema(macd_line, signal_period)
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            return {
                "macd": round(macd_line[-1], 4),
                "signal": round(signal_line[-1], 4),
                "histogram": round(histogram[-1], 4)
            }
            
        except Exception as e:
            logger.error(f"MACD calculation error: {e}")
            return {"macd": 0, "signal": 0, "histogram": 0}
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        try:
            alpha = 2 / (period + 1)
            ema = np.zeros_like(prices)
            ema[0] = prices[0]
            
            for i in range(1, len(prices)):
                ema[i] = alpha * prices[i] + (1 - alpha) * ema[i-1]
            
            return ema
            
        except Exception as e:
            logger.error(f"EMA calculation error: {e}")
            return np.zeros_like(prices)
    
    def _calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calculate Bollinger Bands"""
        try:
            if len(prices) < period:
                current_price = prices[-1]
                return {
                    "upper": current_price * 1.1,
                    "middle": current_price,
                    "lower": current_price * 0.9
                }
            
            prices_array = np.array(prices[-period:])
            sma = np.mean(prices_array)
            std = np.std(prices_array)
            
            return {
                "upper": round(sma + (std_dev * std), 2),
                "middle": round(sma, 2),
                "lower": round(sma - (std_dev * std), 2)
            }
            
        except Exception as e:
            logger.error(f"Bollinger Bands calculation error: {e}")
            return {"upper": 0, "middle": 0, "lower": 0}
    
    def _calculate_volatility(self, prices: List[float], period: int = 20) -> float:
        """Calculate volatility"""
        try:
            if len(prices) < 2:
                return 0.0
            
            returns = np.diff(np.log(prices))
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            
            return round(volatility, 4)
            
        except Exception as e:
            logger.error(f"Volatility calculation error: {e}")
            return 0.0
    
    def _update_risk_assessment(self, symbol: str):
        """Update risk assessment for cryptocurrency"""
        try:
            if symbol not in self.crypto_assets:
                return
            
            asset = self.crypto_assets[symbol]
            
            # Calculate risk score based on volatility and market cap
            volatility = asset.volatility
            market_cap = asset.market_cap
            
            # Risk scoring algorithm
            risk_score = 0
            
            # Volatility risk (0-40 points)
            if volatility > 0.8:
                risk_score += 40
            elif volatility > 0.6:
                risk_score += 30
            elif volatility > 0.4:
                risk_score += 20
            elif volatility > 0.2:
                risk_score += 10
            
            # Market cap risk (0-30 points)
            if market_cap < 1000000000:  # < $1B
                risk_score += 30
            elif market_cap < 10000000000:  # < $10B
                risk_score += 20
            elif market_cap < 100000000000:  # < $100B
                risk_score += 10
            
            # Price change risk (0-30 points)
            price_change_abs = abs(asset.price_change_24h)
            if price_change_abs > 20:
                risk_score += 30
            elif price_change_abs > 10:
                risk_score += 20
            elif price_change_abs > 5:
                risk_score += 10
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = RiskLevel.VERY_HIGH
            elif risk_score >= 60:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 40:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Update asset risk level
            asset.risk_level = risk_level
            
            # Store risk model
            self.risk_models[symbol] = {
                "risk_score": risk_score,
                "risk_level": risk_level.value,
                "volatility": volatility,
                "market_cap": market_cap,
                "price_change_24h": asset.price_change_24h,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Risk assessment update error: {e}")
    
    def generate_trading_signals(self, symbol: str) -> Dict[str, Any]:
        """Generate trading signals for cryptocurrency"""
        try:
            if symbol not in self.technical_indicators:
                return {"status": "error", "message": f"No technical indicators for {symbol}"}
            
            indicators = self.technical_indicators[symbol]
            asset = self.crypto_assets[symbol]
            
            signal_score = 0
            signal_reasons = []
            
            # RSI signals
            rsi = indicators.get("rsi", 50)
            if rsi < 30:
                signal_score += 2  # Oversold
                signal_reasons.append("RSI indicates oversold condition")
            elif rsi > 70:
                signal_score -= 2  # Overbought
                signal_reasons.append("RSI indicates overbought condition")
            
            # MACD signals
            macd = indicators.get("macd", {})
            macd_line = macd.get("macd", 0)
            signal_line = macd.get("signal", 0)
            
            if macd_line > signal_line:
                signal_score += 1
                signal_reasons.append("MACD bullish crossover")
            elif macd_line < signal_line:
                signal_score -= 1
                signal_reasons.append("MACD bearish crossover")
            
            # Moving average signals
            sma_20 = indicators.get("sma_20", asset.current_price)
            sma_50 = indicators.get("sma_50", asset.current_price)
            
            if asset.current_price > sma_20 > sma_50:
                signal_score += 1
                signal_reasons.append("Price above moving averages")
            elif asset.current_price < sma_20 < sma_50:
                signal_score -= 1
                signal_reasons.append("Price below moving averages")
            
            # Bollinger Bands signals
            bollinger = indicators.get("bollinger_bands", {})
            upper_band = bollinger.get("upper", asset.current_price)
            lower_band = bollinger.get("lower", asset.current_price)
            
            if asset.current_price <= lower_band:
                signal_score += 1
                signal_reasons.append("Price at lower Bollinger Band")
            elif asset.current_price >= upper_band:
                signal_score -= 1
                signal_reasons.append("Price at upper Bollinger Band")
            
            # Determine signal
            if signal_score >= 3:
                signal = TradingSignal.STRONG_BUY
            elif signal_score >= 1:
                signal = TradingSignal.BUY
            elif signal_score <= -3:
                signal = TradingSignal.STRONG_SELL
            elif signal_score <= -1:
                signal = TradingSignal.SELL
            else:
                signal = TradingSignal.HOLD
            
            # Store trading signal
            self.trading_signals[symbol] = {
                "signal": signal.value,
                "signal_score": signal_score,
                "reasons": signal_reasons,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "symbol": symbol,
                "signal": signal.value,
                "signal_score": signal_score,
                "reasons": signal_reasons,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Trading signal generation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def calculate_portfolio_optimization(self, symbols: List[str], target_return: float = 0.1) -> Dict[str, Any]:
        """Calculate portfolio optimization for cryptocurrency portfolio"""
        try:
            if len(symbols) < 2:
                return {"status": "error", "message": "Need at least 2 assets for portfolio optimization"}
            
            # Get price data for all symbols
            price_data = {}
            for symbol in symbols:
                if symbol in self.price_history and len(self.price_history[symbol]) >= 30:
                    prices = [point["price"] for point in self.price_history[symbol][-30:]]
                    price_data[symbol] = prices
                else:
                    return {"status": "error", "message": f"Insufficient price data for {symbol}"}
            
            # Calculate returns
            returns_data = {}
            for symbol, prices in price_data.items():
                returns = np.diff(np.log(prices))
                returns_data[symbol] = returns
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            
            # Calculate expected returns and covariance matrix
            expected_returns = returns_df.mean() * 252  # Annualized
            cov_matrix = returns_df.cov() * 252  # Annualized
            
            # Portfolio optimization using Markowitz mean-variance optimization
            def portfolio_variance(weights, cov_matrix):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            def portfolio_return(weights, expected_returns):
                return np.sum(expected_returns * weights)
            
            # Constraints: weights sum to 1
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            
            # Bounds: weights between 0 and 1
            bounds = tuple((0, 1) for _ in range(len(symbols)))
            
            # Initial guess: equal weights
            initial_weights = np.array([1/len(symbols)] * len(symbols))
            
            # Optimize for minimum variance
            min_var_result = minimize(
                portfolio_variance,
                initial_weights,
                args=(cov_matrix,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            # Optimize for target return
            target_return_constraint = {
                'type': 'eq',
                'fun': lambda x: portfolio_return(x, expected_returns) - target_return
            }
            
            constraints_with_return = [constraints[0], target_return_constraint]
            
            target_return_result = minimize(
                portfolio_variance,
                initial_weights,
                args=(cov_matrix,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_with_return
            )
            
            # Calculate portfolio metrics
            min_var_weights = min_var_result.x
            target_return_weights = target_return_result.x
            
            min_var_return = portfolio_return(min_var_weights, expected_returns)
            min_var_volatility = np.sqrt(portfolio_variance(min_var_weights, cov_matrix))
            
            target_return_volatility = np.sqrt(portfolio_variance(target_return_weights, cov_matrix))
            
            # Store optimization results
            self.portfolio_optimization = {
                "symbols": symbols,
                "min_variance_portfolio": {
                    "weights": dict(zip(symbols, min_var_weights)),
                    "expected_return": round(min_var_return, 4),
                    "volatility": round(min_var_volatility, 4)
                },
                "target_return_portfolio": {
                    "weights": dict(zip(symbols, target_return_weights)),
                    "expected_return": round(target_return, 4),
                    "volatility": round(target_return_volatility, 4)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "portfolio_optimization": self.portfolio_optimization
            }
            
        except Exception as e:
            logger.error(f"Portfolio optimization error: {e}")
            return {"status": "error", "message": str(e)}
    
    def calculate_correlation_matrix(self, symbols: List[str]) -> Dict[str, Any]:
        """Calculate correlation matrix for cryptocurrencies"""
        try:
            if len(symbols) < 2:
                return {"status": "error", "message": "Need at least 2 assets for correlation analysis"}
            
            # Get price data for all symbols
            price_data = {}
            for symbol in symbols:
                if symbol in self.price_history and len(self.price_history[symbol]) >= 30:
                    prices = [point["price"] for point in self.price_history[symbol][-30:]]
                    price_data[symbol] = prices
                else:
                    return {"status": "error", "message": f"Insufficient price data for {symbol}"}
            
            # Calculate returns
            returns_data = {}
            for symbol, prices in price_data.items():
                returns = np.diff(np.log(prices))
                returns_data[symbol] = returns
            
            # Create returns DataFrame
            returns_df = pd.DataFrame(returns_data)
            
            # Calculate correlation matrix
            correlation_matrix = returns_df.corr().to_dict()
            
            # Store correlation matrix
            self.correlation_matrix = {
                "symbols": symbols,
                "correlation_matrix": correlation_matrix,
                "timestamp": datetime.now().isoformat()
            }
            
            return {
                "status": "success",
                "correlation_matrix": self.correlation_matrix
            }
            
        except Exception as e:
            logger.error(f"Correlation matrix calculation error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_crypto_analytics(self, symbol: str = None) -> Dict[str, Any]:
        """Get comprehensive crypto analytics"""
        try:
            if symbol:
                if symbol not in self.crypto_assets:
                    return {"status": "error", "message": f"Asset {symbol} not found"}
                
                asset = self.crypto_assets[symbol]
                indicators = self.technical_indicators.get(symbol, {})
                risk_model = self.risk_models.get(symbol, {})
                trading_signal = self.trading_signals.get(symbol, {})
                
                return {
                    "status": "success",
                    "symbol": symbol,
                    "asset": {
                        "name": asset.name,
                        "current_price": asset.current_price,
                        "market_cap": asset.market_cap,
                        "volume_24h": asset.volume_24h,
                        "price_change_24h": asset.price_change_24h,
                        "risk_level": asset.risk_level.value,
                        "last_updated": asset.last_updated.isoformat()
                    },
                    "technical_indicators": indicators,
                    "risk_model": risk_model,
                    "trading_signal": trading_signal,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return all assets
                assets_list = []
                for symbol, asset in self.crypto_assets.items():
                    indicators = self.technical_indicators.get(symbol, {})
                    risk_model = self.risk_models.get(symbol, {})
                    trading_signal = self.trading_signals.get(symbol, {})
                    
                    assets_list.append({
                        "symbol": symbol,
                        "name": asset.name,
                        "current_price": asset.current_price,
                        "market_cap": asset.market_cap,
                        "volume_24h": asset.volume_24h,
                        "price_change_24h": asset.price_change_24h,
                        "risk_level": asset.risk_level.value,
                        "technical_indicators": indicators,
                        "risk_model": risk_model,
                        "trading_signal": trading_signal
                    })
                
                return {
                    "status": "success",
                    "assets": assets_list,
                    "total_count": len(assets_list),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Crypto analytics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_crypto_statistics(self) -> Dict[str, Any]:
        """Get crypto modeling service statistics"""
        try:
            total_assets = len(self.crypto_assets)
            total_price_points = sum(len(history) for history in self.price_history.values())
            
            # Count by risk level
            risk_breakdown = {}
            for asset in self.crypto_assets.values():
                risk_level = asset.risk_level.value
                risk_breakdown[risk_level] = risk_breakdown.get(risk_level, 0) + 1
            
            # Count by trading signal
            signal_breakdown = {}
            for signal in self.trading_signals.values():
                signal_type = signal.get("signal", "hold")
                signal_breakdown[signal_type] = signal_breakdown.get(signal_type, 0) + 1
            
            return {
                "status": "success",
                "statistics": {
                    "total_assets": total_assets,
                    "total_price_points": total_price_points,
                    "risk_breakdown": risk_breakdown,
                    "signal_breakdown": signal_breakdown,
                    "portfolio_optimizations": len(self.portfolio_optimization),
                    "correlation_matrices": len(self.correlation_matrix)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Statistics retrieval error: {e}")
            return {"status": "error", "message": str(e)}
