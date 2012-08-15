from django.db import models
from django.contrib.auth.models import User
import pprint

class ContextDefinition(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    key = models.CharField(max_length=100, blank=True)
    checksum = models.CharField(max_length=40)
    public = models.BooleanField(verbose_name='Visible on public lists')
    agent = models.BooleanField(verbose_name='Activate iAgent')
    inherited = models.BooleanField(default=False)
    data = models.TextField()
    
    def delete(self, using=None):                
        # Remove storage
        try:
            cs = ContextStorage.objects.get(id=self.id)
            cs.delete()
        except Exception as ex:
            pass
        
        # Remove base
        models.Model.delete(self, using=using)

    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name
    
class Machines(models.Model):
    """ Instantiated machines """

    MACHINE_STATUS = (
            ('P', 'Paired'),
            ('D', 'Discovered'),
            ('C', 'Cloud')
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
            ('C', 'Claimed'),
            ('E', 'Error'),
            ('P', 'Pairing'),
            ('U', 'Unclaimed'),
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

class ContextStorage(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    data = models.TextField()    

    def __str__(self):
        return self.id
    
    def __unicode__(self):
        return self.id

class ClusterDefinition(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)    
    cernvm_version = models.CharField(max_length=15)
    key = models.CharField(max_length=100, blank=True)
    public = models.BooleanField(verbose_name='Visible on public lists')
    agent = models.BooleanField(verbose_name='Activate iAgent')
    data = models.TextField()
    
    def delete(self, using=None):                
        # Delete the linked contexts
        cluster_instances = ClusterInstance.objects.filter(cluster=self)
        for cluster_instance in cluster_instances:
            cluster_instance.delete()
        
        # Delete base    
        models.Model.delete(self, using=using)

    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name

class ClusterInstance(models.Model):
    cluster = models.ForeignKey(ClusterDefinition)
    order = models.PositiveIntegerField()
    context = models.ForeignKey(ContextDefinition)
    from_amt = models.PositiveIntegerField()
    to_amt = models.PositiveIntegerField()    
    elastic = models.BooleanField()
    service_offering = models.CharField(max_length=100)
    
    def delete(self, using=None):
        # Delete base
        models.Model.delete(self, using=using)
        
        # Remove the context
        self.context.delete()

    def __str__(self):
        return '#' + self.context.name + ' (' + self.cluster.name + ')'
    
    def __unicode__(self):
        return '#' + self.context.name + ' (' + self.cluster.name + ')'

class UserActivationKey(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=150)
    created_on = models.DateTimeField(auto_now_add=True)

class ActionDefinition(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    script = models.TextField()
    
