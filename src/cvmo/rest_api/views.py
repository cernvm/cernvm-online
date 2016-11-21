from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import APIException

from .models import Cluster, ClusterKeyValue
from .serializers import ClusterSerializer, ClusterKeyValueSerializer
from .renderers import ClusterKeyRenderer


class Conflict(APIException):
    """ Exception class implementing HTTP 409 Conflict """
    status_code = 409
    default_detail = "Resource already exists, cannot be created again"
    default_code = 'conflict'


class ClusterCreate(generics.CreateAPIView):
    """ Create a new cluster """

    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


class ClusterDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, update or destroy a cluster """

    lookup_field = 'pin'
    queryset = Cluster.objects.all()
    serializer_class = ClusterSerializer


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


class ClusterKeyValueDetail(generics.RetrieveUpdateDestroyAPIView):
    """ Retrieve, update or destroy an element in a cluster """

    lookup_field = 'key'
    serializer_class = ClusterKeyValueSerializer
    # Return responses either in plaintext or JSON
    renderer_classes = (ClusterKeyRenderer, JSONRenderer)

    def get_queryset(self):
        # Filter objects with elements from the URL: <pin>, <key>
        return ClusterKeyValue.objects.filter(cluster__pin=self.kwargs['pin']).filter(key=self.kwargs['key'])
