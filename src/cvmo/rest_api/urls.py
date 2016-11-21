from django.conf.urls import url

from .views import ClusterCreate, ClusterDetail, ClusterKeyValueCreate, ClusterKeyValueDetail
from .models import CLUSTER_PIN_LENGTH, CLUSTER_PIN_ALLOWED_CHARS

app_name = 'api-rest'
urlpatterns = [
    url(r'^clusters$', ClusterCreate.as_view(), name='cluster-create'),
    # Match clusters/<cluster_pin>
    url(r'^clusters/(?P<pin>[%s]{%d})$' % (CLUSTER_PIN_ALLOWED_CHARS, CLUSTER_PIN_LENGTH),
        ClusterDetail.as_view(), name='cluster-detail'),
    # Match clusters/<cluster_pin>/keys
    url(r'^clusters/(?P<pin>[%s]{%d})/keys$' % (CLUSTER_PIN_ALLOWED_CHARS, CLUSTER_PIN_LENGTH),
        ClusterKeyValueCreate.as_view(), name='cluster-key-value-create'),
    # Match clusters/<cluster_pin>/keys/<key>
    url(r'^clusters/(?P<pin>[%s]{%d})/keys/(?P<key>[a-zA-Z0-9_-]+)$' % (CLUSTER_PIN_ALLOWED_CHARS, CLUSTER_PIN_LENGTH),
        ClusterKeyValueDetail.as_view(), name='cluster-key-value-detail')
]
