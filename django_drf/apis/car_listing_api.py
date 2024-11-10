from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import serializers

from services.car_services import CarService


class CarListingResponseSerializer(serializers.Serializer):
    vin = serializers.CharField()
    owner = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    model = serializers.IntegerField(source="model_id")
    model_name = serializers.CharField(source='model.name')
    model_year = serializers.IntegerField(source='model.year')
    color = serializers.CharField(source='model.color')
    

class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        car_instances = CarService().retrieve_all_cars()
        response_serializer = CarListingResponseSerializer(car_instances, many=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)