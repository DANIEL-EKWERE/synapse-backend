from django.urls import path
from . import views

urlpatterns = [
    path('',                      views.MeetingListCreateView.as_view(),  name='meeting-list'),
    path('<uuid:pk>/',            views.MeetingDetailView.as_view(),      name='meeting-detail'),
    path('<uuid:pk>/participants/', views.MeetingParticipantsView.as_view(), name='meeting-participants'),
    path('<uuid:pk>/join/',       views.MeetingJoinView.as_view(),        name='meeting-join'),
    path('<uuid:pk>/leave/',      views.MeetingLeaveView.as_view(),       name='meeting-leave'),
    path('<uuid:pk>/token/',      views.MeetingTokenView.as_view(),       name='meeting-token'),
]
