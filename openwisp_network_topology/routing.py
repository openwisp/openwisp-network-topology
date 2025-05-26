from django.urls import path

from . import consumers

websocket_urlpatterns = [
    # This route is used by both
    # the admin and non-admin topology view
    path(
        "ws/network-topology/topology/<uuid:pk>/",
        consumers.TopologyConsumer.as_asgi(),
    ),
]
