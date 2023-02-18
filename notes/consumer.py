from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class ReminderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the WebSocket group based on the user's ID
        await self.channel_layer.group_add(f"user_{self.scope['user'].id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(f"user_{self.scope['user'].id}", self.channel_name)

    async def receive(self, text_data):
        # Not used for this example
        pass

    async def show_reminder(self, event):
        # Sleep for the specified delay and then send a "show_notification" message to the user's browser
        await asyncio.sleep(event["delay"])
        await self.send(text_data=json.dumps({"type": "show_notification", "message": event["message"]}))
