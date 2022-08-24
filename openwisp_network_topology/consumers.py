import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class TopologyConsumer(WebsocketConsumer):
    channel_layer_group = 'topology'

    def _is_user_authenticated(self):
        try:
            assert self.scope['user'].is_authenticated is True
        except (KeyError, AssertionError):
            self.close()
            return False
        else:
            return True

    def connect(self):
        try:
            assert self._is_user_authenticated()
            self.pk = self.scope['url_route']['kwargs']['pk']
        except (AssertionError, KeyError):
            self.close()
        else:
            async_to_sync(self.channel_layer.group_add)(
                f"{self.channel_layer_group}-{self.pk}", self.channel_name
            )
            self.accept()

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
