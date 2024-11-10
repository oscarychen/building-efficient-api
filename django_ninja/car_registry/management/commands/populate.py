from typing import Any
from django.core.management.base import BaseCommand
import random
from car_registry.models import Car, CarModel
from faker import Faker


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> str | None:
        
        self.bulk_create_car_models(200)
        
        for i in range(50):
            print(f'Creating cars batch {i+1}...')
            self.bulk_create_cars(2000)
        
    
    def bulk_create_car_models(self, quantity=100):
        colors = ['Red', 'Blue', 'Green', 'Yellow', 'Black', 'White', 'Silver', 'Gold', 'Purple', 'Orange']
        years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        prices = [10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000, 100000]
        
        car_models = []
        
        for i in range(quantity):
            car_models.append(
                CarModel(
                    name=f'Car Model {i}', 
                    make=f'Car Make {i}', 
                    year=random.choice(years), 
                    color=random.choice(colors), 
                    price=random.choice(prices)
                    )
            )
            
        CarModel.objects.bulk_create(car_models)
        
    def bulk_create_cars(self, quantity=1000):
        car_models = CarModel.objects.all().values_list('id', flat=True)
        
        cars = []
        
        for i in range(quantity):
            cars.append(
                Car(
                    vin=f'VIN-{i}', 
                    model_id=random.choice(car_models), 
                    owner=Faker().name()
                    )
            )
            
        Car.objects.bulk_create(cars)
        