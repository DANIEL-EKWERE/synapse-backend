import uuid
from rest_framework import generics
from .models import CoachingSession, CoachingAvailability
from .serializers import CoachingSessionSerializer, CoachingAvailabilitySerializer


class CoachingSessionListCreateView(generics.ListCreateAPIView):
    serializer_class = CoachingSessionSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return CoachingSession.objects.filter(coach_id=user_id) | CoachingSession.objects.filter(client_id=user_id)

    def perform_create(self, serializer):
        room_name = f"coaching-{uuid.uuid4().hex[:12]}"
        serializer.save(coach_id=self.request.user.id, livekit_room_name=room_name)


class CoachingSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CoachingSessionSerializer
    queryset = CoachingSession.objects.all()


class CoachingAvailabilityView(generics.ListCreateAPIView):
    serializer_class = CoachingAvailabilitySerializer

    def get_queryset(self):
        coach_id = self.kwargs.get('coach_id', self.request.user.id)
        return CoachingAvailability.objects.filter(coach_id=coach_id)

    def perform_create(self, serializer):
        serializer.save(coach_id=self.request.user.id)
