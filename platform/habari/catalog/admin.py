from django.contrib import admin
from .models import *

admin.site.register(Organization)
admin.site.register(DataSource)
admin.site.register(Dhis2DataElement)
admin.site.register(Dhis2Indicator)
