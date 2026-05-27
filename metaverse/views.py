from rest_framework import generics
from .models import Space, MetaverseElement, MetaverseMap, MetaverseAvatar
from .serializers import (
    SpaceSerializer, MetaverseElementSerializer,
    MetaverseMapSerializer, MetaverseAvatarSerializer,
)


class SpaceListCreateView(generics.ListCreateAPIView):
    serializer_class = SpaceSerializer

    def get_queryset(self):
        return Space.objects.all()

    def perform_create(self, serializer):
        serializer.save(creator_id=self.request.user.id)


class SpaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SpaceSerializer
    queryset = Space.objects.all()


class ElementListCreateView(generics.ListCreateAPIView):
    serializer_class = MetaverseElementSerializer
    queryset = MetaverseElement.objects.all()


class ElementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MetaverseElementSerializer
    queryset = MetaverseElement.objects.all()


class MapListCreateView(generics.ListCreateAPIView):
    serializer_class = MetaverseMapSerializer
    queryset = MetaverseMap.objects.all()


class MapDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MetaverseMapSerializer
    queryset = MetaverseMap.objects.all()


class AvatarListCreateView(generics.ListCreateAPIView):
    serializer_class = MetaverseAvatarSerializer
    queryset = MetaverseAvatar.objects.all()
