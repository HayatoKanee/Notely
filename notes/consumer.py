import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ReminderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the WebSocket group based on the user's ID
        await self.channel_layer.group_add(f"user_{self.scope['user'].id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(f"user_{self.scope['user'].id}", self.channel_name)

    async def show_notification(self, event):
        # Send a WebSocket message to the user's browser to show the reminder notification
        await self.send(json.dumps(event))


class CanvasConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(f"page_{self.scope['url_route']['kwargs']['page_id']}", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(f"page_{self.scope['url_route']['kwargs']['page_id']}",
                                               self.channel_name)

    async def receive(self, text_data):
        canvas = text_data
        group_name = f"page_{self.scope['url_route']['kwargs']['page_id']}"
        await self.channel_layer.group_send(group_name, {
            'type': 'update_canvas',
            'data': canvas
        })

    async def update_canvas(self, event):
        canvas = event['data']
        await self.send(canvas)
