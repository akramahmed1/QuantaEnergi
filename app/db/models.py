from sqlalchemy import Column, Integer, String, Float, Boolean
from app.db.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=True)

class EmissionFactor(Base):
    __tablename__ = "emission_factors"
    id = Column(Integer, primary_key=True)
    country_code = Column(String)
    factor_kgco2e_per_kwh = Column(Float)
    source = Column(String)
    year = Column(Integer)