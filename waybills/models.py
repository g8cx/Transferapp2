from django.db import models
from companies.models import Company
from drivers.models import Driver
from vehicles.models import Vehicle
from cargo.models import Cargo


class Waybill(models.Model):
    number = models.CharField(max_length=50)
    date = models.DateField()
    loading_date = models.DateField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    additional_info = models.TextField(blank=True)

    sender = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="sent_waybills"
    )

    receiver = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="received_waybills"
    )

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)

    def __str__(self):
        return self.number


class WaybillItem(models.Model):
    waybill = models.ForeignKey(Waybill, on_delete=models.CASCADE)
    cargo = models.ForeignKey(Cargo, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    weight = models.FloatField(default=0)
