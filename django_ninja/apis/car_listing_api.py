from datetime import datetime

from django.http import HttpRequest
from ninja import Router, Schema

from services.car_services import CarService

router = Router()

class ListCarResponseItem(Schema):
    id: int
    vin: str
    owner: str
    created_at: datetime
    updated_at: datetime
    car_model_id: int
    car_model_name: str
    car_model_year: int
    color: str

@router.get("/cars/", response=list[ListCarResponseItem])
def list_cars(request: HttpRequest):
    return CarService().retrieve_all_cars_annotated()


@router.get("/cars-2/")
def list_cars_2(request: HttpRequest):
    return list(CarService().retrieve_all_cars_as_dicts())
