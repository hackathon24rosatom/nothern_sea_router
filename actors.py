1. граф из маршрутных точек + нужна информация о переходах (ребрах) какие квадраты покрывает путь (чтобы считать плотность льда).
2. класс кораблей, скорость, класс льда, точка отправления\прибытия и т.д., возможно стоит сразу сделать так, чтобы один класс в другой можно было добавить, будет тогда гибкий конструктор караванов.


import enum
import datetime
from typing import Callable
from dataclasses import dataclass, field


class IceCategory(enum.Enum):
    """
    Ice with 3 categories based on integral coefficient:
    light (20-21), medium (15-19), strong (10-14)
    """
    light = 0
    medium = 1
    strong = 2


class VesselCategory(enum.Enum):
    """
    Vessel types based on its ability to passage ice.
    """
    not_assigned = 0
    ice1 = 1
    ice2 = 2
    ice3 = 3
    arc4 = 4
    arc5 = 5
    arc6 = 6
    arc7 = 7
    arc8 = 8
    arc91 = 9
    arc92 = 10


class Passage(enum.Enum):
    """
    Restrictions on vessel movements - from independent movement
    until the need for convoy by an icebreaker or a ban on movement.
    """
    independent = 0
    convoy = 1
    restricted = 2


speed_limitations: Dict[int, Callable] = {
    IceCategory.light: (
        lambda vessel: vessel.max_speed
        ),
    IceCategory.medium: (
        lambda vessel: vessel.max_speed if vessel.category in (
                VesselCategory.not_assigned,
                VesselCategory.ice1,
                VesselCategory.ice2,
                VesselCategory.ice3,
            ) else vessel.max_speed * 0.8 if vessel.category in (
                VesselCategory.arc4,
                VesselCategory.arc5,
                VesselCategory.arc6,
            ) else vessel.max_speed * 0.6 if vessel.category in (
                VesselCategory.arc7,
            ) else min(19, vessel.max_speed) if vessel.category in (
                VesselCategory.arc91,
            ) else min(19, vessel.max_speed * 0.9) if vessel.category in (
                VesselCategory.arc92,
            ) else None
        ),
    IceCategory.strong: (
        lambda vessel: vessel.max_speed * 0.7 if vessel.category in (
                VesselCategory.arc4,
                VesselCategory.arc5,
                VesselCategory.arc6,            
            ) else vessel.max_speed * 0.8 if vessel.category in (
                VesselCategory.arc7,
            ) else min(14, vessel.max_speed) if vessel.category in (
                VesselCategory.arc91,
            ) else min(14, vessel.max_speed * 0.75) if vessel.category in (
                VesselCategory.arc92,
            ) else None
        )
    }


passage_limitations: Dict[int, Callable] = {
    IceCategory.light: (lambda vessel: Passage.independent),
    IceCategory.medium: (lambda vessel: Passage.convoy if vessel.category in (
            VesselCategory.not_assigned,
            VesselCategory.ice1,
            VesselCategory.ice2,
            VesselCategory.ice3,
            VesselCategory.arc4,
            VesselCategory.arc5,
            VesselCategory.arc6,
        ) else (Passage.independent, Passage.convoy) if vessel.category in (
            VesselCategory.arc7,
        ) else Passage.independent if vessel.category in (
            VesselCategory.arc91,
            VesselCategory.arc92,
        )
    ),
    IceCategory.strong: (lambda vessel: Passage.restricted if vessel.category in (
            VesselCategory.not_assigned,
            VesselCategory.ice1,
            VesselCategory.ice2,
            VesselCategory.ice3,
        ) else Passage.convoy id vessel.category in (
            VesselCategory.arc4,
            VesselCategory.arc5,
            VesselCategory.arc6,  
            VesselCategory.arc7,         
        ) else Passage.independent if vessel.category in (
            VesselCategory.arc91,
            VesselCategory.arc92,
        )
    )
}


class VesselMoveStatus(enum.Enum):
    waiting = 0
    routing = 1


@dataclass
class Geopoint:
    """
    Маршрутная точка, которая имеет координаты (широта, долгота)
    """
    latitude: float
    longitude: float


@dataclass
class Date:
    # add calendar sometimes later
    date: datetime.date

    def _next():
        ...
    
    def _prev():
        ...


@dataclass
class Port:
    """
    Points  on SMP.
    """
    name: str
    geopoint: Geopoint


@dataclass
class Route:
    ports = list[Port]


@dataclass
class RouteRequest:
    """
    Request on travel through SMP for vessels of type ship only.
    """
    start_point: Port
    destination_point: Port
    date_start: Date
    date_end: Date | None
    eval_route: Route | None


@dataclass
class ConvoyForceRequest(RouteRequest):
    """
    Force request for convoying ships for icebreakers.
    """
    ...


@dataclass
class Vessel:
    """
    ??? based on env and agent profile, should discuss
    """
    name: str
    category: int
    location_point: Geopoint
    route_request: RouteRequest | None
    status: int
    avg_speed: float
    curr_cpeed: float

    info: str = ('Название: {name:}; '
                     'Следует от: {route_request.start_point:}; '
                     'Следует в: {route_request.destination_point:}; '
                     'Текущая локация: {location_point:}; '
                     'На маршруте или простой: {status:}; '
                     'Средняя скорость на маршруте: {avg_speed:.3f} узлов; ',
                     'Текущая скорость на маршруте: {curr_speed:.3f} узлов; ',
                     'Ожидаемая дата завершения маршрута: {route_request.date_end:}.',
                     )

    def __repr__(self) -> str:
        return self.info.format(**asdict(self))


@dataclass
class Icebreaker(Vessel):
    ...


@dataclass
class Ship(Vessel):
    ...

