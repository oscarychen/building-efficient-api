from django.db.models import F

from car_registry.models import Car


class CarService:
    def retrieve_all_cars(self):
        return Car.objects.all().prefetch_related('model')

    def retrieve_all_cars_annotated(self):
        qs = self.retrieve_all_cars()
        qs = qs.annotate(
            car_model_id=F('model_id'),
            car_model_name=F('model__name'),
            car_model_year=F('model__year'),
            color=F('model__color')
        )
        return qs

    def retrieve_all_cars_as_dicts(self):
        cars = self.retrieve_all_cars_annotated()
        return cars.values(
            'id',
            'vin',
            'owner',
            'created_at',
            'updated_at',
            'car_model_id',
            'car_model_name',
            'car_model_year',
            'color'
        )