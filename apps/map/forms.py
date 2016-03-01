from django.forms import ModelForm
from apps.people.models import Account
from apps.map.models import UserLocation, FixedLocation, Structure


class FixedLocationForm(ModelForm):
    class Meta:
        model = FixedLocation
        fields = ('street_address', 'lat', 'lng')


class StructureForm(ModelForm):
    class Meta:
        model = Structure
        fields = '__all__'
