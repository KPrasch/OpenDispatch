from django.contrib.gis.db import models
from apps.map.models import Agency, Structure, Hydrant, FixedLocation


FUELS = (
    ('Gasoline', 'Gasoline'),
    ('Diesel', 'Diesel'),
    ('CNG', 'CNG'),
    ('Electric', 'Electric'),
    ('Propane', 'Propane'),
    ('Other', 'Other'),
    ('None', 'None'),
    ('Unknown', 'Unknown'),
)

CONNECTION_SIZES = (
    ('.75', '0.75 Inch'),
    ('1', '1 Inch'),
    ('1.5', '1.5 Inch'),
    ('1.75', '1.75 Inch'),
    ('2', '2 Inch'),
    ('2.5', '2.5 Inch'),
    ('3', '3 Inch'),
    ('3.5', '3.5 Inch'),
    ('4', '4 Inch'),
    ('4.5', '4.5 Inch'),
    ('5', '5 Inch'),
    ('6', '6 Inch'),
    ('12', '12 Inch'),
    ('Unknown', 'Unknown'),

)

CONNECTION_TYPES = (
    ('NST', 'NST'),
    ('Storz', 'Storz'),
    ('Air', 'Air King'),
    ('Cam', 'Cam and Groove'),
    ('Hozelock', 'Hozelock'),
    ('Garden', 'Garden Hose Thread'),
    ('Halmatro', 'Halmatro'),
    ('Express', 'Express Coupling'),
    ('Unknown', 'Unknown'),
)

HOSE_USE = (
    ('Attack', 'Attack'),
    ('Supply', 'Supply'),
    ('Link', 'Monkey Link'),
    ('Unknown', 'Unknown'),
)

TRAUMA_LEVEL = (
    ('1', 'Trauma Center Level 1'),
    ('2', 'Trauma Center Level 2'),
    ('3', 'Trauma Center Level 3'),
    ('Unknown', 'Unknown'),
)

AMBULANCE_TYPE = (
    ('1', 'Type 1 Ambulance'),
    ('2', 'Type 2 Ambulance'),
    ('3', 'Type 3 Ambulance'),
    ('4', 'Type 4 Ambulance'),
    ('Unknown', 'Unknown'),
)

MED_SUPPORT_LEVEL = (
    ('BLS', 'Basic Life Support'),
    ('ALS', 'Advanced Life Support'),
    ('Unknown', 'Unknown'),
)


class Preplan(models.Model):
    agency = models.ForeignKey(Agency)
    structure = models.ForeignKey(Structure)
    req_flow = models.PositiveIntegerField(blank=True, null=True)
    first_five = models.TextField(blank=True, null=True)
    second_due = models.TextField(blank=True, null=True)
    third_due = models.TextField(blank=True, null=True)
    resources = models.TextField(blank=True, null=True)
    considerations = models.TextField(blank=True, null=True)
    streetview_url = models.URLField(blank=True, null=True)


class Hospital(models.Model):
    location = models.ForeignKey(FixedLocation)
    title = models.CharField(max_length=512)
    trauma = models.CharField(choices=TRAUMA_LEVEL, max_length=100)


class Apparatus(models.Model):
    agency = models.ForeignKey(Agency)
    preplans = models.ManyToManyField(Preplan)
    identifier = models.PositiveIntegerField()
    width_ft = models.PositiveIntegerField(blank=True, null=True)
    length_ft = models.PositiveIntegerField(blank=True, null=True)
    height_ft = models.PositiveIntegerField(blank=True, null=True)
    medical = models.BooleanField(default=False)
    lz_equip = models.BooleanField(default=False)
    passengers = models.PositiveIntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    fuel = models.CharField(choices=FUELS, max_length=50, default="Unknown")


class Connection(models.Model):
    apparatus = models.ForeignKey(Apparatus, related_name="connections")
    size = models.CharField(choices=CONNECTION_SIZES, max_length=100)
    standard = models.CharField(choices=CONNECTION_TYPES, max_length=100)


class Inlet(Connection):
    location = models.CharField(max_length=200)


class Outlet(Connection):
    location = models.CharField(max_length=200)


class Hose(models.Model):
    apparatus = models.ForeignKey(Apparatus, related_name="hose")
    connection = models.ForeignKey(Connection, related_name="connection")
    length = models.PositiveIntegerField()
    use = models.CharField(choices=HOSE_USE, max_length=256)


class Preconnect(Hose):
    location = models.CharField(max_length=200)
    nozzle = models.CharField(max_length=200)


class Deadlay(Hose):
    location = models.CharField(max_length=200)


class Equipment(models.Model):
    apparatus = models.ForeignKey(Apparatus, related_name="equipment")


class GroundLadder(Equipment):
    height_ft = models.PositiveIntegerField()


class Tool(Equipment):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=500, blank=True, null=True)


class Gear(Equipment):
    title = models.CharField(max_length=256)
    description = models.CharField(max_length=500, blank=True, null=True)


class Engine(Apparatus):
    capacity = models.PositiveIntegerField()
    max_gpm = models.PositiveIntegerField()


class Rescue(Engine):
    extrication = models.BooleanField(default=False)
    ropes = models.BooleanField(default=False)
    ice = models.BooleanField(default=False)
    water = models.BooleanField(default=False)
    hazmat = models.BooleanField(default=False)
    additional = models.TextField(blank=True, null=True)


class Aerial(Engine):
    aerial_height = models.PositiveIntegerField()


class Brush(Engine):
    additional = models.TextField(blank=True, null=True)


class OffRoad(Apparatus):
    additional = models.TextField(blank=True, null=True)


class Boat(Apparatus):
    additional = models.TextField(blank=True, null=True)


class FireCar(Apparatus):
    chief = models.BooleanField(default=False)


class MedCar(Apparatus):
    support_level = models.CharField(choices=MED_SUPPORT_LEVEL, max_length=100, default="Unknown"),


class Ambulance(Apparatus):
    ambulance_type = models.CharField(choices=AMBULANCE_TYPE, max_length=100, default="Unknown")
    support_level = models.CharField(choices=MED_SUPPORT_LEVEL, max_length=100, default="Unknown"),


class Special(Apparatus):
    specialty = models.CharField(max_length=512)
    additional = models.TextField(blank=True, null=True)


class Helicopter(Apparatus):
    standby_location = models.ForeignKey(FixedLocation)
    callsign = models.CharField(max_length=256)
    additional = models.TextField(blank=True, null=True)



