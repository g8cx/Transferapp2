from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'model', 'capacity')

# Также можно использовать: admin.site.register(Vehicle)
