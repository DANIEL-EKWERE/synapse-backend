from django.urls import path
from . import views

urlpatterns = [
    path('spaces/',              views.SpaceListCreateView.as_view(),   name='space-list'),
    path('spaces/<uuid:pk>/',    views.SpaceDetailView.as_view(),       name='space-detail'),
    path('elements/',            views.ElementListCreateView.as_view(), name='element-list'),
    path('elements/<uuid:pk>/',  views.ElementDetailView.as_view(),     name='element-detail'),
    path('maps/',                views.MapListCreateView.as_view(),     name='map-list'),
    path('maps/<uuid:pk>/',      views.MapDetailView.as_view(),         name='map-detail'),
    path('avatars/',             views.AvatarListCreateView.as_view(),  name='avatar-list'),
]
