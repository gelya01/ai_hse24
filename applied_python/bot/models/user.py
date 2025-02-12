from sqlalchemy import Column, Integer, String, Float
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    gender = Column(String, nullable=False)
    activity = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    city = Column(String, nullable=False)
    daily_water = Column(Float, default=0)
    daily_calories = Column(Float, default=0)
    daily_burned = Column(Float, default=0)
