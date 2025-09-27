from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ESG(Base):
    __tablename__ = "esg"
    id = Column(Integer, primary_key=True)
    trade_id = Column(Integer)
    co2 = Column(Float)
    certs = Column(String)
