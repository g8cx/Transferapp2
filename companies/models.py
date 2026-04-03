from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    tax_id = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name
