from rest_framework import serializers

from .models import Cluster, ClusterKeyValue


class ClusterSerializer(serializers.ModelSerializer):
    """ Serializer for the Cluster model class """

    class Meta:
        model = Cluster
        fields = ('pin', 'creation_time')


class ClusterKeyValueSerializer(serializers.ModelSerializer):
    """ Serializer for the ClusterKeyValue model class"""

    class Meta:
        model = ClusterKeyValue
        fields = ('key', 'value')

    def create(self, validated_data):
        cluster_pin = validated_data.pop('cluster_pin', None)
        cluster = Cluster.objects.get(pin=cluster_pin)
        keyValue = ClusterKeyValue.objects.create(cluster=cluster, **validated_data)

        return keyValue
