from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from db import Base


class WaterLog(Base):
    __tablename__ = "water_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # выпитая воды в мл
    timestamp = Column(DateTime, default=func.now(), nullable=False)
