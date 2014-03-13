from . import models
from django.contrib import admin

admin.site.register(models.ClusterDefinition)
admin.site.register(models.ServiceOffering)
admin.site.register(models.DiskOffering)
admin.site.register(models.NetworkOffering)
admin.site.register(models.Template)
admin.site.register(models.ServiceDefinition)
