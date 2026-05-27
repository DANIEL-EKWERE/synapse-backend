from django.urls import path
from . import views

urlpatterns = [
    path('', views.WorkspaceListCreateView.as_view(), name='workspace-list'),
    path('<uuid:pk>/', views.WorkspaceDetailView.as_view(), name='workspace-detail'),
    path('<uuid:pk>/members/', views.WorkspaceMemberListView.as_view(), name='workspace-members'),
    path('<uuid:pk>/channels/', views.ChannelListCreateView.as_view(), name='workspace-channels'),
    path('<uuid:pk>/channels/<uuid:channel_id>/messages/', views.ChannelMessageListCreateView.as_view(), name='channel-messages'),
]
