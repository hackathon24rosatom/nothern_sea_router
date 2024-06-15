from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from typing import Dict, Optional, Callable

from maps.models import IceCategory, Geopoint

User = get_user_model()


class VesselCategory(models.TextChoices):
    """
    Ice with 3 categories based on integral coefficient:
    light (20-21), medium (15-19), strong (10-14)
    """
    NA = "NotAssigned", _("Не определено")
    ICE1 = "Ice1", _("Легкое судно (1)")
    ICE2 = "Ice2", _("Легкое судно (2)")
    ICE3 = "Ice3", _("Легкое судно (3)")
    ARC4 = "Arc4", _("Среднее судно (4)")
    ARC5 = "Arc5", _("Среднее судно (5)")
    ARC6 = "Arc6", _("Среднее судно (6)")
    ARC7 = "Arc7", _("Среднее судно (7)")
    ARC8 = "Arc8", _("Среднее судно (8)")
    ARC91 = "Arc91", _("Ледокол (91)")
    ARC92 = "Arc92", _("Ледокол (92)")


class Passage(models.TextChoices):
    """
    Restrictions on vessel movements - from independent movement
    until the need for convoy by an icebreaker or a ban on movement.
    """
    INDEPENDENT = "independent", _("Самостоятельно")
    CONVOY = "convoy", _("Конвой")
    RESTRICTED = "restricted", _("Запрещено")


def detect_point_category(ice_integral_coef: float) -> int:
    if ice_integral_coef >= 20:
        return IceCategory.light
    if ice_integral_coef >= 15:
        return IceCategory.medium
    return IceCategory.strong


speed_limitations: Dict[int, Callable] = {
    IceCategory.LIGHT: (
        lambda vessel: vessel.max_speed
        ),
    IceCategory.MEDIUM: (
        lambda vessel: vessel.max_speed if vessel.category in (
                VesselCategory.NA,
                VesselCategory.ICE1,
                VesselCategory.ICE2,
                VesselCategory.ICE33,
            ) else vessel.max_speed * 0.8 if vessel.category in (
                VesselCategory.ARC4,
                VesselCategory.ARC5,
                VesselCategory.ARC6,
            ) else vessel.max_speed * 0.6 if vessel.category in (
                VesselCategory.ARC7,
            ) else min(19, vessel.max_speed) if vessel.category in (
                VesselCategory.ARC91,
            ) else min(19, vessel.max_speed * 0.9) if vessel.category in (
                VesselCategory.ARC92,
            ) else None
        ),
    IceCategory.STRONG: (
        lambda vessel: vessel.max_speed * 0.7 if vessel.category in (
                VesselCategory.ARC4,
                VesselCategory.ARC5,
                VesselCategory.ARC6,          
            ) else vessel.max_speed * 0.8 if vessel.category in (
                VesselCategory.ARC7,
            ) else min(14, vessel.max_speed) if vessel.category in (
                VesselCategory.ARC91,
            ) else min(14, vessel.max_speed * 0.75) if vessel.category in (
                VesselCategory.ARC92,
            ) else None
        )
    }


passage_limitations: Dict[int, Callable] = {
    IceCategory.LIGHT: (lambda vessel: Passage.INDEPENDENT),
    IceCategory.MEDIUM: (lambda vessel: Passage.CONVOY if vessel.category in (
            VesselCategory.NA,
            VesselCategory.ICE1,
            VesselCategory.ICE2,
            VesselCategory.ICE3,
            VesselCategory.ARC4,
            VesselCategory.ARC5,
            VesselCategory.ARC6,  
        ) else (Passage.INDEPENDENT, Passage.CONVOY) if vessel.category in (
            VesselCategory.ARC7,  
        ) else Passage.INDEPENDENT if vessel.category in (
            VesselCategory.ARC91,
            VesselCategory.ARC92,
        ) else None
    ),
    IceCategory.STRONG: (lambda vessel: Passage.RESTRICTED if vessel.category in (
            VesselCategory.NA,
            VesselCategory.ICE1,
            VesselCategory.ICE2,
            VesselCategory.ICE3,
        ) else Passage.CONVOY if vessel.category in (
            VesselCategory.ARC4,
            VesselCategory.ARC5,
            VesselCategory.ARC6,  
            VesselCategory.ARC7,         
        ) else Passage.INDEPENDENT if vessel.category in (
            VesselCategory.ARC91,
            VesselCategory.ARC92,
        ) else None
    )
}


class Port(models.Model):
    name = models.CharField(max_length=30)
    location_point = models.OneToOneField(
        Geopoint, 
        null=True, 
        on_delete=models.SET_NULL
    )


class Ship(models.Model):
    name = models.CharField(
        max_length=30,
        unique=True,
        verbose_name=_('Название'),
    )
    category = models.CharField(
        max_length=20,
        choices=VesselCategory.choices,
        default=VesselCategory.NA,
    )
    location_point = models.OneToOneField(
        Geopoint, 
        null=True, 
        on_delete=models.SET_NULL
    )
    # status: int
    max_speed = models.FloatField()

    def get_category(self) -> VesselCategory:
        # Get value from choices enum
        return VesselCategory(self.category)


class RouteRequest(models.Model):
    """
    Request on travel through SMP for vessels of type ship only.
    """

    DELIVERY_CHOICES = [
        ('ACT', 'Актуальная'),
        ('OLD', 'Исполненная')
    ]

    ship = models.ForeignKey(
        Ship,
        on_delete=models.SET_DEFAULT,
        default=-1,
        related_name='route_requests',
        verbose_name=_('Судно')
    )
    start_point = models.ForeignKey(
        Port,
        on_delete=models.SET_DEFAULT,
        default=-1,
        related_name='route_requests_start',
        verbose_name=_('Порт отправления')
    )
    destination_point = models.ForeignKey(
        Port,
        on_delete=models.SET_DEFAULT,
        default=-1,
        related_name='route_requests_end',
        verbose_name=_('Порт назначения')
    )
    pub_date = models.DateTimeField(
        verbose_name=_('Дата размещения заявки'),
        auto_now_add=True,
        db_index=True
    )
    date_start = models.DateTimeField(
        verbose_name=_('Дата начала маршрута'),
        null=True
    )
    date_end = models.DateTimeField(
        verbose_name=_('Дата окончания маршрута'),
        null=True
    )
    active = models.CharField(
        max_length=15,
        choices=DELIVERY_CHOICES
    )
    # eval_route: Route | None

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Маршрутная заявка'
        verbose_name_plural = 'Маршрутные заявки'
        constraints = [
            models.UniqueConstraint(fields=['ship', 'start_point', 'date_start'],
                                    name='unique_ship_start')
        ]

    def __str__(self):
        return f'{self.ship} {self.start_point} {self.destination_point} {self.date_start}'

# TODO: neighbors

# class Route:
#     """
#     Optimal route from start point to destination (can consist of 2 or more??? ports)
#     """
#     ports: List[Port] = field(default_factory=list)
#     steps: List[List[Tuple[float, float]]] = field(init=False, default_factory=list)
#     passageway: List[np.array] = field(init=False, default_factory=list)

#     def __post_init__(self):
#         neighbors = load_serialized_neighbors("data")
#         for point_left, point_right in zip(self.ports[:-1], self.ports[1:]):
#             _steps = route_steps_on_edge(
#                 point_left.geopoint.latitude, point_left.geopoint.longitude,
#                 point_right.geopoint.latitude, point_right.geopoint.longitude,                
#                 )
#             _closest = get_closest_grid_points_on_route_step(neighbors, _steps)

#             self.steps.append( _steps)
#             self.passageway.append( _closest)
    
#     # TODO should be from class Date and connected to real date when convoy|vessel will be in place - for now same conditions on ice
#     def ice_state_on_edge(self, date: int, grid: np.array, pair_idx: int) -> Tuple[np.array, Set[float]]:
#         return ice_metrics_on_route(self.passageway[pair_idx], grid=grid, date_num_col=date)



# from actors import Ship, VesselCategory, Geopoint, VesselMoveStatus
# from route_metrics import ice_integral_coefficient_on_step
