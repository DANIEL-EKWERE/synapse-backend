import uuid
from django.db import models


class Webinar(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('scheduled', 'Scheduled'), ('live', 'Live'), ('ended', 'Ended')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    host_id = models.UUIDField()
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_paid = models.BooleanField(default=False)
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_attendees = models.IntegerField(null=True, blank=True)
    livekit_room_name = models.CharField(max_length=255, blank=True, null=True)
    thumbnail_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinars'
        ordering = ['-start_time']


class WebinarRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='registrations')
    user_id = models.UUIDField()
    payment_status = models.CharField(max_length=20, default='pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinar_registrations'
        unique_together = ['webinar', 'user_id']


class WebinarPoll(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='polls')
    question = models.CharField(max_length=500)
    options = models.JSONField(default=list)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinar_polls'


class WebinarPollResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    poll = models.ForeignKey(WebinarPoll, on_delete=models.CASCADE, related_name='responses')
    user_id = models.UUIDField()
    selected_option = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinar_poll_responses'
        unique_together = ['poll', 'user_id']


class WebinarQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='questions')
    user_id = models.UUIDField()
    question = models.TextField()
    is_answered = models.BooleanField(default=False)
    upvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinar_questions'
        ordering = ['-upvotes', 'created_at']


class WebinarChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    webinar = models.ForeignKey(Webinar, on_delete=models.CASCADE, related_name='chat_messages')
    user_id = models.UUIDField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'webinar_chat_messages'
        ordering = ['created_at']
