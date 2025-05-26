from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf import settings
from django.core.asgi import get_asgi_application

if "openwisp_controller.geo" in settings.INSTALLED_APPS:
    from openwisp_controller.routing import get_routes as get_controller_routes
else:
    from openwisp_notifications.websockets.routing import (
        get_routes as get_notification_routes,
    )

    from openwisp_controller.connection.channels.routing import (
        get_routes as get_connection_routes,
    )

    def get_controller_routes():
        return get_connection_routes() + get_notification_routes()


import openwisp_network_topology.routing

application = ProtocolTypeRouter(
    {
        "websocket": AuthMiddlewareStack(
            URLRouter(
                openwisp_network_topology.routing.websocket_urlpatterns
                + get_controller_routes()
            )
        ),
        "http": get_asgi_application(),
    }
)
