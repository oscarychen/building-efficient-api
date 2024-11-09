
from django.urls import path
from car_registry.views import CarListView, CarListViewWithModel, CarListViewWithModelPrefetched
from apis.car_listing_api import CarListingAPI


urlpatterns = [
    path('cars/', CarListView.as_view()),
    path('retrieve-cars-with-model/', CarListViewWithModel.as_view()),
    path('retrieve-cars-with-prefetch-related/', CarListViewWithModelPrefetched.as_view()),
    
    path('api/cars/', CarListingAPI.as_view()),
]
