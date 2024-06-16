from django.db import models
from django.utils.translation import gettext_lazy as _


def detect_point_category(ice_integral_coef: float) -> int:
    if ice_integral_coef >= 20:
        return IceCategory.LIGHT
    if ice_integral_coef >= 15:
        return IceCategory.MEDIUM
    return IceCategory.STRONG


class Geopoint(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()


class Polygon(models.Model):

    sector_id = models.PositiveSmallIntegerField(
        verbose_name='Сектор'
    )

    bottom_left_x = models.FloatField()
    upper_left_x = models.FloatField()
    upper_right_x = models.FloatField()
    bottom_right_x = models.FloatField()

    bottom_left_y = models.FloatField()
    upper_left_y = models.FloatField()
    upper_right_y = models.FloatField()
    bottom_right_y = models.FloatField()

    lat = models.FloatField()
    lon = models.FloatField()


class PolygonNew(models.Model):
    test = models.JSONField(encoder=None)


class PortMap(models.Model):
    test = models.JSONField(encoder=None)


class IceCategory(models.TextChoices):
    """
    Ice with 3 categories based on integral coefficient:
    light (20-21), medium (15-19), strong (10-14)
    """
    LIGHT = "L", _("(Высокая проходимость) Высокий интегральный коэффициент")
    MEDIUM = "M", _("(Средняя проходимость) Средний интегральный коэффициент")
    STRONG = "S", _("(Низкая проходимость) Низкий интегральный коэффициент")


class WaterMap(models.Model):
    sector_id = models.ForeignKey(
        Polygon,
        on_delete=models.SET_DEFAULT,
        default=-1,
        related_name='map',
        verbose_name=_('Сектор')
    )
    ice_coef = models.FloatField()
    ice_category = models.CharField(
        max_length=20,
        choices=IceCategory.choices,
        default=IceCategory.STRONG,
    )

    def save(self):
        self.ice_category = IceCategory(detect_point_category(self.ice_coef))
        super().save(self)
