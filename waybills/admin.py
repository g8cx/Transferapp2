from django.contrib import admin
from .models import Waybill, WaybillItem

@admin.register(Waybill)
class WaybillAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'sender', 'receiver', 'driver', 'vehicle')
    list_filter = ('date', 'sender', 'receiver')
    search_fields = ('number',)

@admin.register(WaybillItem)
class WaybillItemAdmin(admin.ModelAdmin):
    list_display = ('waybill', 'cargo', 'quantity', 'weight')
    list_filter = ('cargo',)

# Также можно использовать: admin.site.register(Waybill)
# и admin.site.register(WaybillItem)
