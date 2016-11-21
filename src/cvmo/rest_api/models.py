from django.db import models, IntegrityError
from django.utils.crypto import get_random_string

CLUSTER_PIN_LENGTH = 12
CLUSTER_PIN_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyz1234567890"


class Cluster(models.Model):
    """ Collection of information about one cluster """

    # Creates db_index by default; it's not blank, our save method ensures it's filled
    pin = models.CharField(max_length=12, blank=True, unique=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """ Overridden method to get an unique pin """

        if not self.pin:
            self.pin = get_random_string(length=CLUSTER_PIN_LENGTH, allowed_chars=CLUSTER_PIN_ALLOWED_CHARS)
        failures = 5
        while True:
            try:
                super(Cluster, self).save(*args, **kwargs)
            except IntegrityError:  # pin already exists
                failures += 1
                if failures > 5:  # give up after several attempts
                    raise
                self.pin = get_random_string(length=CLUSTER_PIN_LENGTH, allowed_chars=CLUSTER_PIN_ALLOWED_CHARS)
            else:
                break  # successfully saved

    def __str__(self):
        return "pin: %s" % self.pin


#TODO check key only for valid values: [0-9a-zA-Z_-]+
class ClusterKeyValue(models.Model):
    """ Key-value element for a Cluster """

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE, related_name='key_value_elements')
    key = models.CharField(max_length=100, blank=False)
    value = models.CharField(max_length=1000, blank=False)

    def __str__(self):
        return "%s: %s" % (self.key, self.value)
