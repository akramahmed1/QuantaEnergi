from sqlalchemy.orm import Session
from app.models.trade import Trade

def reconcile_position(db: Session, trade_id: int):
    """Reconcile position for a given trade"""
    trade = db.query(Trade).get(trade_id)
    return {"position": trade.quantity * trade.price if trade else 0}
