from django.db import models
from django.contrib.auth.models import User


class ContextDefinition(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    key = models.CharField(max_length=100, blank=True)
    checksum = models.CharField(max_length=40)
    public = models.BooleanField(verbose_name="Visible on public lists")
    inherited = models.BooleanField(default=False)
    abstract = models.BooleanField(default=False)
    from_abstract = models.BooleanField(default=False)
    # No foreign key for now: deleting a parent abstract will delete all the
    # descendants
    # parent = models.ForeignKey("self", null=True, default=None)
    data = models.TextField()

    def delete(self, using=None):
        # Remove storage
        try:
            cs = ContextStorage.objects.get(id=self.id)
            cs.delete()
        except:
            pass

        # Remove base
        models.Model.delete(self, using=using)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ContextStorage(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    data = models.TextField()

    def __str__(self):
        return self.id

    def __unicode__(self):
        return self.id

#
# Pairing related models
#


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
