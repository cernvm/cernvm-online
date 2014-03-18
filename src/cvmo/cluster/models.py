from django.db import models
from django.contrib.auth.models import User
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
    ec2 = models.TextField(null=False, blank=False)
    quota = models.TextField(null=False, blank=False)
    elastiq = models.TextField(null=False, blank=False)
    additional_params = models.TextField(null=True, blank=True)
