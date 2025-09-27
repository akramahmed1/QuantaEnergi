from sqlalchemy import Column, Integer, Float, String, ForeignKey
from .base import Base

class ESG(Base):
    __tablename__ = "esg"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"))
    co2 = Column(Float)
    certs = Column(String)  # e.g., "EU-ETS,UK-ETS"