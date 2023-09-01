import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer

from uuid import UUID
from django.core.cache import cache



class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return obj.hex
        return json.JSONEncoder.default(self, obj)

class PedidosConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'pedidos_%s' % self.room_name
        is_connected = cache.get(f"connected_{self.room_name}")
        if is_connected:
            await self.close()
            return

        cache.set(f"connected_{self.room_name}", 1)

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'att',
                'message': "Connected" + str(datetime.datetime.now()) + " " + str(self.room_group_name)
            }
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        cache.delete(f"connected_{self.room_name}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def att(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def order(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'order': message
        }))
