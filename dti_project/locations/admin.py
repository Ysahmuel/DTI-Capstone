from django.contrib import admin
from .models import Region, Province, CityMunicipality, Barangay

admin.site.register(Region)
admin.site.register(Province)
admin.site.register(CityMunicipality)
admin.site.register(Barangay)
