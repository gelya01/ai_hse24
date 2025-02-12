from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, func
from db import Base


class TrainingLog(Base):
    __tablename__ = "training_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    duration = Column(Float, nullable=False)  # длительность в минутах
    calories_burned = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
