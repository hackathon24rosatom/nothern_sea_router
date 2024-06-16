from django.conf import settings
from django.contrib import admin

from .models import (Port, Ship, RouteRequest)


@admin.register(Port)
class PortAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    search_fields = ('name',)


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    search_fields = ('name', 'category', 'location_point')


@admin.register(RouteRequest)
class RouteRequestAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    search_fields = ('ship', 'start_point', 'destination_point', 'pub_date')
