from rest_framework import generics
from .models import Workspace, WorkspaceMember, Channel, ChannelMessage
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer, ChannelSerializer, ChannelMessageSerializer


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        member_of = WorkspaceMember.objects.filter(user_id=self.request.user.id).values_list('workspace_id', flat=True)
        return Workspace.objects.filter(id__in=member_of)

    def perform_create(self, serializer):
        workspace = serializer.save(owner_id=self.request.user.id)
        WorkspaceMember.objects.create(workspace=workspace, user_id=self.request.user.id, role='owner')


class WorkspaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()


class WorkspaceMemberListView(generics.ListCreateAPIView):
    serializer_class = WorkspaceMemberSerializer

    def get_queryset(self):
        return WorkspaceMember.objects.filter(workspace_id=self.kwargs['pk'])


class AllChannelsListView(generics.ListAPIView):
    serializer_class = ChannelSerializer

    def get_queryset(self):
        member_of = WorkspaceMember.objects.filter(user_id=self.request.user.id).values_list('workspace_id', flat=True)
        return Channel.objects.filter(workspace_id__in=member_of)


class ChannelListCreateView(generics.ListCreateAPIView):
    serializer_class = ChannelSerializer

    def get_queryset(self):
        return Channel.objects.filter(workspace_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(workspace_id=self.kwargs['pk'], created_by_id=self.request.user.id)


class ChannelMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = ChannelMessageSerializer

    def get_queryset(self):
        return ChannelMessage.objects.filter(channel_id=self.kwargs['channel_id'])

    def perform_create(self, serializer):
        serializer.save(channel_id=self.kwargs['channel_id'], user_id=self.request.user.id)
