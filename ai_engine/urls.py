from django.urls import path
from . import views

urlpatterns = [
    path('summaries/', views.AISummaryListView.as_view(), name='ai-summary-list'),
    path('summaries/<uuid:pk>/', views.AISummaryDetailView.as_view(), name='ai-summary-detail'),
    path('transcribe/', views.TranscribeView.as_view(), name='transcribe'),
    path('networking/<uuid:hall_id>/match/', views.NetworkingMatchView.as_view(), name='networking-match'),
]
