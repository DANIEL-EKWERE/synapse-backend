from celery import shared_task
from django.utils import timezone


@shared_task(bind=True, max_retries=3)
def transcribe_recording(self, job_id: str):
    """
    Celery task: transcribe a meeting recording using OpenAI Whisper.
    Triggered after a meeting ends and a recording URL is available.
    """
    from .models import TranscriptionJob
    import openai
    from django.conf import settings

    try:
        job = TranscriptionJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()

        openai.api_key = settings.OPENAI_API_KEY

        # Download audio and send to Whisper
        import urllib.request
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
            urllib.request.urlretrieve(job.recording_url, tmp.name)
            tmp_path = tmp.name

        with open(tmp_path, 'rb') as audio_file:
            response = openai.audio.transcriptions.create(
                model='whisper-1',
                file=audio_file,
                response_format='verbose_json',
            )

        os.unlink(tmp_path)

        job.transcript = response.text
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()

        # Trigger summary generation
        if job.meeting_id:
            generate_meeting_summary.delay(str(job.meeting_id), response.text)

    except Exception as exc:
        job.status = 'failed'
        job.save()
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def generate_meeting_summary(self, meeting_id: str, transcript: str):
    """
    Celery task: generate AI summary, action items, and key decisions
    from a meeting transcript using Claude.
    """
    from .models import AISummary
    import anthropic
    from django.conf import settings

    try:
        summary_obj, _ = AISummary.objects.get_or_create(
            meeting_id=meeting_id,
            defaults={'meeting_title': 'Meeting', 'status': 'processing'},
        )
        summary_obj.status = 'processing'
        summary_obj.transcript = transcript
        summary_obj.save()

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=2048,
            messages=[{
                'role': 'user',
                'content': f"""You are an expert meeting analyst for SYNAPSE, a collaboration platform.

Analyze this meeting transcript and return a JSON object with these exact keys:
- summary: A 2-3 paragraph summary of what was discussed
- action_items: Array of strings, each a specific action item with owner if mentioned
- key_decisions: Array of strings, each a key decision made
- follow_up_tasks: Array of strings, each a follow-up task

Transcript:
{transcript}

Return only valid JSON."""
            }],
        )

        import json
        result = json.loads(message.content[0].text)

        summary_obj.summary = result.get('summary', '')
        summary_obj.action_items = result.get('action_items', [])
        summary_obj.key_decisions = result.get('key_decisions', [])
        summary_obj.follow_up_tasks = result.get('follow_up_tasks', [])
        summary_obj.status = 'completed'
        summary_obj.completed_at = timezone.now()
        summary_obj.save()

    except Exception as exc:
        if 'summary_obj' in locals():
            summary_obj.status = 'failed'
            summary_obj.save()
        raise self.retry(exc=exc, countdown=120)


@shared_task
def match_networking_attendees(hall_id: str):
    """
    AI networking matchmaker for Virtual Hall attendees.
    Suggests connections based on shared interests from profiles.
    """
    from apps.spatial.models import HallAttendee
    from apps.users.models import Profile
    import anthropic
    from django.conf import settings

    attendees = HallAttendee.objects.filter(hall_id=hall_id).values_list('user_id', flat=True)
    profiles = Profile.objects.filter(id__in=attendees).values('id', 'full_name', 'role', 'bio', 'use_case')

    if len(profiles) < 2:
        return []

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    profile_text = '\n'.join([f"- {p['full_name']} ({p['role']}): {p['bio'] or p['use_case']}" for p in profiles])

    message = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=1024,
        messages=[{
            'role': 'user',
            'content': f"""Suggest 3 high-value networking connections from this attendee list.
Return JSON array of objects with: person_a, person_b, reason.

Attendees:
{profile_text}"""
        }],
    )

    import json
    return json.loads(message.content[0].text)
