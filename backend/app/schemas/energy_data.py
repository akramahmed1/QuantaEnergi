from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class EnergyData(Base):
    __tablename__ = "energy_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    commodity_type = Column(String, nullable=False)  # crude_oil, natural_gas, coal, etc.
    price = Column(Float, nullable=False)
    volume = Column(Float, nullable=True)
    region = Column(String, nullable=False)
    source = Column(String, nullable=False)  # cme, ice, simulated
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    # Relationships
    user = relationship("User", back_populates="energy_data")
    
    def __repr__(self):
        return f"<EnergyData(id={self.id}, commodity='{self.commodity_type}', price={self.price}, user_id={self.user_id})>"
