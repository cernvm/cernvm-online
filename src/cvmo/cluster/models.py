from django.db import models
from django.contrib.auth.models import User
from json_field import JSONField
from cvmo.context.models import ContextDefinition, ContextStorage
import cvmo.core.utils.crypt as cvmo_crypt
import base64
import hashlib


class ClusterDefinition(models.Model):

    #id = models.CharField(max_length=64, primary_key=True)
    #id = models.AutoField(primary_key=True)

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
    #encrypted = models.BooleanField(default=False)
    #checksum = models.CharField(max_length=40, default=0)
    encryption_checksum = models.CharField(max_length=40, default=0)
    #ec2 = JSONField(null=False, blank=False)
    #quota = JSONField(null=False, blank=False)
    #elastiq = JSONField(null=False, blank=False)
    #additional_params = JSONField(null=False, blank=False, default={})

    class CryptographyError(Exception):
        pass

    def encrypt(self, key):
        pass

    def decrypt(self, passphrase):

        if not self.is_encrypted():
            # Not encrypted
            return False

        data_json_str = cvmo_crypt.decrypt( base64.b64decode(self.data), passphrase )
        verify_checksum = hashlib.sha1(data_json_str).hexdigest()

        if self.encryption_checksum != verify_checksum:
            raise self.CryptographyError('Wrong password')

        self.encryption_checksum = ''
        self.data = data_json_str

    def is_encrypted(self):
        return self.encryption_checksum != ''
