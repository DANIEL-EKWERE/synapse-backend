import uuid
from django.db import models


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'), ('live', 'Live'),
        ('ended', 'Ended'),         ('cancelled', 'Cancelled'),
    ]
    # Matches what the frontend sends from the meeting type selector
    TYPE_CHOICES = [
        ('meeting',   'Meeting'),
        ('webinar',   'Webinar'),
        ('coaching',  'Coaching'),
        ('classroom', 'Classroom'),
        ('standup',   'Standup'),
        ('interview', 'Interview'),
        ('workshop',  'Workshop'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    host_id = models.UUIDField()
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=30)
    meeting_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='meeting')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    livekit_room_name = models.CharField(max_length=255, blank=True, null=True)
    recording_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meetings'
        ordering = ['start_time']

    def __str__(self):
        return self.title


class MeetingParticipant(models.Model):
    # Added co_host to match the frontend RoleBadge component
    ROLE_CHOICES = [
        ('host',        'Host'),
        ('co_host',     'Co-Host'),
        ('participant', 'Participant'),
        ('observer',    'Observer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='participants')
    user_id = models.UUIDField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'meeting_participants'
