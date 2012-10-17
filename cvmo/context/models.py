from django.db import models
from django.contrib.auth.models import User

##################################################
# Context related models
##################################################

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

class ContextStorage(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    data = models.TextField()    

    def __str__(self):
        return self.id
    
    def __unicode__(self):
        return self.id
        
##################################################
# Pairing related models
##################################################
    
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
    
##################################################
# Cluster related models
##################################################

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
    uid = models.CharField(max_length=16, db_index=True)
    cluster = models.ForeignKey(ClusterDefinition)    
    service_offering = models.ForeignKey(ServiceOffering)
    disk_offering = models.ForeignKey(DiskOffering, null = True, blank = True)
    network_offering = models.ForeignKey(NetworkOffering, null = True, blank = True)
    template = models.ForeignKey(Template)
    context = models.ForeignKey(ContextDefinition)

    MACHINE_STATUS = (
            ('S', 'Scalable'),
            ('F', 'Fixed'),
        )
    service_type = models.CharField(max_length=2, choices=MACHINE_STATUS)
    
    order = models.IntegerField(null = True, blank = True)
    min_instances = models.IntegerField(null = True, blank = True)
    
    def __unicode__(self):
        return self.cluster.uid + " service "  + self.uid + '('+ self.service_type +')'
    
##################################################
# User related models
##################################################

class UserActivationKey(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=150)
    created_on = models.DateTimeField(auto_now_add=True)
    
##################################################
# Deprecated models
##################################################

class ActionDefinition(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    owner = models.ForeignKey(User)
    script = models.TextField()
    
