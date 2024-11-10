
from django.urls import path
from car_registry.views import CarListView, CarListViewWithModel, CarListViewWithModelPrefetched
from apis.car_listing_api import CarListingAPI
from apis.car_listing_api_2 import CarListingAPI as CarListingAPI2
from apis.car_listing_api_3 import CarListingAPI as CarListingAPI3
from apis.car_listing_api_4_paginated import CarListingAPI as CarListingAPI4


urlpatterns = [
    path('cars/', CarListView.as_view()),
    path('retrieve-cars-with-model/', CarListViewWithModel.as_view()),
    path('retrieve-cars-with-prefetch-related/', CarListViewWithModelPrefetched.as_view()),
    
    path('api/cars/', CarListingAPI.as_view()),
    path('api/cars-2/', CarListingAPI2.as_view()),
    path('api/cars-3/', CarListingAPI3.as_view()),
    path('api/cars-4-paginated/', CarListingAPI4.as_view()),
]
