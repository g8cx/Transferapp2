from django.db import models

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20)
    model = models.CharField(max_length=100)
    capacity = models.FloatField()

    def __str__(self):
        return self.plate_number