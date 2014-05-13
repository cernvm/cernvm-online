from django.db import models
from django.contrib.auth.models import User
from json_field import JSONField
from cvmo.context.models import ContextDefinition, ContextStorage


class ClusterDefinition(models.Model):

    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)

    # Owner of the cluster
    owner = models.ForeignKey(User)

    # Master / worker contexts
    master_context = models.ForeignKey(ContextDefinition,
                                       related_name="master_context")
    worker_context = models.ForeignKey(ContextDefinition,
                                       related_name="worker_context")

    # Deployable context
    deployable_context = models.ForeignKey(ContextStorage)

    # Settings
    data = models.TextField(null=False, blank=False, default='{}')
    encrypted = models.BooleanField(default=False)
    #ec2 = JSONField(null=False, blank=False)
    #quota = JSONField(null=False, blank=False)
    #elastiq = JSONField(null=False, blank=False)
    #additional_params = JSONField(null=False, blank=False, default={})
