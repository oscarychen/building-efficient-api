from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from services.car_services import CarService


class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        car_dicts = CarService().retrieve_all_cars_as_dicts()
        return Response(car_dicts, status=status.HTTP_200_OK)