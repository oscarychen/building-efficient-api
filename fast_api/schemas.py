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
