from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # This route is used by both
    # the admin and non-admin topology view
    re_path(
        r'^admin/topology/topology/(?P<pk>[^/]+)/change/$',
        consumers.TopologyConsumer.as_asgi(),
    ),
]
