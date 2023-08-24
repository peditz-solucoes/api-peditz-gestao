import datetime
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer

from uuid import UUID

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

        # is_occupied = await self.check_room_occupation(self.room_group_name)
        # if is_occupied:
        #     # Fecha a conexão se o room_name já estiver ocupado
        #     await self.close()
        #     return
        # await self.mark_room_as_occupied(self.room_group_name)
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
        await self.unmark_room_as_occupied(self.room_group_name)
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    @database_sync_to_async
    def check_room_occupation(self, room_name):
        channel_layer = get_channel_layer()
        is_occupied = channel_layer.group_channels(room_name)
        return len(is_occupied) > 0

    @database_sync_to_async
    def mark_room_as_occupied(self, room_name):
        # Neste exemplo, apenas a existência de um canal no grupo já marca o room_name como ocupado
        pass

    @database_sync_to_async
    def unmark_room_as_occupied(self, room_name):
        # Neste exemplo, removemos o canal do grupo quando o cliente se desconecta
        pass


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
