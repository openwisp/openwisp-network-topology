from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # For topology admin view
    re_path(
        r'^admin/topology/topology/(?P<pk>[^/]+)/change/$',
        consumers.TopologyConsumer.as_asgi(),
    ),
    # For topology non admin view
    re_path(
        r'^topology/topology/(?P<pk>[^/]+)/$', consumers.TopologyConsumer.as_asgi()
    ),
]
