from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from db import Base


class FoodLog(Base):
    __tablename__ = "food_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    calories = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
