from datetime import timedelta

from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils import timezone

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import APIException

from .models import Cluster, ClusterKeyValue
from .serializers import ClusterSerializer, ClusterKeyValueSerializer
from .renderers import ClusterKeyRenderer


class ClusterPairingPage(TemplateView):
    """ HTML page accessible from the menu, with cluster pairing point dialog. """

    template_name = "rest_api/cluster_pairing.html"


class Conflict(APIException):
    """ Exception class implementing HTTP 409 Conflict """

    status_code = 409
    default_detail = "Resource already exists, cannot be created again"
    default_code = 'conflict'


class ClusterCreate(generics.CreateAPIView):
    """ Create a new cluster """

    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

    def initial(self, request, *args, **kwargs):
        """ Check the expired pins before every request. """

        CheckPinExpiration()
        super(ClusterCreate, self).initial(request, *args, **kwargs)


class ClusterDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, update or destroy a cluster """

    lookup_field = 'pin'
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer

    def initial(self, request, *args, **kwargs):
        """ Check the expired pins before every request. """

        CheckPinExpiration()
        super(ClusterDetail, self).initial(request, *args, **kwargs)


class ClusterKeyValueCreate(generics.ListCreateAPIView):
    """ Create a new key-value element for a cluster """

    serializer_class = ClusterKeyValueSerializer

    def get_queryset(self):
        return ClusterKeyValue.objects.filter(cluster__pin=self.kwargs['pin'])

    def perform_create(self, serializer):
        try:
            # Check if we don't already have a key with the same name
            key = self.request.data['key']
            if (self.get_queryset().filter(key=key)).exists():
                raise Conflict

            serializer.save(cluster_pin=self.kwargs['pin'])
        except (ObjectDoesNotExist, KeyError):
            raise Http404

    def initial(self, request, *args, **kwargs):
        """ Check the expired pins before every request. """

        CheckPinExpiration()
        super(ClusterKeyValueCreate, self).initial(request, *args, **kwargs)


class ClusterKeyValueDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, update or destroy an element in a cluster """

    lookup_field = 'key'
    serializer_class = ClusterKeyValueSerializer
    # Return responses either in plaintext or JSON
    renderer_classes = (ClusterKeyRenderer, JSONRenderer)

    def get_queryset(self):
        # Filter objects with elements from the URL: <pin>, <key>
        return ClusterKeyValue.objects.filter(cluster__pin=self.kwargs['pin']).filter(key=self.kwargs['key'])

    def initial(self, request, *args, **kwargs):
        """ Check the expired pins before every request. """

        CheckPinExpiration()
        super(ClusterKeyValueDetail, self).initial(request, *args, **kwargs)


def CheckPinExpiration():
    """ Check for expired cluster pins and delete them if necessary.

    We don't query the DB on each call, but at most every 2 minutes.
    """

    # Initialize our static method variable
    if "lastCheck" not in CheckPinExpiration.__dict__:
        CheckPinExpiration.lastCheck = timezone.now() - timedelta(weeks=56)  # well in the past

    checkingInterval = timedelta(minutes=2)  # check every 2 mins for expired pins

    if CheckPinExpiration.lastCheck + checkingInterval > timezone.now():
        return  # too soon

    # Update last check time
    CheckPinExpiration.lastCheck = timezone.now()
    # Delete objects older than 1 day
    Cluster.objects.filter(creation_time__lt=timezone.now() - timedelta(days=1) ).delete()
