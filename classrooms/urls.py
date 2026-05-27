from django.urls import path
from . import views

urlpatterns = [
    path('',                                                              views.ClassroomListCreateView.as_view(),     name='classroom-list'),
    path('assignments/',                                                  views.AllAssignmentsView.as_view(),          name='all-assignments'),
    path('enrollments/',                                                  views.AllEnrollmentsView.as_view(),          name='all-enrollments'),
    path('<uuid:pk>/',                                                    views.ClassroomDetailView.as_view(),         name='classroom-detail'),
    path('<uuid:pk>/assignments/',                                        views.AssignmentListCreateView.as_view(),    name='assignment-list'),
    path('<uuid:pk>/assignments/<uuid:assignment_id>/submissions/',       views.AssignmentSubmissionView.as_view(),    name='assignment-submissions'),
    path('<uuid:pk>/attendance/',                                         views.AttendanceView.as_view(),              name='attendance'),
    path('<uuid:pk>/enroll/',                                             views.EnrollView.as_view(),                  name='enroll'),
]
