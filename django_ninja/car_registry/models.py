from django.db import models


class CarModel(models.Model):
    name = models.CharField(max_length=100)
    make = models.CharField(max_length=100)
    year = models.IntegerField()
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class Car(models.Model):
    vin = models.CharField(max_length=17)
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    owner = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
