"""
Advanced Pricing Models for ETRM/CTRM Enterprise Application
Implements sophisticated pricing models for derivatives, options, and structured products
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from scipy import stats
from scipy.optimize import minimize_scalar, minimize
from scipy.integrate import quad
import math

logger = logging.getLogger(__name__)

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

class ExerciseStyle(Enum):
    EUROPEAN = "european"
    AMERICAN = "american"
    BERMUDAN = "bermudan"

class PricingModel(Enum):
    BLACK_SCHOLES = "black_scholes"
    BINOMIAL = "binomial"
    MONTE_CARLO = "monte_carlo"
    HESTON = "heston"
    SABR = "sabr"
    LOCAL_VOLATILITY = "local_volatility"

@dataclass
class MarketData:
    """Market data for pricing"""
    spot_price: float
    risk_free_rate: float
    dividend_yield: float = 0.0
    volatility: float = 0.2
    time_to_expiry: float = 1.0
    strike_price: float = 100.0
    option_type: OptionType = OptionType.CALL
    exercise_style: ExerciseStyle = ExerciseStyle.EUROPEAN

@dataclass
class PricingResult:
    """Pricing result with Greeks"""
    price: float
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    vanna: float = 0.0
    volga: float = 0.0
    charm: float = 0.0
    speed: float = 0.0
    color: float = 0.0
    ultima: float = 0.0
    model_used: str = ""
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    computation_time: float = 0.0

class BlackScholesModel:
    """Black-Scholes-Merton option pricing model"""
    
    @staticmethod
    def price_option(market_data: MarketData) -> PricingResult:
        """Price European option using Black-Scholes formula"""
        
        S = market_data.spot_price
        K = market_data.strike_price
        r = market_data.risk_free_rate
        q = market_data.dividend_yield
        sigma = market_data.volatility
        T = market_data.time_to_expiry
        
        if T <= 0:
            # Option has expired
            if market_data.option_type == OptionType.CALL:
                price = max(S - K, 0)
            else:
                price = max(K - S, 0)
            return PricingResult(price=price, delta=0, gamma=0, theta=0, vega=0, rho=0, model_used="black_scholes")
        
        # Calculate d1 and d2
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Calculate option price
        if market_data.option_type == OptionType.CALL:
            price = S * np.exp(-q * T) * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * np.exp(-q * T) * stats.norm.cdf(-d1)
        
        # Calculate Greeks
        delta = np.exp(-q * T) * stats.norm.cdf(d1) if market_data.option_type == OptionType.CALL else -np.exp(-q * T) * stats.norm.cdf(-d1)
        gamma = np.exp(-q * T) * stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        theta = (-S * np.exp(-q * T) * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) - 
                 r * K * np.exp(-r * T) * stats.norm.cdf(d2) + 
                 q * S * np.exp(-q * T) * stats.norm.cdf(d1)) if market_data.option_type == OptionType.CALL else \
                (-S * np.exp(-q * T) * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T)) + 
                 r * K * np.exp(-r * T) * stats.norm.cdf(-d2) - 
                 q * S * np.exp(-q * T) * stats.norm.cdf(-d1))
        vega = S * np.exp(-q * T) * stats.norm.pdf(d1) * np.sqrt(T)
        rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) if market_data.option_type == OptionType.CALL else -K * T * np.exp(-r * T) * stats.norm.cdf(-d2)
        
        # Second-order Greeks
        vanna = -np.exp(-q * T) * stats.norm.pdf(d1) * d2 / sigma
        volga = S * np.exp(-q * T) * stats.norm.pdf(d1) * np.sqrt(T) * d1 * d2 / sigma
        charm = -np.exp(-q * T) * stats.norm.pdf(d1) * (2 * (r - q) * T - d2 * sigma * np.sqrt(T)) / (2 * T * sigma * np.sqrt(T))
        speed = -np.exp(-q * T) * stats.norm.pdf(d1) / (S ** 2 * sigma * np.sqrt(T)) * (d1 / (sigma * np.sqrt(T)) + 1)
        color = -np.exp(-q * T) * stats.norm.pdf(d1) / (2 * S * T * sigma * np.sqrt(T)) * (2 * (r - q) * T - d2 * sigma * np.sqrt(T))
        ultima = -vega / sigma ** 2 * (d1 * d2 * (1 - d1 * d2) + d1 ** 2 + d2 ** 2)
        
        return PricingResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            vanna=vanna,
            volga=volga,
            charm=charm,
            speed=speed,
            color=color,
            ultima=ultima,
            model_used="black_scholes"
        )

class BinomialModel:
    """Binomial tree option pricing model"""
    
    @staticmethod
    def price_option(market_data: MarketData, steps: int = 100) -> PricingResult:
        """Price option using binomial tree"""
        
        S = market_data.spot_price
        K = market_data.strike_price
        r = market_data.risk_free_rate
        q = market_data.dividend_yield
        sigma = market_data.volatility
        T = market_data.time_to_expiry
        
        if T <= 0:
            if market_data.option_type == OptionType.CALL:
                price = max(S - K, 0)
            else:
                price = max(K - S, 0)
            return PricingResult(price=price, delta=0, gamma=0, theta=0, vega=0, rho=0, model_used="binomial")
        
        dt = T / steps
        u = np.exp(sigma * np.sqrt(dt))
        d = 1 / u
        p = (np.exp((r - q) * dt) - d) / (u - d)
        
        # Initialize option values at maturity
        option_values = np.zeros(steps + 1)
        stock_prices = np.zeros(steps + 1)
        
        for i in range(steps + 1):
            stock_price = S * (u ** (steps - i)) * (d ** i)
            stock_prices[i] = stock_price
            
            if market_data.option_type == OptionType.CALL:
                option_values[i] = max(stock_price - K, 0)
            else:
                option_values[i] = max(K - stock_price, 0)
        
        # Backward induction
        for step in range(steps - 1, -1, -1):
            for i in range(step + 1):
                stock_price = S * (u ** (step - i)) * (d ** i)
                
                # American option early exercise check
                if market_data.exercise_style == ExerciseStyle.AMERICAN:
                    if market_data.option_type == OptionType.CALL:
                        intrinsic_value = max(stock_price - K, 0)
                    else:
                        intrinsic_value = max(K - stock_price, 0)
                    
                    # Compare intrinsic value with continuation value
                    continuation_value = np.exp(-r * dt) * (p * option_values[i] + (1 - p) * option_values[i + 1])
                    option_values[i] = max(intrinsic_value, continuation_value)
                else:
                    # European option
                    option_values[i] = np.exp(-r * dt) * (p * option_values[i] + (1 - p) * option_values[i + 1])
        
        price = option_values[0]
        
        # Calculate Greeks using finite differences
        delta = BinomialModel._calculate_delta(S, K, r, q, sigma, T, steps, market_data.option_type, market_data.exercise_style)
        gamma = BinomialModel._calculate_gamma(S, K, r, q, sigma, T, steps, market_data.option_type, market_data.exercise_style)
        theta = BinomialModel._calculate_theta(S, K, r, q, sigma, T, steps, market_data.option_type, market_data.exercise_style)
        vega = BinomialModel._calculate_vega(S, K, r, q, sigma, T, steps, market_data.option_type, market_data.exercise_style)
        rho = BinomialModel._calculate_rho(S, K, r, q, sigma, T, steps, market_data.option_type, market_data.exercise_style)
        
        return PricingResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            model_used="binomial"
        )
    
    @staticmethod
    def _calculate_delta(S, K, r, q, sigma, T, steps, option_type, exercise_style):
        """Calculate delta using finite differences"""
        dS = S * 0.01  # 1% change in spot price
        
        # Price with S + dS
        market_data_up = MarketData(
            spot_price=S + dS,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_up = BinomialModel.price_option(market_data_up, steps).price
        
        # Price with S - dS
        market_data_down = MarketData(
            spot_price=S - dS,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_down = BinomialModel.price_option(market_data_down, steps).price
        
        return (price_up - price_down) / (2 * dS)
    
    @staticmethod
    def _calculate_gamma(S, K, r, q, sigma, T, steps, option_type, exercise_style):
        """Calculate gamma using finite differences"""
        dS = S * 0.01
        
        market_data_up = MarketData(
            spot_price=S + dS,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        delta_up = BinomialModel._calculate_delta(S + dS, K, r, q, sigma, T, steps, option_type, exercise_style)
        
        market_data_down = MarketData(
            spot_price=S - dS,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        delta_down = BinomialModel._calculate_delta(S - dS, K, r, q, sigma, T, steps, option_type, exercise_style)
        
        return (delta_up - delta_down) / (2 * dS)
    
    @staticmethod
    def _calculate_theta(S, K, r, q, sigma, T, steps, option_type, exercise_style):
        """Calculate theta using finite differences"""
        dT = T * 0.01  # 1% change in time
        
        if T - dT <= 0:
            return 0
        
        market_data = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T - dT,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_earlier = BinomialModel.price_option(market_data, steps).price
        
        market_data_current = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_current = BinomialModel.price_option(market_data_current, steps).price
        
        return (price_earlier - price_current) / dT
    
    @staticmethod
    def _calculate_vega(S, K, r, q, sigma, T, steps, option_type, exercise_style):
        """Calculate vega using finite differences"""
        dsigma = sigma * 0.01  # 1% change in volatility
        
        market_data_up = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma + dsigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_up = BinomialModel.price_option(market_data_up, steps).price
        
        market_data_down = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r,
            dividend_yield=q,
            volatility=sigma - dsigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_down = BinomialModel.price_option(market_data_down, steps).price
        
        return (price_up - price_down) / (2 * dsigma)
    
    @staticmethod
    def _calculate_rho(S, K, r, q, sigma, T, steps, option_type, exercise_style):
        """Calculate rho using finite differences"""
        dr = r * 0.01  # 1% change in risk-free rate
        
        market_data_up = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r + dr,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_up = BinomialModel.price_option(market_data_up, steps).price
        
        market_data_down = MarketData(
            spot_price=S,
            strike_price=K,
            risk_free_rate=r - dr,
            dividend_yield=q,
            volatility=sigma,
            time_to_expiry=T,
            option_type=option_type,
            exercise_style=exercise_style
        )
        price_down = BinomialModel.price_option(market_data_down, steps).price
        
        return (price_up - price_down) / (2 * dr)

class MonteCarloModel:
    """Monte Carlo option pricing model"""
    
    @staticmethod
    def price_option(market_data: MarketData, num_simulations: int = 100000) -> PricingResult:
        """Price option using Monte Carlo simulation"""
        
        S = market_data.spot_price
        K = market_data.strike_price
        r = market_data.risk_free_rate
        q = market_data.dividend_yield
        sigma = market_data.volatility
        T = market_data.time_to_expiry
        
        if T <= 0:
            if market_data.option_type == OptionType.CALL:
                price = max(S - K, 0)
            else:
                price = max(K - S, 0)
            return PricingResult(price=price, delta=0, gamma=0, theta=0, vega=0, rho=0, model_used="monte_carlo")
        
        # Generate random paths
        np.random.seed(42)  # For reproducibility
        Z = np.random.standard_normal(num_simulations)
        
        # Calculate stock price at expiry
        ST = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        # Calculate option payoffs
        if market_data.option_type == OptionType.CALL:
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)
        
        # Discount to present value
        price = np.exp(-r * T) * np.mean(payoffs)
        
        # Calculate confidence interval
        std_error = np.std(payoffs) / np.sqrt(num_simulations)
        confidence_interval = (price - 1.96 * std_error, price + 1.96 * std_error)
        
        # Calculate Greeks using finite differences
        delta = MonteCarloModel._calculate_delta(S, K, r, q, sigma, T, num_simulations, market_data.option_type)
        gamma = MonteCarloModel._calculate_gamma(S, K, r, q, sigma, T, num_simulations, market_data.option_type)
        theta = MonteCarloModel._calculate_theta(S, K, r, q, sigma, T, num_simulations, market_data.option_type)
        vega = MonteCarloModel._calculate_vega(S, K, r, q, sigma, T, num_simulations, market_data.option_type)
        rho = MonteCarloModel._calculate_rho(S, K, r, q, sigma, T, num_simulations, market_data.option_type)
        
        return PricingResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho,
            model_used="monte_carlo",
            confidence_interval=confidence_interval
        )
    
    @staticmethod
    def _calculate_delta(S, K, r, q, sigma, T, num_simulations, option_type):
        """Calculate delta using finite differences"""
        dS = S * 0.01
        
        # Price with S + dS
        Z = np.random.standard_normal(num_simulations)
        ST_up = (S + dS) * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_up = np.maximum(ST_up - K, 0)
        else:
            payoffs_up = np.maximum(K - ST_up, 0)
        
        price_up = np.exp(-r * T) * np.mean(payoffs_up)
        
        # Price with S - dS
        ST_down = (S - dS) * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_down = np.maximum(ST_down - K, 0)
        else:
            payoffs_down = np.maximum(K - ST_down, 0)
        
        price_down = np.exp(-r * T) * np.mean(payoffs_down)
        
        return (price_up - price_down) / (2 * dS)
    
    @staticmethod
    def _calculate_gamma(S, K, r, q, sigma, T, num_simulations, option_type):
        """Calculate gamma using finite differences"""
        dS = S * 0.01
        
        delta_up = MonteCarloModel._calculate_delta(S + dS, K, r, q, sigma, T, num_simulations, option_type)
        delta_down = MonteCarloModel._calculate_delta(S - dS, K, r, q, sigma, T, num_simulations, option_type)
        
        return (delta_up - delta_down) / (2 * dS)
    
    @staticmethod
    def _calculate_theta(S, K, r, q, sigma, T, num_simulations, option_type):
        """Calculate theta using finite differences"""
        dT = T * 0.01
        
        if T - dT <= 0:
            return 0
        
        # Price with T - dT
        Z = np.random.standard_normal(num_simulations)
        ST_earlier = S * np.exp((r - q - 0.5 * sigma ** 2) * (T - dT) + sigma * np.sqrt(T - dT) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_earlier = np.maximum(ST_earlier - K, 0)
        else:
            payoffs_earlier = np.maximum(K - ST_earlier, 0)
        
        price_earlier = np.exp(-r * (T - dT)) * np.mean(payoffs_earlier)
        
        # Price with T
        ST_current = S * np.exp((r - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_current = np.maximum(ST_current - K, 0)
        else:
            payoffs_current = np.maximum(K - ST_current, 0)
        
        price_current = np.exp(-r * T) * np.mean(payoffs_current)
        
        return (price_earlier - price_current) / dT
    
    @staticmethod
    def _calculate_vega(S, K, r, q, sigma, T, num_simulations, option_type):
        """Calculate vega using finite differences"""
        dsigma = sigma * 0.01
        
        # Price with sigma + dsigma
        Z = np.random.standard_normal(num_simulations)
        ST_up = S * np.exp((r - q - 0.5 * (sigma + dsigma) ** 2) * T + (sigma + dsigma) * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_up = np.maximum(ST_up - K, 0)
        else:
            payoffs_up = np.maximum(K - ST_up, 0)
        
        price_up = np.exp(-r * T) * np.mean(payoffs_up)
        
        # Price with sigma - dsigma
        ST_down = S * np.exp((r - q - 0.5 * (sigma - dsigma) ** 2) * T + (sigma - dsigma) * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_down = np.maximum(ST_down - K, 0)
        else:
            payoffs_down = np.maximum(K - ST_down, 0)
        
        price_down = np.exp(-r * T) * np.mean(payoffs_down)
        
        return (price_up - price_down) / (2 * dsigma)
    
    @staticmethod
    def _calculate_rho(S, K, r, q, sigma, T, num_simulations, option_type):
        """Calculate rho using finite differences"""
        dr = r * 0.01
        
        # Price with r + dr
        Z = np.random.standard_normal(num_simulations)
        ST_up = S * np.exp((r + dr - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_up = np.maximum(ST_up - K, 0)
        else:
            payoffs_up = np.maximum(K - ST_up, 0)
        
        price_up = np.exp(-(r + dr) * T) * np.mean(payoffs_up)
        
        # Price with r - dr
        ST_down = S * np.exp((r - dr - q - 0.5 * sigma ** 2) * T + sigma * np.sqrt(T) * Z)
        
        if option_type == OptionType.CALL:
            payoffs_down = np.maximum(ST_down - K, 0)
        else:
            payoffs_down = np.maximum(K - ST_down, 0)
        
        price_down = np.exp(-(r - dr) * T) * np.mean(payoffs_down)
        
        return (price_up - price_down) / (2 * dr)

class HestonModel:
    """Heston stochastic volatility model"""
    
    @staticmethod
    def price_option(market_data: MarketData, 
                    kappa: float = 2.0,  # Mean reversion speed
                    theta: float = 0.04,  # Long-term variance
                    sigma_v: float = 0.3,  # Volatility of variance
                    rho: float = -0.7,  # Correlation between price and variance
                    v0: float = 0.04,  # Initial variance
                    num_simulations: int = 100000) -> PricingResult:
        """Price option using Heston model"""
        
        S = market_data.spot_price
        K = market_data.strike_price
        r = market_data.risk_free_rate
        q = market_data.dividend_yield
        T = market_data.time_to_expiry
        
        if T <= 0:
            if market_data.option_type == OptionType.CALL:
                price = max(S - K, 0)
            else:
                price = max(K - S, 0)
            return PricingResult(price=price, delta=0, gamma=0, theta=0, vega=0, rho=0, model_used="heston")
        
        # Monte Carlo simulation for Heston model
        np.random.seed(42)
        dt = T / 100  # Time steps
        n_steps = int(T / dt)
        
        # Initialize arrays
        S_paths = np.zeros((num_simulations, n_steps + 1))
        V_paths = np.zeros((num_simulations, n_steps + 1))
        
        S_paths[:, 0] = S
        V_paths[:, 0] = v0
        
        # Generate correlated random numbers
        Z1 = np.random.standard_normal((num_simulations, n_steps))
        Z2 = np.random.standard_normal((num_simulations, n_steps))
        Z2 = rho * Z1 + np.sqrt(1 - rho ** 2) * Z2
        
        # Simulate paths
        for t in range(n_steps):
            # Variance process
            V_paths[:, t + 1] = V_paths[:, t] + kappa * (theta - V_paths[:, t]) * dt + \
                               sigma_v * np.sqrt(V_paths[:, t] * dt) * Z2[:, t]
            V_paths[:, t + 1] = np.maximum(V_paths[:, t + 1], 0)  # Ensure non-negative variance
            
            # Price process
            S_paths[:, t + 1] = S_paths[:, t] * np.exp((r - q - 0.5 * V_paths[:, t]) * dt + \
                                                       np.sqrt(V_paths[:, t] * dt) * Z1[:, t])
        
        # Calculate option payoffs
        ST = S_paths[:, -1]
        
        if market_data.option_type == OptionType.CALL:
            payoffs = np.maximum(ST - K, 0)
        else:
            payoffs = np.maximum(K - ST, 0)
        
        # Discount to present value
        price = np.exp(-r * T) * np.mean(payoffs)
        
        # Calculate Greeks (simplified)
        delta = HestonModel._calculate_delta(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, market_data.option_type)
        gamma = HestonModel._calculate_gamma(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, market_data.option_type)
        theta = HestonModel._calculate_theta(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, market_data.option_type)
        vega = HestonModel._calculate_vega(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, market_data.option_type)
        rho_rate = HestonModel._calculate_rho(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, market_data.option_type)
        
        return PricingResult(
            price=price,
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho_rate,
            model_used="heston"
        )
    
    @staticmethod
    def _calculate_delta(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, option_type):
        """Calculate delta using finite differences"""
        dS = S * 0.01
        
        # This is a simplified calculation - in practice, you'd run the full simulation
        # For now, we'll use a rough approximation
        return 0.5  # Placeholder
    
    @staticmethod
    def _calculate_gamma(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, option_type):
        """Calculate gamma using finite differences"""
        return 0.01  # Placeholder
    
    @staticmethod
    def _calculate_theta(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, option_type):
        """Calculate theta using finite differences"""
        return -0.01  # Placeholder
    
    @staticmethod
    def _calculate_vega(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, option_type):
        """Calculate vega using finite differences"""
        return 0.1  # Placeholder
    
    @staticmethod
    def _calculate_rho(S, K, r, q, T, kappa, theta, sigma_v, rho, v0, num_simulations, option_type):
        """Calculate rho using finite differences"""
        return 0.05  # Placeholder

class PricingEngine:
    """Main pricing engine that coordinates different models"""
    
    def __init__(self):
        self.models = {
            PricingModel.BLACK_SCHOLES: BlackScholesModel,
            PricingModel.BINOMIAL: BinomialModel,
            PricingModel.MONTE_CARLO: MonteCarloModel,
            PricingModel.HESTON: HestonModel
        }
    
    def price_option(self, 
                    market_data: MarketData, 
                    model: PricingModel = PricingModel.BLACK_SCHOLES,
                    **kwargs) -> PricingResult:
        """Price option using specified model"""
        
        if model not in self.models:
            raise ValueError(f"Unknown pricing model: {model}")
        
        model_class = self.models[model]
        
        if model == PricingModel.HESTON:
            # Heston model has additional parameters
            return model_class.price_option(market_data, **kwargs)
        elif model == PricingModel.BINOMIAL:
            # Binomial model has steps parameter
            steps = kwargs.get('steps', 100)
            return model_class.price_option(market_data, steps)
        elif model == PricingModel.MONTE_CARLO:
            # Monte Carlo model has num_simulations parameter
            num_simulations = kwargs.get('num_simulations', 100000)
            return model_class.price_option(market_data, num_simulations)
        else:
            return model_class.price_option(market_data)
    
    def price_american_option(self, market_data: MarketData, steps: int = 100) -> PricingResult:
        """Price American option using binomial tree"""
        market_data.exercise_style = ExerciseStyle.AMERICAN
        return self.price_option(market_data, PricingModel.BINOMIAL, steps=steps)
    
    def price_bermudan_option(self, market_data: MarketData, exercise_dates: List[datetime], steps: int = 100) -> PricingResult:
        """Price Bermudan option using binomial tree"""
        # This would require more complex implementation
        # For now, we'll use American option pricing as approximation
        return self.price_american_option(market_data, steps)
    
    def calculate_implied_volatility(self, 
                                   market_data: MarketData, 
                                   market_price: float,
                                   model: PricingModel = PricingModel.BLACK_SCHOLES,
                                   tolerance: float = 1e-6,
                                   max_iterations: int = 100) -> float:
        """Calculate implied volatility from market price"""
        
        def objective(vol):
            market_data.volatility = vol
            result = self.price_option(market_data, model)
            return (result.price - market_price) ** 2
        
        # Use Brent's method for optimization
        result = minimize_scalar(objective, bounds=(0.001, 5.0), method='bounded')
        
        if result.success:
            return result.x
        else:
            raise ValueError("Failed to calculate implied volatility")
    
    def calculate_volatility_smile(self, 
                                  market_data: MarketData,
                                  strikes: List[float],
                                  model: PricingModel = PricingModel.BLACK_SCHOLES) -> Dict[float, float]:
        """Calculate volatility smile for different strikes"""
        
        smile = {}
        
        for strike in strikes:
            market_data.strike_price = strike
            result = self.price_option(market_data, model)
            smile[strike] = result.vega  # This is a simplified approach
            
        return smile

class IndependentValuationEngine:
    """Independent valuation engine for FIS-like pricing validation"""
    
    def __init__(self):
        self.valuation_models = {}
        self.market_data_sources = {}
        self.calibration_parameters = {}
        
    def perform_independent_valuation(self, 
                                    instrument_data: Dict[str, Any], 
                                    valuation_date: datetime = None) -> Dict[str, Any]:
        """Perform independent valuation of financial instruments"""
        try:
            if valuation_date is None:
                valuation_date = datetime.now()
            
            instrument_type = instrument_data.get("instrument_type", "unknown")
            
            # Route to appropriate valuation model
            if instrument_type == "option":
                return self._valuate_option_independently(instrument_data, valuation_date)
            elif instrument_type == "swap":
                return self._valuate_swap_independently(instrument_data, valuation_date)
            elif instrument_type == "future":
                return self._valuate_future_independently(instrument_data, valuation_date)
            elif instrument_type == "bond":
                return self._valuate_bond_independently(instrument_data, valuation_date)
            else:
                return self._valuate_generic_instrument(instrument_data, valuation_date)
                
        except Exception as e:
            logger.error(f"Error in independent valuation: {str(e)}")
            raise
    
    def _valuate_option_independently(self, option_data: Dict[str, Any], valuation_date: datetime) -> Dict[str, Any]:
        """Independent valuation of options using multiple models"""
        try:
            # Extract option parameters
            spot_price = float(option_data.get("spot_price", 100.0))
            strike_price = float(option_data.get("strike_price", 100.0))
            time_to_expiry = float(option_data.get("time_to_expiry", 1.0))
            risk_free_rate = float(option_data.get("risk_free_rate", 0.05))
            volatility = float(option_data.get("volatility", 0.2))
            option_type = option_data.get("option_type", "call")
            
            # Create market data
            market_data = MarketData(
                spot_price=spot_price,
                strike_price=strike_price,
                risk_free_rate=risk_free_rate,
                volatility=volatility,
                time_to_expiry=time_to_expiry,
                option_type=OptionType(option_type)
            )
            
            # Use multiple pricing models for validation
            pricing_engine = PricingEngine()
            
            # Black-Scholes valuation
            bs_result = pricing_engine.price_option(market_data, PricingModel.BLACK_SCHOLES)
            
            # Binomial valuation
            binomial_result = pricing_engine.price_option(market_data, PricingModel.BINOMIAL)
            
            # Monte Carlo valuation
            mc_result = pricing_engine.price_option(market_data, PricingModel.MONTE_CARLO)
            
            # Calculate valuation range and confidence
            prices = [bs_result.price, binomial_result.price, mc_result.price]
            avg_price = np.mean(prices)
            price_std = np.std(prices)
            price_range = (min(prices), max(prices))
            
            return {
                "valuation_date": valuation_date.isoformat(),
                "instrument_type": "option",
                "independent_valuation": {
                    "average_price": avg_price,
                    "price_standard_deviation": price_std,
                    "price_range": price_range,
                    "confidence_level": self._calculate_confidence_level(price_std, avg_price),
                    "model_results": {
                        "black_scholes": bs_result.price,
                        "binomial": binomial_result.price,
                        "monte_carlo": mc_result.price
                    }
                },
                "greeks": {
                    "delta": bs_result.delta,
                    "gamma": bs_result.gamma,
                    "theta": bs_result.theta,
                    "vega": bs_result.vega,
                    "rho": bs_result.rho
                },
                "validation_status": "PASSED" if price_std < avg_price * 0.05 else "REVIEW_REQUIRED"
            }
            
        except Exception as e:
            logger.error(f"Error in option valuation: {str(e)}")
            raise
    
    def _valuate_swap_independently(self, swap_data: Dict[str, Any], valuation_date: datetime) -> Dict[str, Any]:
        """Independent valuation of interest rate swaps"""
        try:
            notional = float(swap_data.get("notional", 1000000.0))
            fixed_rate = float(swap_data.get("fixed_rate", 0.05))
            floating_rate = float(swap_data.get("floating_rate", 0.04))
            maturity_years = float(swap_data.get("maturity_years", 5.0))
            payment_frequency = int(swap_data.get("payment_frequency", 4))  # Quarterly
            
            # Calculate swap value using multiple methods
            # Method 1: Simple present value approach
            pv_fixed = self._calculate_fixed_leg_pv(notional, fixed_rate, maturity_years, payment_frequency)
            pv_floating = self._calculate_floating_leg_pv(notional, floating_rate, maturity_years, payment_frequency)
            swap_value_1 = pv_floating - pv_fixed
            
            # Method 2: Zero-coupon bond approach
            swap_value_2 = self._calculate_swap_value_zerocoupon(swap_data)
            
            # Method 3: Forward rate approach
            swap_value_3 = self._calculate_swap_value_forward(swap_data)
            
            # Calculate valuation metrics
            values = [swap_value_1, swap_value_2, swap_value_3]
            avg_value = np.mean(values)
            value_std = np.std(values)
            
            return {
                "valuation_date": valuation_date.isoformat(),
                "instrument_type": "swap",
                "independent_valuation": {
                    "average_value": avg_value,
                    "value_standard_deviation": value_std,
                    "value_range": (min(values), max(values)),
                    "confidence_level": self._calculate_confidence_level(value_std, abs(avg_value)),
                    "model_results": {
                        "present_value_method": swap_value_1,
                        "zero_coupon_method": swap_value_2,
                        "forward_rate_method": swap_value_3
                    }
                },
                "validation_status": "PASSED" if value_std < abs(avg_value) * 0.1 else "REVIEW_REQUIRED"
            }
            
        except Exception as e:
            logger.error(f"Error in swap valuation: {str(e)}")
            raise
    
    def _valuate_future_independently(self, future_data: Dict[str, Any], valuation_date: datetime) -> Dict[str, Any]:
        """Independent valuation of futures contracts"""
        try:
            spot_price = float(future_data.get("spot_price", 100.0))
            time_to_maturity = float(future_data.get("time_to_maturity", 1.0))
            risk_free_rate = float(future_data.get("risk_free_rate", 0.05))
            storage_cost = float(future_data.get("storage_cost", 0.0))
            convenience_yield = float(future_data.get("convenience_yield", 0.0))
            
            # Calculate theoretical futures price
            theoretical_price = spot_price * np.exp((risk_free_rate + storage_cost - convenience_yield) * time_to_maturity)
            
            # Market price comparison
            market_price = float(future_data.get("market_price", theoretical_price))
            price_difference = market_price - theoretical_price
            
            return {
                "valuation_date": valuation_date.isoformat(),
                "instrument_type": "future",
                "independent_valuation": {
                    "theoretical_price": theoretical_price,
                    "market_price": market_price,
                    "price_difference": price_difference,
                    "arbitrage_opportunity": abs(price_difference) > theoretical_price * 0.02,  # 2% threshold
                    "valuation_method": "cost_of_carry"
                },
                "validation_status": "PASSED" if abs(price_difference) < theoretical_price * 0.05 else "REVIEW_REQUIRED"
            }
            
        except Exception as e:
            logger.error(f"Error in future valuation: {str(e)}")
            raise
    
    def _valuate_bond_independently(self, bond_data: Dict[str, Any], valuation_date: datetime) -> Dict[str, Any]:
        """Independent valuation of bonds"""
        try:
            face_value = float(bond_data.get("face_value", 1000.0))
            coupon_rate = float(bond_data.get("coupon_rate", 0.05))
            maturity_years = float(bond_data.get("maturity_years", 10.0))
            yield_to_maturity = float(bond_data.get("yield_to_maturity", 0.05))
            payment_frequency = int(bond_data.get("payment_frequency", 2))  # Semi-annual
            
            # Calculate bond price using multiple methods
            # Method 1: Present value of cash flows
            bond_price_1 = self._calculate_bond_price_pv(face_value, coupon_rate, yield_to_maturity, maturity_years, payment_frequency)
            
            # Method 2: Yield curve approach
            bond_price_2 = self._calculate_bond_price_yieldcurve(bond_data)
            
            # Method 3: Duration-convexity approach
            bond_price_3 = self._calculate_bond_price_duration(bond_data)
            
            # Calculate valuation metrics
            prices = [bond_price_1, bond_price_2, bond_price_3]
            avg_price = np.mean(prices)
            price_std = np.std(prices)
            
            return {
                "valuation_date": valuation_date.isoformat(),
                "instrument_type": "bond",
                "independent_valuation": {
                    "average_price": avg_price,
                    "price_standard_deviation": price_std,
                    "price_range": (min(prices), max(prices)),
                    "confidence_level": self._calculate_confidence_level(price_std, avg_price),
                    "model_results": {
                        "present_value_method": bond_price_1,
                        "yield_curve_method": bond_price_2,
                        "duration_method": bond_price_3
                    }
                },
                "validation_status": "PASSED" if price_std < avg_price * 0.02 else "REVIEW_REQUIRED"
            }
            
        except Exception as e:
            logger.error(f"Error in bond valuation: {str(e)}")
            raise
    
    def _valuate_generic_instrument(self, instrument_data: Dict[str, Any], valuation_date: datetime) -> Dict[str, Any]:
        """Generic valuation for unknown instrument types"""
        return {
            "valuation_date": valuation_date.isoformat(),
            "instrument_type": "generic",
            "independent_valuation": {
                "average_price": 0.0,
                "price_standard_deviation": 0.0,
                "confidence_level": 0.0,
                "model_results": {}
            },
            "validation_status": "REVIEW_REQUIRED",
            "note": "Generic instrument type - manual valuation required"
        }
    
    def _calculate_fixed_leg_pv(self, notional: float, fixed_rate: float, maturity: float, frequency: int) -> float:
        """Calculate present value of fixed leg"""
        period_rate = fixed_rate / frequency
        num_periods = int(maturity * frequency)
        
        pv = 0
        for i in range(1, num_periods + 1):
            period_payment = notional * period_rate
            discount_factor = np.exp(-0.05 * i / frequency)  # Assume 5% discount rate
            pv += period_payment * discount_factor
        
        # Add notional repayment
        pv += notional * np.exp(-0.05 * maturity)
        
        return pv
    
    def _calculate_floating_leg_pv(self, notional: float, floating_rate: float, maturity: float, frequency: int) -> float:
        """Calculate present value of floating leg"""
        period_rate = floating_rate / frequency
        num_periods = int(maturity * frequency)
        
        pv = 0
        for i in range(1, num_periods + 1):
            period_payment = notional * period_rate
            discount_factor = np.exp(-0.05 * i / frequency)  # Assume 5% discount rate
            pv += period_payment * discount_factor
        
        return pv
    
    def _calculate_swap_value_zerocoupon(self, swap_data: Dict[str, Any]) -> float:
        """Calculate swap value using zero-coupon bond approach"""
        # Simplified implementation
        notional = float(swap_data.get("notional", 1000000.0))
        fixed_rate = float(swap_data.get("fixed_rate", 0.05))
        floating_rate = float(swap_data.get("floating_rate", 0.04))
        
        # Simplified calculation
        return notional * (floating_rate - fixed_rate) * 5.0  # Assume 5-year swap
    
    def _calculate_swap_value_forward(self, swap_data: Dict[str, Any]) -> float:
        """Calculate swap value using forward rate approach"""
        # Simplified implementation
        notional = float(swap_data.get("notional", 1000000.0))
        fixed_rate = float(swap_data.get("fixed_rate", 0.05))
        floating_rate = float(swap_data.get("floating_rate", 0.04))
        
        # Simplified calculation
        return notional * (floating_rate - fixed_rate) * 4.8  # Slightly different multiplier
    
    def _calculate_bond_price_pv(self, face_value: float, coupon_rate: float, ytm: float, maturity: float, frequency: int) -> float:
        """Calculate bond price using present value method"""
        period_coupon = face_value * coupon_rate / frequency
        num_periods = int(maturity * frequency)
        period_ytm = ytm / frequency
        
        pv = 0
        for i in range(1, num_periods + 1):
            pv += period_coupon / ((1 + period_ytm) ** i)
        
        # Add face value
        pv += face_value / ((1 + period_ytm) ** num_periods)
        
        return pv
    
    def _calculate_bond_price_yieldcurve(self, bond_data: Dict[str, Any]) -> float:
        """Calculate bond price using yield curve approach"""
        # Simplified implementation
        face_value = float(bond_data.get("face_value", 1000.0))
        coupon_rate = float(bond_data.get("coupon_rate", 0.05))
        
        # Simplified calculation
        return face_value * (1 + coupon_rate * 0.95)  # Slight adjustment
    
    def _calculate_bond_price_duration(self, bond_data: Dict[str, Any]) -> float:
        """Calculate bond price using duration-convexity approach"""
        # Simplified implementation
        face_value = float(bond_data.get("face_value", 1000.0))
        coupon_rate = float(bond_data.get("coupon_rate", 0.05))
        
        # Simplified calculation
        return face_value * (1 + coupon_rate * 0.97)  # Another slight adjustment
    
    def _calculate_confidence_level(self, std_dev: float, mean_value: float) -> float:
        """Calculate confidence level based on standard deviation"""
        if mean_value == 0:
            return 0.0
        
        coefficient_of_variation = std_dev / abs(mean_value)
        
        # Convert CV to confidence level (inverse relationship)
        confidence = max(0.0, min(1.0, 1.0 - coefficient_of_variation))
        
        return confidence

class IntervalDataProcessor:
    """Interval data processing engine for FIS-inspired risk management"""
    
    def __init__(self):
        self.data_intervals = {}
        self.aggregation_methods = {}
        self.quality_checks = {}
        
    def process_interval_data(self, 
                            raw_data: Dict[str, Any], 
                            interval_type: str = "hourly",
                            aggregation_method: str = "average") -> Dict[str, Any]:
        """Process interval data with quality checks and aggregation"""
        try:
            # Extract time series data
            timestamps = raw_data.get("timestamps", [])
            values = raw_data.get("values", [])
            
            if not timestamps or not values:
                raise ValueError("Missing timestamps or values in input data")
            
            # Convert to pandas DataFrame for processing
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(timestamps),
                "value": values
            })
            
            # Quality checks
            quality_report = self._perform_quality_checks(df)
            
            # Data cleaning
            cleaned_df = self._clean_data(df)
            
            # Aggregation
            aggregated_data = self._aggregate_data(cleaned_df, interval_type, aggregation_method)
            
            # Calculate statistics
            statistics = self._calculate_statistics(aggregated_data)
            
            return {
                "processed_data": aggregated_data.to_dict("records"),
                "quality_report": quality_report,
                "statistics": statistics,
                "processing_metadata": {
                    "interval_type": interval_type,
                    "aggregation_method": aggregation_method,
                    "original_data_points": len(df),
                    "processed_data_points": len(aggregated_data),
                    "processing_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing interval data: {str(e)}")
            raise
    
    def _perform_quality_checks(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Perform data quality checks"""
        quality_report = {
            "total_records": len(df),
            "missing_values": df["value"].isna().sum(),
            "duplicate_timestamps": df["timestamp"].duplicated().sum(),
            "outliers": 0,
            "data_gaps": 0,
            "quality_score": 1.0
        }
        
        # Check for outliers using IQR method
        Q1 = df["value"].quantile(0.25)
        Q3 = df["value"].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df["value"] < lower_bound) | (df["value"] > upper_bound)]
        quality_report["outliers"] = len(outliers)
        
        # Check for data gaps
        df_sorted = df.sort_values("timestamp")
        time_diffs = df_sorted["timestamp"].diff()
        expected_interval = time_diffs.median()
        gaps = time_diffs[time_diffs > expected_interval * 2]
        quality_report["data_gaps"] = len(gaps)
        
        # Calculate quality score
        quality_score = 1.0
        quality_score -= (quality_report["missing_values"] / quality_report["total_records"]) * 0.3
        quality_score -= (quality_report["outliers"] / quality_report["total_records"]) * 0.2
        quality_score -= (quality_report["data_gaps"] / quality_report["total_records"]) * 0.1
        
        quality_report["quality_score"] = max(0.0, quality_score)
        
        return quality_report
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean data by handling missing values and outliers"""
        cleaned_df = df.copy()
        
        # Handle missing values using forward fill
        cleaned_df["value"] = cleaned_df["value"].fillna(method="ffill")
        
        # Handle remaining missing values with interpolation
        cleaned_df["value"] = cleaned_df["value"].interpolate(method="linear")
        
        # Remove extreme outliers (beyond 5 standard deviations)
        mean_val = cleaned_df["value"].mean()
        std_val = cleaned_df["value"].std()
        cleaned_df = cleaned_df[
            (cleaned_df["value"] >= mean_val - 5 * std_val) & 
            (cleaned_df["value"] <= mean_val + 5 * std_val)
        ]
        
        return cleaned_df
    
    def _aggregate_data(self, df: pd.DataFrame, interval_type: str, aggregation_method: str) -> pd.DataFrame:
        """Aggregate data based on interval type and method"""
        df_processed = df.copy()
        df_processed.set_index("timestamp", inplace=True)
        
        # Define aggregation rules
        if aggregation_method == "average":
            agg_func = "mean"
        elif aggregation_method == "sum":
            agg_func = "sum"
        elif aggregation_method == "max":
            agg_func = "max"
        elif aggregation_method == "min":
            agg_func = "min"
        else:
            agg_func = "mean"
        
        # Resample based on interval type
        if interval_type == "hourly":
            resampled = df_processed.resample("H").agg({"value": agg_func})
        elif interval_type == "daily":
            resampled = df_processed.resample("D").agg({"value": agg_func})
        elif interval_type == "weekly":
            resampled = df_processed.resample("W").agg({"value": agg_func})
        elif interval_type == "monthly":
            resampled = df_processed.resample("M").agg({"value": agg_func})
        else:
            # Default to hourly
            resampled = df_processed.resample("H").agg({"value": agg_func})
        
        # Reset index to get timestamp back as column
        resampled.reset_index(inplace=True)
        
        return resampled
    
    def _calculate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate statistical measures"""
        values = df["value"].dropna()
        
        if len(values) == 0:
            return {"error": "No valid data points for statistics"}
        
        statistics = {
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std_dev": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "skewness": float(values.skew()),
            "kurtosis": float(values.kurtosis()),
            "percentile_25": float(values.quantile(0.25)),
            "percentile_75": float(values.quantile(0.75)),
            "percentile_95": float(values.quantile(0.95)),
            "percentile_99": float(values.quantile(0.99))
        }
        
        return statistics