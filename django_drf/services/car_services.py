from django.db.models import F

from car_registry.models import Car


class CarService:
    def retrieve_all_cars(self):
        return Car.objects.all().prefetch_related('model')

    def retrieve_all_cars_annotated(self):
        qs = self.retrieve_all_cars()
        qs = qs.annotate(
            model_name=F('model__name'),
            model_year=F('model__year'),
            color=F('model__color')
        )
        return qs

    def retrieve_all_cars_as_dicts(self):
        cars = self.retrieve_all_cars_annotated()
        return cars.values(
            'vin',
            'owner',
            'created_at',
            'updated_at',
            'model_id',
            'model_name',
            'model_year',
            'color'
        )