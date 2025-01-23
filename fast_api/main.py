from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import CarSchema
from services import CarService

from typing import Annotated, List

app = FastAPI()


@app.get("/api/cars/", response_model=List[CarSchema])
async def list_cars(db: Annotated[AsyncSession, Depends(get_db)]):
    return await CarService(db).retrieve_all_cars()
