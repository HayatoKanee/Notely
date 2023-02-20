import asyncio
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ReminderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the WebSocket group based on the user's ID
        print('connected')
        await self.channel_layer.group_add(f"user_{self.scope['user'].id}", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        print('disconnected')
        await self.channel_layer.group_discard(f"user_{self.scope['user'].id}", self.channel_name)

    async def receive(self, text_data):
        message = json.loads(text_data)
        print("received", message)
        # Schedule a reminder event
        if message["type"] == "schedule_reminder":
            await self.schedule_reminder(message)

    async def schedule_reminder(self, event):
        # Sleep for the specified delay and then send a "show_notification" message to the user's browser
        print('dealing')
        await asyncio.sleep(event["delay"])
        await self.channel_layer.group_send(
            f"user_{self.scope['user'].id}",
            {
                "type": "show_notification",
                "message": event["message"]
            }
        )

    async def show_notification(self, event):
        # Send a WebSocket message to the user's browser to show the reminder notification
        await self.send(text_data=json.dumps({"type": "show_notification", "message": event["message"]}))
