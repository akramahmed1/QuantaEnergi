from sklearn.linear_model import LinearRegression
import numpy as np
from app.models.esg import ESG
from app.models.trade import Trade
from sqlalchemy.orm import Session

def calculate_carbon_footprint(trade: Trade):
    model = LinearRegression()
    X = np.array([[trade.quantity]])
    y = np.array([0.5 * trade.quantity])
    model.fit(X, y)
    emissions = model.predict([[trade.quantity]])[0]
    return {'co2': emissions, 'certs': ['EU-ETS'] if 'renew' in trade.asset else []}

def track_esg(trade_id: int, db: Session):
    trade = db.query(Trade).get(trade_id)
    esg_data = calculate_carbon_footprint(trade)
    esg = ESG(trade_id=trade_id, co2=esg_data['co2'], certs=','.join(esg_data['certs']))
    db.add(esg)
    db.commit()
    return esg_data
