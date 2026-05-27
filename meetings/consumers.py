"""
MeetingConsumer — real-time events inside a live meeting room.

Client → server event types:
  reaction        Emoji (broadcast to all)
  hand_raise      { raised: bool }
  media_status    { muted: bool, camera_off: bool }
  chat_message    { text: str }
  moderation      { action: "mute"|"remove", target_user_id: str }

Server → client envelope:
  { type, payload, user_id, user_name }
"""
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class MeetingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.group = f'meeting_{self.meeting_id}'
        self.user = self.scope.get('user')
        if not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001)
            return
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self._broadcast('participant_joined', {'user_id': str(self.user.id)})
        logger.info('Meeting %s: %s joined', self.meeting_id, self.user.id)

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self._broadcast('participant_left', {'user_id': str(self.user.id)})
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return
        handlers = {
            'reaction':     self._reaction,
            'hand_raise':   self._hand_raise,
            'media_status': self._media_status,
            'chat_message': self._chat,
            'moderation':   self._moderation,
        }
        fn = handlers.get(data.get('type', ''))
        if fn:
            await fn(data.get('payload', {}))

    async def _reaction(self, p):
        await self._broadcast('reaction', {
            'emoji': p.get('emoji', '👍'),
            'x': p.get('x', 50), 'y': p.get('y', 50),
        })

    async def _hand_raise(self, p):
        await self._broadcast('hand_raise', {'raised': bool(p.get('raised', True))})

    async def _media_status(self, p):
        await self._broadcast('media_status', {
            'muted': bool(p.get('muted', False)),
            'camera_off': bool(p.get('camera_off', False)),
        })

    async def _chat(self, p):
        text = str(p.get('text', '')).strip()
        if text:
            await self._broadcast('chat_message', {'text': text})

    async def _moderation(self, p):
        action = p.get('action')
        if action in ('mute', 'remove'):
            await self._broadcast('moderation', {
                'action': action,
                'target_user_id': p.get('target_user_id', ''),
            })

    async def meeting_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'],
            'payload': event['payload'],
            'user_id': event['user_id'],
            'user_name': event.get('user_name', ''),
        }))

    async def _broadcast(self, event_type, payload):
        await self.channel_layer.group_send(self.group, {
            'type': 'meeting_event',
            'event': event_type,
            'payload': payload,
            'user_id': str(self.user.id),
            'user_name': self.user.email,
        })
