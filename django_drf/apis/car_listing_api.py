from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status


class CarListingAPI(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        print(request)
        return Response({'detail': 'to be implemented'}, status=status.HTTP_501_NOT_IMPLEMENTED)