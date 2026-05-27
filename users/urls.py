from django.urls import path
from . import views

urlpatterns = [
    path('register/',                      views.RegisterView.as_view(),                 name='register'),
    path('login/',                         views.LoginView.as_view(),                    name='login'),
    path('me/',                            views.MeView.as_view(),                       name='me'),
    path('profiles/',                      views.ProfileListView.as_view(),              name='profiles'),
    path('notifications/',                 views.NotificationListView.as_view(),         name='notifications'),
    path('notifications/unread-count/',    views.UnreadNotificationCountView.as_view(),  name='notif-count'),
    path('notifications/mark-all-read/',   views.MarkAllNotificationsReadView.as_view(), name='notif-mark-all'),
]
