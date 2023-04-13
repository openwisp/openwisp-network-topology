from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # This route is used by both
    # the admin and non-admin topology view
    re_path(
        r'^network-topology/topology/(?P<pk>[^/]+)/$',
        consumers.TopologyConsumer.as_asgi(),
    ),
]
