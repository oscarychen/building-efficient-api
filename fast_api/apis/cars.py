from fastapi import APIRouter, Depends
from services.cars import CarService
from typing import Annotated, List

from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

from datetime import datetime
from pydantic import BaseModel


class CarSchema(BaseModel):
    id: int
    vin: str
    owner: str
    created_at: datetime
    updated_at: datetime
    car_model_id: int
    car_model_name: str
    car_model_year: int
    color: str


@router.get("/fastapi/", response_model=list[CarSchema])
async def list_cars(db: Annotated[AsyncSession, Depends(get_db)]):
    return await CarService(db).retrieve_all_cars()
