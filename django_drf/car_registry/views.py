from rest_framework.generics import ListAPIView
from car_registry.serializers import CarSerializer, CarSerializerWithRelatedModel
from car_registry.models import Car


class CarListView(ListAPIView):
    serializer_class = CarSerializer
    queryset = Car.objects.all()


class CarListViewWithModel(ListAPIView):
    serializer_class = CarSerializerWithRelatedModel
    queryset = Car.objects.all()


class CarListViewWithModelPrefetched(ListAPIView):
    serializer_class = CarSerializerWithRelatedModel
    queryset = Car.objects.all().prefetch_related('model')
    