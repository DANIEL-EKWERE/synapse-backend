from rest_framework import serializers
from .models import Workspace, WorkspaceMember, Channel, ChannelMessage


class WorkspaceMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkspaceMember
        fields = '__all__'
        read_only_fields = ['id', 'joined_at']


class WorkspaceSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Workspace
        fields = '__all__'
        read_only_fields = ['id', 'owner_id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.members.count()


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = '__all__'
        read_only_fields = ['id', 'created_by_id', 'created_at']


class ChannelMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelMessage
        fields = '__all__'
        read_only_fields = ['id', 'user_id', 'created_at']
