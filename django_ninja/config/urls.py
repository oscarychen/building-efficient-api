
from django.urls import path
from ninja import NinjaAPI
from apis.car_listing_api import router
from custom_renderer import ORJSONRenderer

# api = NinjaAPI()  # Chapter 2
api = NinjaAPI(renderer=ORJSONRenderer())  # Chapter 3

api.add_router("", router)


urlpatterns = [
    path("", api.urls),
]
