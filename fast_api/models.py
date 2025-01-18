from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.types import DECIMAL
from database import Base
from sqlalchemy.sql import func

class CarModel(Base):
    __tablename__ = "car_registry_carmodel"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100))
    make = Column(String(length=100))
    year = Column(Integer)
    color = Column(String(length=100))
    price = Column(DECIMAL(precision=10, scale=2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Car(Base):
    __tablename__ = "car_registry_car"

    id = Column(Integer, primary_key=True, index=True)
    vin = Column(String(length=17))
    model_id = Column(Integer, ForeignKey("car_registry_carmodel.id"))
    owner = Column(String(length=100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
