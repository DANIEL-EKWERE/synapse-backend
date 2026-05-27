from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Webinar, WebinarRegistration, WebinarPoll, WebinarQuestion, WebinarChatMessage
from .serializers import (
    WebinarSerializer, WebinarRegistrationSerializer,
    WebinarPollSerializer, WebinarQuestionSerializer, WebinarChatMessageSerializer,
)


class WebinarListCreateView(generics.ListCreateAPIView):
    serializer_class = WebinarSerializer
    queryset = Webinar.objects.all()

    def perform_create(self, serializer):
        import uuid
        room_name = f"webinar-{uuid.uuid4().hex[:12]}"
        serializer.save(host_id=self.request.user.id, livekit_room_name=room_name)


class WebinarDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WebinarSerializer
    queryset = Webinar.objects.all()


class WebinarRegisterView(APIView):
    def post(self, request, pk):
        webinar = Webinar.objects.get(pk=pk)
        registration, created = WebinarRegistration.objects.get_or_create(
            webinar=webinar,
            user_id=request.user.id,
            defaults={'payment_status': 'completed' if not webinar.is_paid else 'pending'},
        )
        return Response(WebinarRegistrationSerializer(registration).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class WebinarQuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = WebinarQuestionSerializer

    def get_queryset(self):
        return WebinarQuestion.objects.filter(webinar_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(webinar_id=self.kwargs['pk'], user_id=self.request.user.id)


class WebinarPollListCreateView(generics.ListCreateAPIView):
    serializer_class = WebinarPollSerializer

    def get_queryset(self):
        return WebinarPoll.objects.filter(webinar_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(webinar_id=self.kwargs['pk'])
