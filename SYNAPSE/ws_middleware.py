"""
WebSocket JWT middleware — reads ?token=<jwt> from handshake URL.
"""
import jwt
import logging
from urllib.parse import parse_qs
from django.conf import settings
from channels.db import database_sync_to_async

logger = logging.getLogger(__name__)


class SimpleUser:
    def __init__(self, user_id: str, email: str = ''):
        self.id = user_id
        self.email = email
        self.is_authenticated = True


class AnonUser:
    id = None
    email = ''
    is_authenticated = False


class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        scope['user'] = await self._auth(scope)
        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def _auth(self, scope):
        params = parse_qs(scope.get('query_string', b'').decode())
        tokens = params.get('token', [])
        if not tokens:
            return AnonUser()
        try:
            payload = jwt.decode(
                tokens[0], settings.JWT_SECRET,
                algorithms=['HS256'],
                options={'verify_aud': False},
            )
            uid = payload.get('sub') or payload.get('id', '')
            return SimpleUser(uid, payload.get('email', ''))
        except jwt.InvalidTokenError as e:
            logger.warning('WS auth failed: %s', e)
            return AnonUser()
