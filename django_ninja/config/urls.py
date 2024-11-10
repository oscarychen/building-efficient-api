
from django.urls import path
from ninja import NinjaAPI
from apis.car_listing_api import router
api = NinjaAPI()

api.add_router("/cars/", router)

urlpatterns = [
    path("api/", api.urls),
]
