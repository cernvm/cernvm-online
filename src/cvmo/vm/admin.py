from . import models
from django.contrib import admin


class ClaimRequestsAdmin(admin.ModelAdmin):
    list_display = ("pin", "status", "alloc_date", "machine")
admin.site.register(models.ClaimRequests, ClaimRequestsAdmin)


class MachinesAdmin(admin.ModelAdmin):
    list_display = ("uuid", "ip", "owner")
admin.site.register(models.Machines, MachinesAdmin)
