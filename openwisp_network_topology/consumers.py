import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ValidationError
from swapper import load_model

from . import settings as app_settings

Topology = load_model("topology", "Topology")


class TopologyConsumer(WebsocketConsumer):
    channel_layer_group = "topology"

    def _is_user_authorized_to_view_topology(self, user, topology_pk):
        try:
            topology = Topology.objects.get(pk=topology_pk)
        except (Topology.DoesNotExist, ValidationError):
            return False
        if not app_settings.TOPOLOGY_API_AUTH_REQUIRED:
            return True
        return user.is_superuser or (
            user.is_authenticated
            and user.is_manager(topology.organization_id)
            and user.has_perm(f"{Topology._meta.app_label}.view_topology")
        )

    def connect(self):
        user, topology_pk = self.scope.get("user"), self.scope.get("url_route").get(
            "kwargs"
        ).get("pk")
        if self._is_user_authorized_to_view_topology(user, topology_pk):
            async_to_sync(self.channel_layer.group_add)(
                f"{self.channel_layer_group}-{topology_pk}", self.channel_name
            )
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        self.close()

    def send_topology_update(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "type": "broadcast_topology",
                    "topology": event["data"],
                }
            )
        )
