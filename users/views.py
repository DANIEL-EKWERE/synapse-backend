import jwt
import uuid
import datetime
from django.conf import settings
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth.models import User as DjangoUser
from .models import Profile
from .serializers import ProfileSerializer


def _make_token(user_id: str, email: str) -> str:
    payload = {
        'sub': str(user_id),
        'email': email,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm='HS256')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email     = request.data.get('email', '').strip().lower()
        password  = request.data.get('password', '')
        full_name = request.data.get('full_name', '').strip()

        if not email or not password:
            return Response({'detail': 'email and password required'}, status=400)
        if DjangoUser.objects.filter(username=email).exists():
            return Response({'detail': 'Email already registered'}, status=400)

        DjangoUser.objects.create_user(username=email, email=email, password=password)

        # Profile uses its own UUID, not the Django auth int PK
        profile_id = str(uuid.uuid4())
        Profile.objects.create(id=profile_id, email=email, full_name=full_name)
        token = _make_token(profile_id, email)
        return Response({'token': token}, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        dj_user  = authenticate(username=email, password=password)
        if not dj_user:
            return Response({'detail': 'Invalid credentials'}, status=401)

        profile = Profile.objects.filter(email=email).first()
        if not profile:
            profile = Profile.objects.create(id=str(uuid.uuid4()), email=email, full_name='')

        token = _make_token(str(profile.id), email)
        return Response({'token': token})


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        profile, _ = Profile.objects.get_or_create(
            id=self.request.user.id,
            defaults={'email': self.request.user.email, 'full_name': ''},
        )
        return profile


class ProfileListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()


class NotificationListView(APIView):
    def get(self, request):
        # Placeholder — returns empty list until Notification model is added
        return Response([])


class UnreadNotificationCountView(APIView):
    def get(self, request):
        return Response({'count': 0})


class MarkAllNotificationsReadView(APIView):
    def post(self, request):
        return Response({'status': 'ok'})
