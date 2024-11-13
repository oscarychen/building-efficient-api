from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import serializers

from custom_response import OrJsonResponse
from services.car_services import CarService


class CarListingResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vin = serializers.CharField()
    owner = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    car_model_id = serializers.IntegerField(source="model_id")
    car_model_name = serializers.CharField(source='model.name')
    car_model_year = serializers.IntegerField(source='model.year')
    color = serializers.CharField(source='model.color')
    

class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        car_instances = CarService().retrieve_all_cars()
        response_serializer = CarListingResponseSerializer(car_instances, many=True)
        return OrJsonResponse(response_serializer.data, status=status.HTTP_200_OK)