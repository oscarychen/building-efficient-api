from rest_framework.generics import ListAPIView
from car_registry.serializers import CarSerializer
from car_registry.models import Car


class CarListView(ListAPIView):
    serializer_class = CarSerializer
    queryset = Car.objects.all()
