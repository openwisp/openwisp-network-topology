from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r'^admin/topology/topology/(?P<pk>[^/]+)/change/$',
        consumers.TopologyConsumer.as_asgi(),
    )
]
