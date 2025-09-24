"""
Market Data Processing Tasks
High-frequency market data processing using Celery
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp

from celery import current_task
from celery.exceptions import Retry
import numpy as np
import pandas as pd
import structlog

from app.core.celery_app import celery_app

logger = structlog.get_logger(__name__)

# Configure multiprocessing
mp.set_start_method('spawn', force=True)


@celery_app.task(bind=True, name="app.tasks.market_data_processing.process_realtime_data")
def process_realtime_data(self, market_data: Dict[str, Any], 
                         tenant_id: str = "system") -> Dict[str, Any]:
    """
    Process real-time market data
    
    Args:
        market_data: Raw market data
        tenant_id: Tenant identifier
        
    Returns:
        Processed market data
    """
    try:
        logger.info("Starting real-time market data processing", 
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Extract data
        commodities = market_data.get("commodities", [])
        raw_prices = market_data.get("prices", {})
        
        # Process data in parallel
        with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = []
            
            for commodity in commodities:
                future = executor.submit(
                    _process_commodity_data,
                    commodity,
                    raw_prices.get(commodity, {}),
                    tenant_id
                )
                futures.append((commodity, future))
            
            # Collect results
            processed_data = {}
            for commodity, future in futures:
                try:
                    result = future.result(timeout=30)
                    processed_data[commodity] = result
                except Exception as e:
                    logger.error("Commodity data processing failed", 
                               commodity=commodity,
                               error=str(e))
                    processed_data[commodity] = {"error": str(e)}
        
        # Calculate cross-commodity correlations
        correlations = _calculate_correlations(processed_data)
        
        duration = time.time() - start_time
        
        result = {
            "processed_data": processed_data,
            "correlations": correlations,
            "processing_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Real-time market data processing completed", 
                   tenant_id=tenant_id,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Real-time market data processing failed", 
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=30, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.market_data_processing.calculate_technical_indicators")
def calculate_technical_indicators(self, commodity: str, price_data: List[Dict], 
                                  tenant_id: str = "system") -> Dict[str, Any]:
    """
    Calculate technical indicators for a commodity
    
    Args:
        commodity: Commodity name
        price_data: Historical price data
        tenant_id: Tenant identifier
        
    Returns:
        Technical indicators
    """
    try:
        logger.info("Starting technical indicators calculation", 
                   commodity=commodity,
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Convert to DataFrame
        df = pd.DataFrame(price_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate indicators using multiprocessing
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = {
                'sma': executor.submit(_calculate_sma, df),
                'ema': executor.submit(_calculate_ema, df),
                'rsi': executor.submit(_calculate_rsi, df),
                'macd': executor.submit(_calculate_macd, df),
                'bollinger': executor.submit(_calculate_bollinger_bands, df),
                'atr': executor.submit(_calculate_atr, df)
            }
            
            # Collect results
            indicators = {}
            for name, future in futures.items():
                try:
                    indicators[name] = future.result(timeout=60)
                except Exception as e:
                    logger.error("Technical indicator calculation failed", 
                               indicator=name,
                               commodity=commodity,
                               error=str(e))
                    indicators[name] = {"error": str(e)}
        
        duration = time.time() - start_time
        
        result = {
            "commodity": commodity,
            "indicators": indicators,
            "calculation_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Technical indicators calculation completed", 
                   commodity=commodity,
                   tenant_id=tenant_id,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Technical indicators calculation failed", 
                    commodity=commodity,
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.market_data_processing.detect_market_anomalies")
def detect_market_anomalies(self, market_data: Dict[str, Any], 
                           tenant_id: str = "system") -> Dict[str, Any]:
    """
    Detect market anomalies using statistical methods
    
    Args:
        market_data: Market data
        tenant_id: Tenant identifier
        
    Returns:
        Detected anomalies
    """
    try:
        logger.info("Starting market anomaly detection", 
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Process each commodity
        anomalies = {}
        commodities = market_data.get("commodities", [])
        
        with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
            futures = []
            
            for commodity in commodities:
                price_data = market_data.get("prices", {}).get(commodity, [])
                future = executor.submit(
                    _detect_commodity_anomalies,
                    commodity,
                    price_data
                )
                futures.append((commodity, future))
            
            # Collect results
            for commodity, future in futures:
                try:
                    result = future.result(timeout=60)
                    anomalies[commodity] = result
                except Exception as e:
                    logger.error("Anomaly detection failed", 
                               commodity=commodity,
                               error=str(e))
                    anomalies[commodity] = {"error": str(e)}
        
        duration = time.time() - start_time
        
        result = {
            "anomalies": anomalies,
            "detection_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Market anomaly detection completed", 
                   tenant_id=tenant_id,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Market anomaly detection failed", 
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@celery_app.task(bind=True, name="app.tasks.market_data_processing.generate_trading_signals")
def generate_trading_signals(self, market_data: Dict[str, Any], 
                           tenant_id: str = "system") -> Dict[str, Any]:
    """
    Generate trading signals based on market data
    
    Args:
        market_data: Market data
        tenant_id: Tenant identifier
        
    Returns:
        Trading signals
    """
    try:
        logger.info("Starting trading signal generation", 
                   tenant_id=tenant_id,
                   task_id=self.request.id)
        
        start_time = time.time()
        
        # Get technical indicators
        indicators_task = calculate_technical_indicators.delay(
            "crude_oil",  # Example commodity
            market_data.get("prices", {}).get("crude_oil", [])
        )
        
        # Get anomaly detection results
        anomalies_task = detect_market_anomalies.delay(market_data, tenant_id)
        
        # Wait for results
        indicators = indicators_task.get(timeout=120)
        anomalies = anomalies_task.get(timeout=120)
        
        # Generate signals based on indicators and anomalies
        signals = _generate_signals_from_data(indicators, anomalies, market_data)
        
        duration = time.time() - start_time
        
        result = {
            "signals": signals,
            "generation_time": duration,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant_id": tenant_id
        }
        
        logger.info("Trading signal generation completed", 
                   tenant_id=tenant_id,
                   duration=duration,
                   task_id=self.request.id)
        
        return result
        
    except Exception as exc:
        logger.error("Trading signal generation failed", 
                    tenant_id=tenant_id,
                    error=str(exc),
                    task_id=self.request.id)
        raise self.retry(exc=exc, countdown=60, max_retries=3)


def _process_commodity_data(commodity: str, raw_data: Dict[str, Any], 
                          tenant_id: str) -> Dict[str, Any]:
    """
    Process data for a single commodity
    
    Args:
        commodity: Commodity name
        raw_data: Raw commodity data
        tenant_id: Tenant identifier
        
    Returns:
        Processed commodity data
    """
    try:
        # Extract price data
        prices = raw_data.get("prices", [])
        volumes = raw_data.get("volumes", [])
        
        # Calculate basic statistics
        price_changes = []
        for i in range(1, len(prices)):
            change = (prices[i] - prices[i-1]) / prices[i-1]
            price_changes.append(change)
        
        # Calculate volatility
        volatility = np.std(price_changes) if price_changes else 0.0
        
        # Calculate moving averages
        sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else np.mean(prices)
        sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else np.mean(prices)
        
        # Calculate volume-weighted average price
        if volumes and prices:
            vwap = np.sum(np.array(prices) * np.array(volumes)) / np.sum(volumes)
        else:
            vwap = np.mean(prices) if prices else 0.0
        
        return {
            "commodity": commodity,
            "current_price": prices[-1] if prices else 0.0,
            "volatility": volatility,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "vwap": vwap,
            "price_changes": price_changes,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Commodity data processing failed", 
                    commodity=commodity,
                    error=str(e))
        return {"error": str(e)}


def _calculate_correlations(processed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate cross-commodity correlations
    
    Args:
        processed_data: Processed commodity data
        
    Returns:
        Correlation matrix
    """
    try:
        commodities = list(processed_data.keys())
        correlations = {}
        
        for i, comm1 in enumerate(commodities):
            for j, comm2 in enumerate(commodities):
                if i < j:  # Only calculate upper triangle
                    data1 = processed_data[comm1].get("price_changes", [])
                    data2 = processed_data[comm2].get("price_changes", [])
                    
                    if data1 and data2:
                        # Ensure same length
                        min_len = min(len(data1), len(data2))
                        corr = np.corrcoef(data1[:min_len], data2[:min_len])[0, 1]
                        correlations[f"{comm1}_{comm2}"] = float(corr)
        
        return correlations
        
    except Exception as e:
        logger.error("Correlation calculation failed", error=str(e))
        return {"error": str(e)}


def _calculate_sma(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Simple Moving Average"""
    try:
        periods = [10, 20, 50, 200]
        sma_data = {}
        
        for period in periods:
            if len(df) >= period:
                sma_data[f"sma_{period}"] = df['price'].rolling(window=period).mean().iloc[-1]
        
        return sma_data
    except Exception as e:
        return {"error": str(e)}


def _calculate_ema(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Exponential Moving Average"""
    try:
        periods = [12, 26, 50]
        ema_data = {}
        
        for period in periods:
            if len(df) >= period:
                ema_data[f"ema_{period}"] = df['price'].ewm(span=period).mean().iloc[-1]
        
        return ema_data
    except Exception as e:
        return {"error": str(e)}


def _calculate_rsi(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Relative Strength Index"""
    try:
        if len(df) < 14:
            return {"error": "Insufficient data for RSI"}
        
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {"rsi": rsi.iloc[-1]}
    except Exception as e:
        return {"error": str(e)}


def _calculate_macd(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate MACD"""
    try:
        if len(df) < 26:
            return {"error": "Insufficient data for MACD"}
        
        ema_12 = df['price'].ewm(span=12).mean()
        ema_26 = df['price'].ewm(span=26).mean()
        
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()
        histogram = macd - signal
        
        return {
            "macd": macd.iloc[-1],
            "signal": signal.iloc[-1],
            "histogram": histogram.iloc[-1]
        }
    except Exception as e:
        return {"error": str(e)}


def _calculate_bollinger_bands(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Bollinger Bands"""
    try:
        if len(df) < 20:
            return {"error": "Insufficient data for Bollinger Bands"}
        
        sma_20 = df['price'].rolling(window=20).mean()
        std_20 = df['price'].rolling(window=20).std()
        
        upper_band = sma_20 + (std_20 * 2)
        lower_band = sma_20 - (std_20 * 2)
        
        return {
            "upper_band": upper_band.iloc[-1],
            "middle_band": sma_20.iloc[-1],
            "lower_band": lower_band.iloc[-1]
        }
    except Exception as e:
        return {"error": str(e)}


def _calculate_atr(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate Average True Range"""
    try:
        if len(df) < 14:
            return {"error": "Insufficient data for ATR"}
        
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=14).mean()
        
        return {"atr": atr.iloc[-1]}
    except Exception as e:
        return {"error": str(e)}


def _detect_commodity_anomalies(commodity: str, price_data: List[Dict]) -> Dict[str, Any]:
    """
    Detect anomalies for a single commodity
    
    Args:
        commodity: Commodity name
        price_data: Price data
        
    Returns:
        Detected anomalies
    """
    try:
        if not price_data:
            return {"error": "No price data"}
        
        prices = [d["price"] for d in price_data]
        
        # Calculate Z-scores
        mean_price = np.mean(prices)
        std_price = np.std(prices)
        
        anomalies = []
        for i, price in enumerate(prices):
            z_score = abs((price - mean_price) / std_price) if std_price > 0 else 0
            
            if z_score > 3:  # 3-sigma rule
                anomalies.append({
                    "timestamp": price_data[i].get("timestamp"),
                    "price": price,
                    "z_score": z_score,
                    "severity": "high" if z_score > 4 else "medium"
                })
        
        return {
            "commodity": commodity,
            "anomalies": anomalies,
            "total_anomalies": len(anomalies)
        }
        
    except Exception as e:
        return {"error": str(e)}


def _generate_signals_from_data(indicators: Dict[str, Any], 
                               anomalies: Dict[str, Any], 
                               market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate trading signals from indicators and anomalies
    
    Args:
        indicators: Technical indicators
        anomalies: Market anomalies
        market_data: Market data
        
    Returns:
        Trading signals
    """
    signals = []
    
    try:
        # Simple signal generation logic
        for commodity in market_data.get("commodities", []):
            signal = {
                "commodity": commodity,
                "signal": "HOLD",
                "confidence": 0.5,
                "reason": "No clear signal",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Check for anomalies
            commodity_anomalies = anomalies.get("anomalies", {}).get(commodity, {})
            if commodity_anomalies.get("total_anomalies", 0) > 0:
                signal["signal"] = "SELL"
                signal["confidence"] = 0.8
                signal["reason"] = "Market anomaly detected"
            
            # Check technical indicators
            commodity_indicators = indicators.get("indicators", {})
            rsi = commodity_indicators.get("rsi", {})
            if rsi.get("rsi", 50) > 70:
                signal["signal"] = "SELL"
                signal["confidence"] = 0.7
                signal["reason"] = "RSI overbought"
            elif rsi.get("rsi", 50) < 30:
                signal["signal"] = "BUY"
                signal["confidence"] = 0.7
                signal["reason"] = "RSI oversold"
            
            signals.append(signal)
        
        return signals
        
    except Exception as e:
        logger.error("Signal generation failed", error=str(e))
        return []
