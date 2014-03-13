from . import models
from django.contrib import admin


class ClaimRequestsAdmin(admin.ModelAdmin):
    list_display = ("pin", "status", "alloc_date", "machine")
admin.site.register(models.ClaimRequests, ClaimRequestsAdmin)


class ContextDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "public", "owner")
admin.site.register(models.ContextDefinition, ContextDefinitionAdmin)


class MachinesAdmin(admin.ModelAdmin):
    list_display = ("uuid", "ip", "owner")
admin.site.register(models.Machines, MachinesAdmin)


class ContextStorageAdmin(admin.ModelAdmin):
    list_display = ["id"]
admin.site.register(models.ContextStorage, ContextStorageAdmin)
