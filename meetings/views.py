from django.conf import settings
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Meeting, MeetingParticipant
from .serializers import MeetingSerializer, MeetingParticipantSerializer


class MeetingListCreateView(generics.ListCreateAPIView):
    serializer_class = MeetingSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        pids = MeetingParticipant.objects.filter(user_id=user_id).values_list('meeting_id', flat=True)
        return Meeting.objects.filter(id__in=pids).order_by('start_time')

    def perform_create(self, serializer):
        import uuid
        room_name = f"meeting-{uuid.uuid4().hex[:12]}"
        meeting = serializer.save(host_id=self.request.user.id, livekit_room_name=room_name)
        MeetingParticipant.objects.create(
            meeting=meeting, user_id=self.request.user.id,
            role='host', joined_at=timezone.now(),
        )


class MeetingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MeetingSerializer
    queryset = Meeting.objects.all()


class MeetingParticipantsView(generics.ListAPIView):
    serializer_class = MeetingParticipantSerializer

    def get_queryset(self):
        return MeetingParticipant.objects.filter(meeting_id=self.kwargs['pk'])


class MeetingJoinView(APIView):
    def post(self, request, pk):
        try:
            meeting = Meeting.objects.get(pk=pk)
        except Meeting.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        participant, created = MeetingParticipant.objects.get_or_create(
            meeting=meeting, user_id=request.user.id,
            defaults={'role': 'participant', 'joined_at': timezone.now()},
        )
        if not created:
            participant.joined_at = timezone.now()
            participant.left_at = None
            participant.save()

        if meeting.status == 'scheduled':
            meeting.status = 'live'
            meeting.save()

        return Response(MeetingParticipantSerializer(participant).data)


class MeetingLeaveView(APIView):
    def post(self, request, pk):
        MeetingParticipant.objects.filter(
            meeting_id=pk, user_id=request.user.id
        ).update(left_at=timezone.now())
        return Response({'status': 'left'})


class MeetingTokenView(APIView):
    def post(self, request, pk):
        try:
            meeting = Meeting.objects.get(pk=pk)
        except Meeting.DoesNotExist:
            return Response({'error': 'Not found'}, status=404)

        try:
            from livekit import api as livekit_api
            token = (
                livekit_api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
                .with_identity(str(request.user.id))
                .with_name(request.user.email)
                .with_grants(livekit_api.VideoGrants(room_join=True, room=meeting.livekit_room_name))
                .to_jwt()
            )
            return Response({'token': token, 'room': meeting.livekit_room_name, 'url': settings.LIVEKIT_URL})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
