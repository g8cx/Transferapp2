from django.db import models

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, blank=True)
    model = models.CharField(max_length=100, blank=True)
    capacity = models.FloatField(default=0)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description or self.plate_number or self.model or f"Vehicle #{self.pk}"
