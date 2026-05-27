from rest_framework import serializers
from .models import Webinar, WebinarRegistration, WebinarPoll, WebinarQuestion, WebinarChatMessage


class WebinarSerializer(serializers.ModelSerializer):
    attendee_count = serializers.SerializerMethodField()

    class Meta:
        model = Webinar
        fields = '__all__'
        read_only_fields = ['id', 'host_id', 'livekit_room_name', 'created_at']

    def get_attendee_count(self, obj):
        return obj.registrations.filter(payment_status='completed').count()


class WebinarRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarRegistration
        fields = '__all__'
        read_only_fields = ['id', 'user_id', 'registered_at']


class WebinarPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarPoll
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class WebinarQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarQuestion
        fields = '__all__'
        read_only_fields = ['id', 'user_id', 'upvotes', 'created_at']


class WebinarChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebinarChatMessage
        fields = '__all__'
        read_only_fields = ['id', 'user_id', 'created_at']
