import enum
import datetime
from typing import Callable, Dict, List, Tuple, Set
from dataclasses import dataclass, field

import numpy as np

from route_metrics import route_steps_on_edge, get_closest_grid_points_on_route_step, ice_metrics_on_route
from utils import load_serialized_neighbors

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


def detect_point_category(ice_integral_coef: float) -> int:
    if ice_integral_coef >= 20:
        return IceCategory.light
    if ice_integral_coef >= 15:
        return IceCategory.medium
    return IceCategory.strong


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
        ) else None
    ),
    IceCategory.strong: (lambda vessel: Passage.restricted if vessel.category in (
            VesselCategory.not_assigned,
            VesselCategory.ice1,
            VesselCategory.ice2,
            VesselCategory.ice3,
        ) else Passage.convoy if vessel.category in (
            VesselCategory.arc4,
            VesselCategory.arc5,
            VesselCategory.arc6,  
            VesselCategory.arc7,         
        ) else Passage.independent if vessel.category in (
            VesselCategory.arc91,
            VesselCategory.arc92,
        ) else None
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


# TODO: discuss
@dataclass
class Route:
    """
    Optimal route from start point to destination (can consist of 2 or more??? ports)
    """
    ports: List[Port] = field(default_factory=list)
    steps: List[List[Tuple[float, float]]] = field(init=False, default_factory=list)
    passageway: List[np.array] = field(init=False, default_factory=list)

    def __post_init__(self):
        neighbors = load_serialized_neighbors("data")
        for point_left, point_right in zip(self.ports[:-1], self.ports[1:]):
            _steps = route_steps_on_edge(
                point_left.geopoint.latitude, point_left.geopoint.longitude,
                point_right.geopoint.latitude, point_right.geopoint.longitude,                
                )
            _closest = get_closest_grid_points_on_route_step(neighbors, _steps)

            self.steps.append( _steps)
            self.passageway.append( _closest)
    
    # TODO should be from class Date and connected to real date when convoy|vessel will be in place - for now same conditions on ice
    def ice_state_on_edge(self, date: int, grid: np.array, pair_idx: int) -> Tuple[np.array, Set[float]]:
        return ice_metrics_on_route(self.passageway[pair_idx], grid=grid, date_num_col=date)


# TODO: calc optimal route in case 2 or more points??
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


# TODO: recalc mutable attr on limitations inside
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
    max_speed: float
    avg_speed: float
    curr_speed: float


@dataclass
class Icebreaker(Vessel):
    ...


@dataclass
class Ship(Vessel):
    ...
