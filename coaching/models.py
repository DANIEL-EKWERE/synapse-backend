import uuid
from django.db import models


class CoachingSession(models.Model):
    STATUS_CHOICES = [('scheduled', 'Scheduled'), ('live', 'Live'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    coach_id = models.UUIDField()
    client_id = models.UUIDField(null=True, blank=True)
    title = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    livekit_room_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coaching_sessions'
        ordering = ['start_time']


class CoachingAvailability(models.Model):
    DAY_CHOICES = [(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    coach_id = models.UUIDField()
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coaching_availability'
        ordering = ['day_of_week', 'start_time']
