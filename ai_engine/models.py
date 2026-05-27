import uuid
from django.db import models


class AISummary(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    meeting_id = models.UUIDField(null=True, blank=True)
    webinar_id = models.UUIDField(null=True, blank=True)
    meeting_title = models.CharField(max_length=255)
    transcript = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    action_items = models.JSONField(default=list)
    key_decisions = models.JSONField(default=list)
    follow_up_tasks = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ai_summaries'
        ordering = ['-created_at']


class TranscriptionJob(models.Model):
    STATUS_CHOICES = [('queued', 'Queued'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    meeting_id = models.UUIDField(null=True, blank=True)
    recording_url = models.URLField()
    transcript = models.TextField(blank=True, null=True)
    speakers = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'transcription_jobs'
        ordering = ['-created_at']
