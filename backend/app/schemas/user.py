from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # user, admin, trader, analyst
    subscription_plan = Column(String, default="basic")  # basic, pro, enterprise
    api_calls_this_month = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    energy_data = relationship("EnergyData", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', company='{self.company_name}')>"
