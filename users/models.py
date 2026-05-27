import uuid
from django.db import models


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    avatar_url = models.URLField(blank=True, null=True)
    role = models.CharField(max_length=50, default='individual')
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=100, default='UTC')
    workspace_name = models.CharField(max_length=255, blank=True, null=True)
    use_case = models.CharField(max_length=255, blank=True, null=True)
    collaboration_goals = models.TextField(blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self):
        return self.full_name or self.email
