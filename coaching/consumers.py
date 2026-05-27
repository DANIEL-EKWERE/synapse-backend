"""CoachingConsumer — session status, shared notes, timer sync, action items."""
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class CoachingConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group = f'coaching_{self.session_id}'
        self.user = self.scope.get('user')
        if not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001); return
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self._broadcast('participant_connected', {'user_id': str(self.user.id)})

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self._broadcast('participant_disconnected', {'user_id': str(self.user.id)})
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        try: data = json.loads(text_data)
        except: return
        handlers = {
            'session_status':  self._status,
            'note_update':     self._note,
            'timer_sync':      self._timer,
            'action_item_add': self._action_item,
            'chat_message':    self._chat,
        }
        fn = handlers.get(data.get('type', ''))
        if fn: await fn(data.get('payload', {}))

    async def _status(self, p):
        s = p.get('status', '')
        if s in ('live', 'completed', 'cancelled'):
            await self._update_status(s)
            await self._broadcast('session_status', {'status': s})

    async def _note(self, p):
        await self._broadcast('note_update', {'content': str(p.get('content', ''))})

    async def _timer(self, p):
        await self._broadcast('timer_sync', {'remaining_seconds': int(p.get('remaining_seconds', 0))})

    async def _action_item(self, p):
        text = str(p.get('text', '')).strip()
        if text:
            await self._append_action_item(text)
            await self._broadcast('action_item_added', {'text': text})

    async def _chat(self, p):
        text = str(p.get('text', '')).strip()
        if text: await self._broadcast('chat_message', {'text': text})

    async def coaching_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'], 'payload': event['payload'],
            'user_id': event['user_id'], 'user_name': event.get('user_name', ''),
        }))

    async def _broadcast(self, event_type, payload):
        await self.channel_layer.group_send(self.group, {
            'type': 'coaching_event', 'event': event_type,
            'payload': payload, 'user_id': str(self.user.id), 'user_name': self.user.email,
        })

    @database_sync_to_async
    def _update_status(self, status):
        from coaching.models import CoachingSession
        CoachingSession.objects.filter(id=self.session_id).update(status=status)

    @database_sync_to_async
    def _append_action_item(self, text):
        from coaching.models import CoachingSession
        s = CoachingSession.objects.get(id=self.session_id)
        s.notes = (s.notes or '') + f'\n[ ] {text}'
        s.save(update_fields=['notes'])
