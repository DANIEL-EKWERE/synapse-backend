"""ClassroomConsumer — attendance, hand-raise, quiz, teacher broadcast."""
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class ClassroomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.classroom_id = self.scope['url_route']['kwargs']['classroom_id']
        self.group = f'classroom_{self.classroom_id}'
        self.user = self.scope.get('user')
        if not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001); return
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self._broadcast('student_joined', {'user_id': str(self.user.id)})

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self._broadcast('student_left', {'user_id': str(self.user.id)})
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        try: data = json.loads(text_data)
        except: return
        handlers = {
            'hand_raise':        self._hand_raise,
            'attendance_mark':   self._attendance,
            'quiz_answer':       self._quiz,
            'teacher_broadcast': self._broadcast_msg,
            'chat_message':      self._chat,
            'assignment_notify': self._assignment_notify,
        }
        fn = handlers.get(data.get('type', ''))
        if fn: await fn(data.get('payload', {}))

    async def _hand_raise(self, p):
        await self._broadcast('hand_raise', {'raised': bool(p.get('raised', True))})

    async def _attendance(self, p):
        sid, present = p.get('student_id', ''), bool(p.get('is_present', True))
        await self._save_attendance(sid, present)
        await self._broadcast('attendance_updated', {'student_id': sid, 'is_present': present})

    async def _quiz(self, p):
        await self._broadcast('quiz_answer', {
            'question_id': p.get('question_id', ''), 'answer': p.get('answer', ''),
        })

    async def _broadcast_msg(self, p):
        await self._broadcast('teacher_broadcast', {'text': str(p.get('text', '')).strip()})

    async def _chat(self, p):
        text = str(p.get('text', '')).strip()
        if text: await self._broadcast('chat_message', {'text': text})

    async def _assignment_notify(self, p):
        await self._broadcast('assignment_notify', {
            'assignment_id': p.get('assignment_id', ''),
            'title': p.get('title', ''),
            'action': p.get('action', 'created'),
        })

    async def classroom_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'], 'payload': event['payload'],
            'user_id': event['user_id'], 'user_name': event.get('user_name', ''),
        }))

    async def _broadcast(self, event_type, payload):
        await self.channel_layer.group_send(self.group, {
            'type': 'classroom_event', 'event': event_type,
            'payload': payload, 'user_id': str(self.user.id), 'user_name': self.user.email,
        })

    @database_sync_to_async
    def _save_attendance(self, student_id, is_present):
        from classrooms.models import Attendance
        from django.utils import timezone
        Attendance.objects.update_or_create(
            classroom_id=self.classroom_id, student_id=student_id,
            session_date=timezone.now().date(), defaults={'is_present': is_present},
        )
