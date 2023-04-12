import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from swapper import load_model

Topology = load_model('topology', 'Topology')


class TopologyConsumer(WebsocketConsumer):
    channel_layer_group = 'topology'

    def _is_user_authorized_to_view_topology(self, user, topology_pk):
        if user.is_authenticated and user.is_superuser:
            return True
        topology = Topology.objects.get(pk=topology_pk)
        return (
            user.is_authenticated
            and user.has_perm(f'{Topology._meta.app_label}.view_topology')
            and user.is_manager(topology.organization.pk)
        )

    def connect(self):
        user, topology_pk = self.scope.get('user'), self.scope.get('url_route').get(
            'kwargs'
        ).get('pk')
        if self._is_user_authorized_to_view_topology(user, topology_pk):
            async_to_sync(self.channel_layer.group_add)(
                f"{self.channel_layer_group}-{topology_pk}", self.channel_name
            )
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        self.close()
        pass

    def send_topology_update(self, event):
        self.send(
            text_data=json.dumps(
                {
                    'type': "broadcast_topology",
                    'topology': event['data'],
                }
            )
        )
