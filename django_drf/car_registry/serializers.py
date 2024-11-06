from rest_framework import serializers
from car_registry.models import CarModel, Car


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = '__all__'
        
        
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'