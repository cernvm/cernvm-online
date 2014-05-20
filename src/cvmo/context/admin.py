from . import models
from django.contrib import admin


class ContextDefinitionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "public", "owner")
admin.site.register(models.ContextDefinition, ContextDefinitionAdmin)


class ContextStorageAdmin(admin.ModelAdmin):
    list_display = ["id"]
admin.site.register(models.ContextStorage, ContextStorageAdmin)
