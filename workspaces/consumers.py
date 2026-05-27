import json
from channels.generic.websocket import AsyncWebsocketConsumer


class WorkspaceConsumer(AsyncWebsocketConsumer):
    """Real-time channel messages and presence for a workspace."""

    async def connect(self):
        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.room_group = f'workspace_{self.workspace_id}'
        self.user = self.scope.get('user')

        if not self.user:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.channel_layer.group_send(self.room_group, {
            'type': 'presence_event',
            'event': 'user_joined',
            'user_id': str(self.user.id),
        })
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.room_group, {
            'type': 'presence_event',
            'event': 'user_left',
            'user_id': str(self.user.id),
        })
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.room_group, {
            'type': 'chat_message',
            'message': data.get('message'),
            'channel_id': data.get('channel_id'),
            'user_id': str(self.user.id),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'channel_id': event['channel_id'],
            'user_id': event['user_id'],
        }))

    async def presence_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'],
            'user_id': event['user_id'],
        }))
