from django.db import models
from django.contrib.auth.models import User
from cvmo.context.models import ContextDefinition


class MarketplaceGroup(models.Model):
    name = models.CharField(max_length=150)

    def __unicode__(self):
        return self.name


class MarketplaceContextEntry(models.Model):
    details = models.TextField()
    context = models.ForeignKey(ContextDefinition)
    group = models.ForeignKey(MarketplaceGroup)
    icon = models.ImageField(upload_to="market/icons")
    tags = models.TextField()
    rank = models.IntegerField(default=0)

    def __unicode__(self):
        return self.context.name


class MarketplaceContextVotes(models.Model):
    entry = models.ForeignKey(MarketplaceContextEntry)
    user = models.ForeignKey(User)
    vote = models.IntegerField()


# class MarketplaceClusterEntry(models.Model):
#     details = models.TextField()
#     cluster = models.ForeignKey(ClusterDefinition)
#     group = models.ForeignKey(MarketplaceGroup)
#     icon = models.ImageField(upload_to="market/icons")
#     tags = models.TextField()
#     variables = models.TextField()
#     rank = models.IntegerField(default=0)

#     def __unicode__(self):
#         return self.context.name


# class MarketplaceClusterVotes(models.Model):
#     entry = models.ForeignKey(MarketplaceClusterEntry)
#     user = models.ForeignKey(User)
#     vote = models.IntegerField()
