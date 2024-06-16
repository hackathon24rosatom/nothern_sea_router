from django.shortcuts import render
from maps.models import Polygon, PolygonNew, PortMap
import json


# TODO: load dotenv key
def default_map(request):
    # TODO: You can place your key here
    mapbox_access_token = ""

    ice_polygons = PolygonNew.objects.all()
    ice_polygons = [
        json.loads(el.test) for el in ice_polygons
    ]
    json_list_ice = json.dumps(ice_polygons)

    ports = PortMap.objects.all()
    ports = [
        json.loads(el.test) for el in ports
    ]
    json_list_ports = json.dumps(ports)

    return render(request, 'main.html', {
        'mapbox_access_token': mapbox_access_token,
        'ice_polygons': json_list_ice,
        'ports': json_list_ports,
    })


# TODO: fill view
def gannt(request):
    # даты старта окончания для каждого осудна
    # путь (лист из гео)
    return render(request)


# TODO: fill view
def algo(request):
    # tick (int hrs), n steps
    # ships (ice break last!) grid
    return render(request)
