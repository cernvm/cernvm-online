import re
import uuid
import base64
import pickle
from django.db import models
from django.contrib.auth.models import User
from cvmo.core.utils import crypt


class ContextDefinition(models.Model):
    #
    # Errors
    #

    class EncryptionError(Exception):
        pass

    class FormatError(Exception):
        pass

    #
    # Fields
    #

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

    #
    # Actions
    #

    def delete(self, using=None):
        # Remove storage
        try:
            cs = ContextStorage.objects.get(id=self.id)
            cs.delete()
        except:
            pass

        # Remove base
        models.Model.delete(self, using=using)

    #
    # Encryption
    #

    def encrypt(self, key):
        if not self.is_encrypted:
            return False

        self.data = base64.b64encode(
            crypt.encrypt(self.data, key)
        )

        return True

    def decrypt(self, key):
        if not self.is_encrypted:
            return False

        self.data = base64.b64encode(
            crypt.decrypt(self.data, key)
        )

        return True

    #
    # Accessors
    #

    @staticmethod
    def generate_new_id():
        return uuid.uuid4().hex

    @property
    def is_encrypted(self):
        try:
            d = pickle.loads(str(self.data))
            return False
        except:
            return True

    @property
    def values(self):
        if self.is_encrypted:
            raise ContextDefinition.EncryptionError("The context is encrypted")
        d = pickle.loads(self.data)
        return d["values"]

    @property
    def enabled_plugins(self):
        if self.is_encrypted:
            raise ContextDefinition.EncryptionError("The context is encrypted")
        d = pickle.loads(self.data)
        return d["enabled"]

    #
    # String representation
    #

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ContextStorage(models.Model):
    #
    # Errors
    #

    class EncryptionError(Exception):
        pass

    class FormatError(Exception):
        pass

    #
    # Fields
    #

    id = models.CharField(max_length=64, primary_key=True)
    data = models.TextField()

    #
    # Constructor
    #

    @staticmethod
    def create(uuid, name, ec2_user_data, root_pub_key=None):
        data = """VM_CONTEXT_UUID=%s
VM_CONTEXT_NAME="%s"
EC2_USER_DATA=%s""" % (uuid, name, base64.b64encode(ec2_user_data))
        if root_pub_key:
            data += "\nROOT_PUBKEY=%s" % base64.b64encode(root_pub_key)
        return ContextStorage(
            id=uuid,
            data=data
        )

    #
    # Encryption
    #

    def encrypt(self, key):
        if not self.is_encrypted:
            return False

        self.data = "ENCRYPTED:" + base64.b64encode( crypt.encrypt(self.data, key) )

        return True

    def decrypt(self, key):
        if not self.is_encrypted:
            return False

        g = re.match(r"^ENCRYPTED:(.*)$", self.data)
        if g:
            # Warning: it does not check for password correctness!!!
            self.data = crypt.decrypt( base64.b64decode(str(g.group(1))), key )
        else:
            raise FormatError('Malformed encrypted data!')

        return True

    #
    # Accessors
    #

    @property
    def is_encrypted(self):
        g = re.match(r"^ENCRYPTED:(.*)$", self.data)
        return (g is not None)

    @property
    def root_ssh_key(self):
        if self.is_encrypted:
            raise ContextStorage.EncryptionError("The context is encrypted")
        r = re.search(r"^\s*ROOT_PUBKEY\s*=\s*([^\s]*)\s*$", self.data, re.M)
        if not r:
            return None
        return base64.b64decode(r.group(1))

    @property
    def ec2_user_data(self):
        if self.is_encrypted:
            raise ContextStorage.EncryptionError("The context is encrypted")
        r = re.search(r"^\s*EC2_USER_DATA\s*=\s*([^\s]*)$", self.data, re.M)
        if not r:
            raise ContextStorage.FormatError("Unable to find `EC2_USER_DATA`")
        return base64.b64decode(r.group(1))

    @property
    def context_uuid(self):
        if self.is_encrypted:
            raise ContextStorage.EncryptionError("The context is encrypted")
        r = re.search(
            r"^\s*VM_CONTEXT_UUID\s*=\s*([^\s]*)\s*$", self.data, re.M
        )
        if not r:
            raise ContextStorage.FormatError(
                "Unable to find `VM_CONTEXT_UUID`"
            )
        return r.group(1)

    @property
    def context_name(self):
        if self.is_encrypted:
            return ContextStorage.EncryptionError("The context is encrypted")
        r = re.search(
            r"^\s*VM_CONTEXT_NAME\s*=\s*\"([^\"]*)\"\s*$", self.data, re.M
        )
        if not r:
            return ContextStorage.FormatError(
                "Unable to find `VM_CONTEXT_NAME`"
            )
        return r.group(1)

    #
    # String representation
    #

    def __str__(self):
        return self.id

    def __unicode__(self):
        return self.id
