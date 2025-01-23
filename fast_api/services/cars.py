from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.cars import Car, CarModel


class CarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def retrieve_all_cars(self):
        async with self.db.begin():
            statement = select(
                Car.id,
                Car.vin,
                Car.owner,
                Car.created_at,
                Car.updated_at,
                Car.model_id.label('car_model_id'),
                CarModel.name.label('car_model_name'),
                CarModel.year.label('car_model_year'),
                CarModel.color.label('color')
            ).join(CarModel, Car.model_id == CarModel.id)
            result = await self.db.execute(statement)
            return result.all()
