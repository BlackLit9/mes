from django.contrib import admin

from .models import MaterialInventory, WarehouseInfo, InventoryLog

admin.site.register([MaterialInventory, WarehouseInfo, InventoryLog])
