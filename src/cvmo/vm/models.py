from django.db import models
from django.contrib.auth.models import User
from cvmo.context.models import ContextDefinition


class Machines(models.Model):

    """ Instantiated machines """

    MACHINE_STATUS = (
        ("P", "Paired"),
        ("D", "Discovered"),
        ("C", "Cloud")
    )

    uuid = models.CharField(max_length=64, primary_key=True)
    version = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    owner = models.ForeignKey(User)
    context = models.ForeignKey(ContextDefinition, blank=True, null=True)
    status = models.CharField(max_length=2, choices=MACHINE_STATUS)

    def __str__(self):
        return self.uuid

    def __unicode__(self):
        return self.uuid


class ClaimRequests(models.Model):

    """ Amiconfig plugin definition """

    CLAIM_STATUS = (
        ("C", "Claimed"),
        ("E", "Error"),
        ("P", "Pairing"),
        ("U", "Unclaimed"),
    )

    pin = models.CharField(max_length=6, primary_key=True)
    status = models.CharField(max_length=2, choices=CLAIM_STATUS)
    alloc_date = models.DateTimeField()
    machine = models.ForeignKey(Machines, blank=True, null=True)
    context = models.ForeignKey(ContextDefinition)
    requestby = models.ForeignKey(User)

    def __str__(self):
        return self.pin

    def __unicode__(self):
        return self.pin
