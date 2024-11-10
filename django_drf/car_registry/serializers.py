from rest_framework import serializers
from car_registry.models import Car


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'
        

class CarSerializerWithRelatedModel(serializers.ModelSerializer):
    car_model_id = serializers.IntegerField(source='model_id', read_only=True)
    car_model_name = serializers.CharField(source='model.name', read_only=True)
    car_model_year = serializers.IntegerField(source='model.year', read_only=True)
    color = serializers.CharField(source='model.color', read_only=True)
    class Meta:
        model = Car
        fields = [
            "id",
            "vin",
            "owner",
            "created_at",
            "updated_at",
            "car_model_id",
            "car_model_name",
            "car_model_year",
            "color",
        ]