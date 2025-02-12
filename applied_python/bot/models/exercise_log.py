from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from db import Base


class ExerciseLog(Base):
    __tablename__ = "exercise_log"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # длительность в минутах
    calories_burned = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
