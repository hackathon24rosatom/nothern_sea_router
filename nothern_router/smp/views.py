from django.shortcuts import render
from smp.models import Ship, Route, RouteRequest
from django.http import HttpResponse
from django.db.models import Q
import datetime


def ships(request):
    # ships
    ships = Ship.objects.all().values()
    # ships = Ship.objects.filter(
    #     Q(date_start__gte=datetime.date(2010, 5, 24))
    # ).values()
    return HttpResponse(ships)
