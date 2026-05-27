from rest_framework import serializers
from .models import CoachingSession, CoachingAvailability


class CoachingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachingSession
        fields = '__all__'
        read_only_fields = ['id', 'livekit_room_name', 'stripe_payment_intent', 'created_at']


class CoachingAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachingAvailability
        fields = '__all__'
        read_only_fields = ['id', 'coach_id', 'created_at']
