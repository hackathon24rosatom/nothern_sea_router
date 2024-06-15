from django.conf import settings
from django.contrib import admin

from .models import (WaterMap, Polygon)


@admin.register(WaterMap)
class WaterMapAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    # search_fields = ('name',)


@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
