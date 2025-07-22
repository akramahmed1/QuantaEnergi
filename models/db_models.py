from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.schema import PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    disabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class IoTData(Base):
    __tablename__ = "iot_data"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    measurement_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    location = Column(String, nullable=True)
    raw_payload = Column(JSONB, nullable=True)
    anomaly_score = Column(Float, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_iot_data'),
        Index('idx_iot_timestamp', 'timestamp'),
    )

class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(Integer, primary_key=True, index=True)
    country_code = Column(String, index=True, nullable=False)
    factor_kgco2e_per_kwh = Column(Float, nullable=False)
    source = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    last_updated = Column(DateTime(timezone=True), default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class CarbonCredit(Base):
    __tablename__ = "carbon_credits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    issued_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    user = relationship("User")

class ForecastDataPointDB(Base):
    __tablename__ = "forecast_data_points"

    id = Column(Integer, primary_key=True, index=True)
    forecast_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    model_used = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    __table_args__ = (
        PrimaryKeyConstraint('id', name='pk_forecast_data_points'),
        Index('idx_forecast_id_timestamp', 'forecast_id', 'timestamp'),
    )