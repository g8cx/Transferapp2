from django.db import models

class Driver(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)

    def __str__(self):
        return self.name