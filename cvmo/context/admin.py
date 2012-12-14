import cvmo.context.models
from django.contrib import admin

#admin.site.register(cvmo.context.models.AmiconfigPlugin,    AmiconfigPluginAdmin)
#admin.site.register(cvmo.context.models.AmiconfigParameter)
#admin.site.register(cvmo.context.models.ContextDefinition)
#admin.site.register(cvmo.context.models.ClusterDefinition)
#admin.site.register(cvmo.context.models.ClusterContexts)
#admin.site.register(cvmo.context.models.Values)

class ClaimRequestsAdmin(admin.ModelAdmin):
    list_display = ('pin', 'status', 'alloc_date', 'machine')

class ContextDefinitionAdmin(admin.ModelAdmin):
    list_display = ('id','name','public','owner')

class MachinesAdmin(admin.ModelAdmin):
    list_display = ('uuid','ip','owner')

class ContextStorageAdmin(admin.ModelAdmin):
    list_display = [ 'id' ]

admin.site.register(cvmo.context.models.ClaimRequests, ClaimRequestsAdmin)
admin.site.register(cvmo.context.models.Machines, MachinesAdmin)
admin.site.register(cvmo.context.models.ContextDefinition, ContextDefinitionAdmin)
admin.site.register(cvmo.context.models.ContextStorage, ContextStorageAdmin)
admin.site.register(cvmo.context.models.ClusterDefinition)

# Cluster admin pages
admin.site.register(cvmo.context.models.ServiceOffering)
admin.site.register(cvmo.context.models.DiskOffering)
admin.site.register(cvmo.context.models.NetworkOffering)
admin.site.register(cvmo.context.models.Template)
admin.site.register(cvmo.context.models.ServiceDefinition)

admin.site.register(cvmo.context.models.MarketplaceGroup)
admin.site.register(cvmo.context.models.MarketplaceEntry)
