from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.CoachingSessionListCreateView.as_view(),  name='coaching-list'),
    path('<uuid:pk>/',                    views.CoachingSessionDetailView.as_view(),       name='coaching-detail'),
    path('availability/',                 views.CoachingAvailabilityView.as_view(),        name='coaching-availability'),
    path('availability/<uuid:coach_id>/', views.CoachingAvailabilityView.as_view(),        name='coach-availability'),
]
