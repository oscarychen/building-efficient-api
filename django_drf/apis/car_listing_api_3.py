from rest_framework import status
from rest_framework.request import Request
from rest_framework.views import APIView

from custom_response import OrJsonResponse
from services.car_services import CarService



class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> OrJsonResponse:
        car_dicts = CarService().retrieve_all_cars_as_dicts()
        return OrJsonResponse(car_dicts, status=status.HTTP_200_OK)
