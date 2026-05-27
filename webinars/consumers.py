"""WebinarConsumer — Q&A, polls, chat, reactions, host controls."""
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class WebinarConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.webinar_id = self.scope['url_route']['kwargs']['webinar_id']
        self.group = f'webinar_{self.webinar_id}'
        self.user = self.scope.get('user')
        if not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001); return
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()
        await self._broadcast('attendee_delta', {'delta': 1})

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self._broadcast('attendee_delta', {'delta': -1})
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data):
        try: data = json.loads(text_data)
        except: return
        handlers = {
            'chat_message':    self._chat,
            'question_submit': self._question_submit,
            'question_upvote': self._question_upvote,
            'poll_vote':       self._poll_vote,
            'host_control':    self._host_control,
            'reaction':        self._reaction,
        }
        fn = handlers.get(data.get('type', ''))
        if fn: await fn(data.get('payload', {}))

    async def _chat(self, p):
        text = str(p.get('text', '')).strip()
        if text: await self._broadcast('chat_message', {'text': text})

    async def _question_submit(self, p):
        question = str(p.get('question', '')).strip()
        if not question: return
        qid = await self._save_question(question)
        await self._broadcast('question_submitted', {
            'id': str(qid), 'question': question, 'upvotes': 0, 'is_answered': False,
        })

    async def _question_upvote(self, p):
        qid = p.get('question_id', '')
        count = await self._upvote_question(qid)
        await self._broadcast('question_upvoted', {'question_id': qid, 'upvotes': count})

    async def _poll_vote(self, p):
        poll_id, option = p.get('poll_id', ''), p.get('option', '')
        results = await self._record_vote(poll_id, option)
        await self._broadcast('poll_results', {'poll_id': poll_id, 'results': results})

    async def _host_control(self, p):
        await self._broadcast('host_control', p)

    async def _reaction(self, p):
        await self._broadcast('reaction', {'emoji': p.get('emoji', '👍')})

    async def webinar_event(self, event):
        await self.send(text_data=json.dumps({
            'type': event['event'], 'payload': event['payload'],
            'user_id': event['user_id'], 'user_name': event.get('user_name', ''),
        }))

    async def _broadcast(self, event_type, payload):
        await self.channel_layer.group_send(self.group, {
            'type': 'webinar_event', 'event': event_type,
            'payload': payload, 'user_id': str(self.user.id), 'user_name': self.user.email,
        })

    @database_sync_to_async
    def _save_question(self, text):
        from webinars.models import WebinarQuestion
        return WebinarQuestion.objects.create(
            webinar_id=self.webinar_id, user_id=self.user.id, question=text
        ).id

    @database_sync_to_async
    def _upvote_question(self, qid):
        from webinars.models import WebinarQuestion
        from django.db.models import F
        WebinarQuestion.objects.filter(id=qid).update(upvotes=F('upvotes') + 1)
        return WebinarQuestion.objects.get(id=qid).upvotes

    @database_sync_to_async
    def _record_vote(self, poll_id, option):
        from webinars.models import WebinarPollResponse
        WebinarPollResponse.objects.get_or_create(
            poll_id=poll_id, user_id=self.user.id, defaults={'selected_option': option}
        )
        tally = {}
        for r in WebinarPollResponse.objects.filter(poll_id=poll_id):
            tally[r.selected_option] = tally.get(r.selected_option, 0) + 1
        return tally
