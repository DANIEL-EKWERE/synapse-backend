from django.urls import re_path
from meetings.consumers import MeetingConsumer
from webinars.consumers import WebinarConsumer
from classrooms.consumers import ClassroomConsumer
from coaching.consumers import CoachingConsumer
from metaverse.consumers import MetaverseConsumer

websocket_urlpatterns = [
    re_path(r'^ws/meetings/(?P<meeting_id>[0-9a-f-]+)/$',     MeetingConsumer.as_asgi()),
    re_path(r'^ws/webinars/(?P<webinar_id>[0-9a-f-]+)/$',     WebinarConsumer.as_asgi()),
    re_path(r'^ws/classrooms/(?P<classroom_id>[0-9a-f-]+)/$', ClassroomConsumer.as_asgi()),
    re_path(r'^ws/coaching/(?P<session_id>[0-9a-f-]+)/$',     CoachingConsumer.as_asgi()),
    re_path(r'^ws/metaverse/(?P<space_id>[0-9a-f-]+)/$',      MetaverseConsumer.as_asgi()),
]
