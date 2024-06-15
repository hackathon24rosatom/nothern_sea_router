from django.shortcuts import render
from maps.models import Polygon, PolygonNew
import json


def default_map(request):
    # TODO: load dotenv key

    ice_polygons = PolygonNew.objects.all()[:1000]
    ice_polygons = [
        json.loads(el.test) for el in ice_polygons
    ]
    mapbox_access_token = "pk.eyJ1IjoiZW1pbGljaGNrYSIsImEiOiJjbHhic3VuNHcyNXZ6MmpzY2Q3ZzcyamhvIn0.qgjZ8az9cYhze1tXJ0ZLig"
    json_list = json.dumps(ice_polygons)

    return render(request, 'merkers.html', {
        'mapbox_access_token': mapbox_access_token,
        'ice_polygons': json_list,
    })


def gannt(request):
    # даты старта окончания для каждого осудна
    # путь (лист из гео)
    return render(request, 'gannt.html', {})


def algo(request):
    # tick (int hrs), n steps
    # ships (ice break last!) grid
    return render(request)
