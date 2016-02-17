from django.contrib import admin
from apps.map.models import *


class MetaInline(admin.StackedInline):
    model = IncidentMeta
    fk_name = "incident"


class IncidentAdmin(admin.ModelAdmin):
    inlines = [MetaInline]

admin.site.register(Incident, IncidentAdmin)
