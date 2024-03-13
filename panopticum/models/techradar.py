import django.forms
from django.db import models
from simple_history.models import HistoricalRecords

class RingPosition(models.IntegerChoices):
    INNER = 0, "Inner"
    FIRST = 1, "First"
    SECOND = 2, "Second"
    OUTER = 3, "Outer"

class QuadrantPosition(models.IntegerChoices):
    INNER = 0, "Bottom Right"
    FIRST = 1, "Bottom Left"
    SECOND = 2, "Top Left"
    OUTER = 3, "Top Right"

TECH_RADAR_MOVE = (
    (0, "Not moved"),
    (-1, "Moved out"),
    (1, "Moved in"),
)


class TechradarQuadrant(models.Model):
    name = models.CharField(max_length=64, help_text="Top Right, Bottom Right, ...")
    position = models.IntegerField(default=0, choices=QuadrantPosition.choices)
    description = models.TextField(blank=True, null=True)

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __str__(self):
        return self.__unicode__()


class TechradarRing(models.Model):
    name = models.CharField(max_length=64)
    position = models.IntegerField(default=0, choices=RingPosition.choices)
    description = models.TextField(blank=True, null=True)
    color = models.CharField("Color code: #000000", default="#e0e0e0", max_length=64, blank=False)

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.name}"

    def __str__(self):
        return self.__unicode__()


class TechradarEntry(models.Model):
    label = models.CharField("Entry name", max_length=64, default="", blank=False)
    description = models.TextField(blank=True, null=True)
    quadrant = models.ForeignKey(TechradarQuadrant, on_delete=models.CASCADE)
    ring = models.ForeignKey(TechradarRing, on_delete=models.CASCADE)
    moved = models.IntegerField("Short history tracking", choices=TECH_RADAR_MOVE, default=TECH_RADAR_MOVE[0][0])
    link = models.URLField("Entry link URL", max_length=4096, blank=True)
    active = models.BooleanField(default=True)
    history = HistoricalRecords()

    def __unicode__(self):
        return f"{self.__class__.__name__}: {self.label}"

    def __str__(self):
        return self.__unicode__()
