from rest_framework import serializers
from .models import Space, MetaverseElement, MetaverseMap, MapElement, SpaceElement, MetaverseAvatar


class SpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ['id', 'name', 'width', 'height', 'thumbnail', 'creator_id', 'created_at']
        read_only_fields = ['id', 'creator_id', 'created_at']


class MetaverseElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaverseElement
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MetaverseMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaverseMap
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MapElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapElement
        fields = '__all__'
        read_only_fields = ['id']


class SpaceElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceElement
        fields = '__all__'
        read_only_fields = ['id']


class MetaverseAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaverseAvatar
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
