from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometrySerializerMethodField
from rest_framework import serializers
from apps.map.models import Incident, IncidentMeta, FixedLocation, WeatherSnapshot


class FixedLocationGeoSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = FixedLocation
        geo_field = "point"

        fields = ('id', 'street_address', 'streetview_url')


class FixedLocationModelSerializer(serializers.ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = FixedLocation

        fields = ('id', 'street_address', 'lng', 'lat', 'streetview_url')


class WeatherSnapshotModelSerializer(serializers.ModelSerializer):
     class Meta:
         model = WeatherSnapshot

         fields = ('description', 'station', 'wind_speed', 'wind_heading', 'rain', 'clouds', 'temperature')


class IncidentMetaSerializer(serializers.ModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """
    street_address = serializers.SerializerMethodField()

    def get_street_address(self, obj):
        return obj.incident.location.street_address

    class Meta:
        model = IncidentMeta

        fields = ('id', 'location', 'street_address', 'venue', 'dispatch', 'intersection', 'unit', 'weather')


class IncidentGeoSerializer(GeoFeatureModelSerializer):
    """ A class to serialize locations as GeoJSON compatible data """
    point = GeometrySerializerMethodField()
    location = FixedLocationModelSerializer()
    meta = IncidentMetaSerializer()

    def get_point(self, obj):
        return obj.location.point

    class Meta:
        model = Incident
        geo_field = 'point'

        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        fields = ('id', 'location', 'meta', 'active', 'dispatch_time', 'received_time', 'created_time')


class IncidentSerializer(serializers.Serializer):
    """ A class to serialize locations as JSON compatible data """
    location = FixedLocationModelSerializer()
    meta = IncidentMetaSerializer()

    class Meta:
        model = Incident

        fields = ('id', 'location', 'meta', 'active', 'dispatch_time', 'received_time', 'created_time')
