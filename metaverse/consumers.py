"""
MetaverseConsumer — real-time 2D avatar movement inside a Space.

WebSocket URL: ws://<host>/ws/metaverse/<space_id>/?token=<jwt>

Client → server:
  { "type": "move", "payload": { "x": int, "y": int } }

Server → client:
  { "type": "space-joined",    "payload": { "spawn": {x,y}, "userId", "name", "users": [...] } }
  { "type": "user-joined",     "payload": { "userId", "name", "x", "y" } }
  { "type": "movement",        "payload": { "userId", "x", "y" } }
  { "type": "movement-rejected","payload": { "x", "y" } }
  { "type": "user-left",       "payload": { "userId" } }
"""
import json
import logging
import random
import threading

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Space

logger = logging.getLogger(__name__)

_lock = threading.Lock()
# { space_id: { channel_name: { user_id, name, x, y } } }
_rooms: dict[str, dict[str, dict]] = {}


class MetaverseConsumer(AsyncWebsocketConsumer):

    # ── connect ────────────────────────────────────────────────────────────────

    async def connect(self):
        self.space_id = self.scope['url_route']['kwargs']['space_id']
        self.group    = f'metaverse_{self.space_id}'
        self.user     = self.scope.get('user')

        if not getattr(self.user, 'is_authenticated', False):
            await self.close(code=4001)
            return

        self.user_id   = str(self.user.id)
        self.user_name = getattr(self.user, 'email', self.user_id)

        try:
            space = await sync_to_async(Space.objects.get)(id=self.space_id)
        except Space.DoesNotExist:
            await self.close(code=4004)
            return

        self.x = random.randint(0, max(0, space.width  - 1))
        self.y = random.randint(0, max(0, space.height - 1))

        with _lock:
            if self.space_id not in _rooms:
                _rooms[self.space_id] = {}
            _rooms[self.space_id][self.channel_name] = {
                'user_id': self.user_id,
                'name':    self.user_name,
                'x':       self.x,
                'y':       self.y,
            }
            other_users = [
                v for k, v in _rooms[self.space_id].items()
                if k != self.channel_name
            ]

        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Tell this user about the space and everyone already in it
        await self.send(text_data=json.dumps({
            'type': 'space-joined',
            'payload': {
                'spawn':  {'x': self.x, 'y': self.y},
                'userId': self.user_id,
                'name':   self.user_name,
                'users': [
                    {'userId': u['user_id'], 'name': u['name'], 'x': u['x'], 'y': u['y']}
                    for u in other_users
                ],
            },
        }))

        # Tell everyone else that this user joined
        await self.channel_layer.group_send(self.group, {
            'type': 'metaverse_event',
            'data': {
                'type': 'user-joined',
                'payload': {
                    'userId': self.user_id,
                    'name':   self.user_name,
                    'x':      self.x,
                    'y':      self.y,
                },
            },
            'exclude': self.channel_name,
        })
        logger.info('Metaverse %s: %s joined at (%d,%d)', self.space_id, self.user_id, self.x, self.y)

    # ── disconnect ─────────────────────────────────────────────────────────────

    async def disconnect(self, code):
        if not hasattr(self, 'group'):
            return

        with _lock:
            room = _rooms.get(self.space_id, {})
            room.pop(self.channel_name, None)
            if not room:
                _rooms.pop(self.space_id, None)

        await self.channel_layer.group_send(self.group, {
            'type': 'metaverse_event',
            'data': {
                'type':    'user-left',
                'payload': {'userId': self.user_id},
            },
            'exclude': self.channel_name,
        })
        await self.channel_layer.group_discard(self.group, self.channel_name)

    # ── receive ────────────────────────────────────────────────────────────────

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return

        if data.get('type') != 'move':
            return

        try:
            new_x = int(data['payload']['x'])
            new_y = int(data['payload']['y'])
        except (KeyError, ValueError, TypeError):
            return

        dx = abs(self.x - new_x)
        dy = abs(self.y - new_y)
        valid = (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

        if valid:
            self.x = new_x
            self.y = new_y
            with _lock:
                room = _rooms.get(self.space_id, {})
                if self.channel_name in room:
                    room[self.channel_name].update({'x': self.x, 'y': self.y})

            await self.channel_layer.group_send(self.group, {
                'type': 'metaverse_event',
                'data': {
                    'type':    'movement',
                    'payload': {'userId': self.user_id, 'x': self.x, 'y': self.y},
                },
                'exclude': None,  # broadcast to everyone including sender
            })
        else:
            await self.send(text_data=json.dumps({
                'type':    'movement-rejected',
                'payload': {'x': self.x, 'y': self.y},
            }))

    # ── channel-layer event handler ────────────────────────────────────────────

    async def metaverse_event(self, event):
        if event.get('exclude') == self.channel_name:
            return
        await self.send(text_data=json.dumps(event['data']))
