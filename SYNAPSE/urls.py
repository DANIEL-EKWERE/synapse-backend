from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from workspaces.views import AllChannelsListView


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stub_list(_request):
    return Response([])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_stats(_request):
    return Response({})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users/',            include('users.urls')),
    path('api/meetings/',         include('meetings.urls')),
    path('api/webinars/',         include('webinars.urls')),
    path('api/classrooms/',       include('classrooms.urls')),
    path('api/coaching/',         include('coaching.urls')),
    path('api/ai/',               include('ai_engine.urls')),
    path('api/workspaces/',       include('workspaces.urls')),
    path('api/channels/',         AllChannelsListView.as_view()),
    path('api/metaverse/',        include('metaverse.urls')),
    path('api/spatial/rooms/',    stub_list),
    path('api/recordings/',       stub_list),
    path('api/calendar/events/',  stub_list),
    path('api/admin/stats/',      admin_stats),
]
