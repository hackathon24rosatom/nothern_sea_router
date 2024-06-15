import csv
from pathlib import Path
import ast
import json

from smp.models import Ship, Port
from maps.models import Geopoint, Polygon, WaterMap, PolygonNew

LOCAL_FILE_PATH_PORTS = 'data/ports_in.csv'
LOCAL_FILE_PATH_SHIPS = 'data/vessels_in.csv'
# LOCAL_FILE_PATH_POLYGON = 'data/polygons.csv'
LOCAL_FILE_PATH_POLYGON = 'data/Icecube_polygon.geojson'
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
        Ship.objects.all().delete()
    # with open(PARENT_PATH / LOCAL_FILE_PATH_POLYGON, encoding='utf-8') as file:
    #     reader = csv.reader(file, delimiter=",")
    #     for row in reader:
    #         i, a, b, c, d, ice, lat, lon = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]
    #         a, b, c, d = ast.literal_eval(a), ast.literal_eval(b), ast.literal_eval(c), ast.literal_eval(d)
    #         Polygon(
    #             sector_id=i,
    #             bottom_left_x=a[0],
    #             upper_left_x=b[0],
    #             upper_right_x=c[0], 
    #             bottom_right_x=d[0],
    #             bottom_left_y=a[1],
    #             upper_left_y=b[1], 
    #             upper_right_y=c[1], 
    #             bottom_right_y=d[1],
    #             lat=lat,
    #             lon=lon
    #         ).save()
    with open(PARENT_PATH / LOCAL_FILE_PATH_POLYGON, 'r') as f:
        geodata = json.load(f)
    geodata = geodata.get("features")
    for sample in geodata:
        PolygonNew(test=json.dumps(sample)).save()
    


