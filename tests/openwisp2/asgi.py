from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import openwisp_network_topology.routing

application = ProtocolTypeRouter(
    {
        'websocket': AuthMiddlewareStack(
            URLRouter(openwisp_network_topology.routing.websocket_urlpatterns)
        ),
    }
)
