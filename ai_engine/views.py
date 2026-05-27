from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AISummary, TranscriptionJob
from .serializers import AISummarySerializer, TranscriptionJobSerializer
from .task import transcribe_recording, generate_meeting_summary, match_networking_attendees


class AISummaryListView(generics.ListAPIView):
    serializer_class = AISummarySerializer

    def get_queryset(self):
        return AISummary.objects.all()


class AISummaryDetailView(generics.RetrieveAPIView):
    serializer_class = AISummarySerializer
    queryset = AISummary.objects.all()


class TranscribeView(APIView):
    """Queue a transcription job for a recording URL."""

    def post(self, request):
        recording_url = request.data.get('recording_url')
        meeting_id = request.data.get('meeting_id')

        if not recording_url:
            return Response({'error': 'recording_url is required'}, status=status.HTTP_400_BAD_REQUEST)

        job = TranscriptionJob.objects.create(recording_url=recording_url, meeting_id=meeting_id)
        transcribe_recording.delay(str(job.id))

        return Response(TranscriptionJobSerializer(job).data, status=status.HTTP_202_ACCEPTED)


class NetworkingMatchView(APIView):
    """Trigger AI networking matchmaking for a virtual hall."""

    def post(self, request, hall_id):
        matches = match_networking_attendees(str(hall_id))
        return Response({'matches': matches})
