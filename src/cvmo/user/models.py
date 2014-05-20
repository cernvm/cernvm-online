from django.db import models
from django.contrib.auth.models import User


class UserActivationKey(models.Model):
    user = models.OneToOneField(User)
    key = models.CharField(max_length=150)
    created_on = models.DateTimeField(auto_now_add=True)
