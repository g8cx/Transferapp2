from django.contrib import admin
from .models import Cargo

@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('name',)

# Также можно использовать: admin.site.register(Cargo)
