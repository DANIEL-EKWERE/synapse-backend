from rest_framework import serializers
from .models import Meeting, MeetingParticipant


class MeetingParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingParticipant
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MeetingSerializer(serializers.ModelSerializer):
    participants = MeetingParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['id', 'host_id', 'livekit_room_name', 'created_at']
