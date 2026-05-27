"""
DRF authentication: validates HS256 JWT from `Authorization: Bearer <token>`.
Works with any JWT provider (your own Django-issued tokens, Auth0, etc.)
Configure JWT_SECRET in .env.
"""
import jwt
import logging
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class SimpleUser:
    def __init__(self, user_id: str, email: str = ''):
        self.id = user_id
        self.email = email
        self.is_authenticated = True
        self.is_active = True

    def __str__(self):
        return self.email or str(self.id)


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return None
        token = auth[7:]
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET,
                algorithms=['HS256'],
                options={'verify_aud': False},
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {e}')
        user_id = payload.get('sub') or payload.get('id', '')
        return (SimpleUser(user_id, payload.get('email', '')), token)

    def authenticate_header(self, request):
        return 'Bearer'
