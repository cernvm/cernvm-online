from django.db import models
from django.contrib.auth.models import User
from cvmo.context.models import ContextDefinition


class ClusterDefinition(models.Model):
    uid = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(User)
    key = models.CharField(max_length=64, blank=True)
    public = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


class ServiceOffering(models.Model):
    uid = models.CharField(max_length=16, db_index=True, unique=True)
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class DiskOffering(models.Model):
    uid = models.CharField(max_length=16, db_index=True, unique=True)
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class NetworkOffering(models.Model):
    uid = models.CharField(max_length=16, db_index=True, unique=True)
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class Template(models.Model):
    uid = models.CharField(max_length=128, db_index=True, unique=True)
    name = models.CharField(max_length=250)

    def __unicode__(self):
        return self.name


class ServiceDefinition(models.Model):
    uid = models.CharField(max_length=128, db_index=True)
    name = models.CharField(max_length=250)
    cluster = models.ForeignKey(ClusterDefinition)
    service_offering = models.ForeignKey(ServiceOffering)
    disk_offering = models.ForeignKey(DiskOffering, null=True, blank=True)
    network_offering = models.ForeignKey(
        NetworkOffering, null=True, blank=True)
    template = models.ForeignKey(Template)
    context = models.ForeignKey(ContextDefinition)

    MACHINE_STATUS = (
        ("S", "Scalable"),
        ("F", "Fixed"),
    )
    service_type = models.CharField(max_length=2, choices=MACHINE_STATUS)

    order = models.IntegerField(null=True, blank=True)
    min_instances = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.cluster.uid + " service " + self.uid \
            + "(" + self.service_type + ")"
