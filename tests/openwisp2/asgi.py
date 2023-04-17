from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from openwisp_controller.routing import get_routes as get_controller_routes

import openwisp_network_topology.routing

application = ProtocolTypeRouter(
    {
        'websocket': AuthMiddlewareStack(
            URLRouter(
                openwisp_network_topology.routing.websocket_urlpatterns
                + get_controller_routes()
            )
        ),
    }
)
