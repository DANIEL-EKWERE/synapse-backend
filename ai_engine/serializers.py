from rest_framework import serializers
from .models import AISummary, TranscriptionJob


class AISummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AISummary
        fields = '__all__'
        read_only_fields = ['id', 'status', 'transcript', 'summary', 'action_items', 'key_decisions', 'follow_up_tasks', 'created_at', 'completed_at']


class TranscriptionJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TranscriptionJob
        fields = '__all__'
        read_only_fields = ['id', 'status', 'transcript', 'speakers', 'created_at', 'completed_at']
