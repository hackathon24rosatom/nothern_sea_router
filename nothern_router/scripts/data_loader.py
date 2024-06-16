import csv
from pathlib import Path
import ast
import json
from datetime import datetime

from smp.models import Ship, Port, RouteRequest
from maps.models import Geopoint, Polygon, WaterMap, PolygonNew, PortMap

LOCAL_FILE_PATH_PORTS = 'data/ports_in.csv'
LOCAL_FILE_PATH_SHIPS = 'data/vessels_in.csv'
LOCAL_FILE_PATH_POLYGON = 'data/Icecube_polygon.geojson'
LOCAL_FILE_PATH_SCHEDULE = 'data/schedule_in.csv'
LOCAL_FILE_PATH_PORTMAP = 'data/Graph_vertex.geojson'
PARENT_PATH = Path(__file__).resolve().parent.parent.parent


def run():
    Port.objects.all().delete()
    with open(PARENT_PATH / LOCAL_FILE_PATH_PORTS, encoding='utf-8') as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            name, lat, lon = row[0], row[1], row[2]
            location_point = Geopoint(latitude=lat, longitude=lon)
            location_point.save()
            Port(
                name=name,
                location_point=location_point, 
            ).save()

    Ship.objects.all().delete()
    with open(PARENT_PATH / LOCAL_FILE_PATH_SHIPS, encoding='utf-8') as file:
        reader = csv.reader(file, delimiter="\t")
        for row in reader:
            name, category, max_speed, lat, lon = row[0], row[1], row[2], row[3], row[4]
            location_point = Geopoint(latitude=lat, longitude=lon)
            location_point.save()
            Ship(
                name=name,
                category=category,
                max_speed=max_speed,
                location_point=location_point, 
            ).save()
    
    PolygonNew.objects.all().delete()
    with open(PARENT_PATH / LOCAL_FILE_PATH_POLYGON, 'r', encoding='utf-8') as f:
        geodata = json.load(f)
    geodata = geodata.get("features")
    for sample in geodata:
        PolygonNew(test=json.dumps(sample)).save()

    PortMap.objects.all().delete()
    with open(PARENT_PATH / LOCAL_FILE_PATH_PORTMAP, 'r', encoding='utf-8') as f:
        geodata = json.load(f)
    geodata = geodata.get("features")
    for sample in geodata:
        PortMap(test=json.dumps(sample)).save()

    RouteRequest.objects.all().delete()
    with open(PARENT_PATH / LOCAL_FILE_PATH_SCHEDULE, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            name, start, end, dates = row[0], row[1], row[2], row[3]
            ship = Ship.objects.filter(name=name).first()
            start_port = Port.objects.filter(name=start).first()
            end_port = Port.objects.filter(name=end).first()       
            date_in = datetime.strptime(dates, "%d.%m.%y").date()
            RouteRequest(
                ship=ship,
                start_point=start_port,
                destination_point=end_port,
                date_start=date_in,
                active="ACT"
            ).save()
