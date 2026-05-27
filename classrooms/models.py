import uuid
from django.db import models


class Classroom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    teacher_id = models.UUIDField()
    subject = models.CharField(max_length=100, blank=True, null=True)
    cover_image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classrooms'
        ordering = ['-created_at']


class ClassroomEnrollment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments')
    student_id = models.UUIDField()
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classroom_enrollments'
        unique_together = ['classroom', 'student_id']


class Assignment(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    max_score = models.IntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['due_date']


class AssignmentSubmission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student_id = models.UUIDField()
    content = models.TextField(blank=True, null=True)
    file_url = models.URLField(blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'assignment_submissions'
        unique_together = ['assignment', 'student_id']


class Attendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance')
    student_id = models.UUIDField()
    session_date = models.DateField()
    is_present = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance'
        unique_together = ['classroom', 'student_id', 'session_date']
