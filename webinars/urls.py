from django.urls import path
from . import views

urlpatterns = [
    path('', views.WebinarListCreateView.as_view(), name='webinar-list'),
    path('<uuid:pk>/', views.WebinarDetailView.as_view(), name='webinar-detail'),
    path('<uuid:pk>/register/', views.WebinarRegisterView.as_view(), name='webinar-register'),
    path('<uuid:pk>/questions/', views.WebinarQuestionListCreateView.as_view(), name='webinar-questions'),
    path('<uuid:pk>/polls/', views.WebinarPollListCreateView.as_view(), name='webinar-polls'),
]
