import uuid
from django.db import models


class Workspace(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    owner_id = models.UUIDField()
    avatar_url = models.URLField(blank=True, null=True)
    plan = models.CharField(max_length=50, default='free')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'workspaces'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    ROLE_CHOICES = [('owner', 'Owner'), ('admin', 'Admin'), ('member', 'Member'), ('guest', 'Guest')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')
    user_id = models.UUIDField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workspace_members'
        unique_together = ['workspace', 'user_id']


class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='channels')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'channels'


class ChannelMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    user_id = models.UUIDField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'channel_messages'
        ordering = ['created_at']
