from django.urls import re_path
from apps.workspaces.consumers import WorkspaceConsumer

websocket_urlpatterns = [
    re_path(r'^ws/workspaces/(?P<workspace_id>[0-9a-f-]+)/$', WorkspaceConsumer.as_asgi()),
]
