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
