from rest_framework import serializers
from car_registry.models import CarModel, Car


class CarModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarModel
        fields = '__all__'
        
        
class CarSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    model_year = serializers.IntegerField(source='model.year', read_only=True)
    color = serializers.CharField(source='model.color', read_only=True)
    class Meta:
        model = Car
        fields = '__all__'