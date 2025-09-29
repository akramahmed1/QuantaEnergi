from sklearn.linear_model import LinearRegression
import numpy as np
from app.models.esg import ESG
from app.models.trade import Trade
from sqlalchemy.orm import Session
from .geo_risk_service import fetch_geo_risk, get_geo_risk_recommendations

def calculate_carbon_footprint(trade: Trade):
    model = LinearRegression()
    X = np.array([[trade.quantity]])
    y = np.array([0.5 * trade.quantity])
    model.fit(X, y)
    emissions = model.predict([[trade.quantity]])[0]
    return {'co2': emissions, 'certs': ['EU-ETS'] if 'renew' in trade.asset else []}

def track_esg(trade_id: int, db: Session):
    """Enhanced ESG tracking with geo-risk assessment"""
    trade = db.query(Trade).get(trade_id)
    esg_data = calculate_carbon_footprint(trade)
    
    # Add geo-risk assessment for ESG tracking
    # Determine region based on trade asset
    region = determine_trade_region(trade.asset)
    
    # Get geo-risk assessment
    geo_risk = fetch_geo_risk(region=region, volatility=0.15, sentiment=0.6)
    
    # Adjust CO2 based on geo-risk level
    co2_multiplier = 1.0
    if geo_risk['risk_level'] == 'CRITICAL':
        co2_multiplier = 1.3  # 30% higher CO2 for critical risk regions
    elif geo_risk['risk_level'] == 'HIGH':
        co2_multiplier = 1.2  # 20% higher CO2 for high risk regions
    elif geo_risk['risk_level'] == 'MEDIUM':
        co2_multiplier = 1.1  # 10% higher CO2 for medium risk regions
    
    # Apply geo-risk adjustment
    esg_data['co2'] *= co2_multiplier
    esg_data['geo_risk'] = geo_risk
    esg_data['risk_adjusted'] = True
    
    # Add geo-risk recommendations
    esg_data['recommendations'] = get_geo_risk_recommendations(geo_risk)
    
    # Save to database
    esg = ESG(
        trade_id=trade_id, 
        co2=esg_data['co2'], 
        certs=','.join(esg_data['certs'])
    )
    db.add(esg)
    db.commit()
    
    return esg_data

def determine_trade_region(asset: str) -> str:
    """Determine geographic region based on trade asset"""
    asset_lower = asset.lower()
    
    if any(keyword in asset_lower for keyword in ['guyana', 'south_america', 'latin']):
        return 'GUYANA'
    elif any(keyword in asset_lower for keyword in ['middle_east', 'saudi', 'uae', 'qatar', 'iran']):
        return 'MIDDLE_EAST'
    elif any(keyword in asset_lower for keyword in ['shale', 'texas', 'north_dakota', 'permian']):
        return 'NORTH_AMERICA'
    else:
        return 'NORTH_AMERICA'  # Default to North America
