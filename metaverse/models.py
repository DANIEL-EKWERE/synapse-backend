import uuid
from django.db import models


class Space(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    width = models.PositiveIntegerField(default=20)
    height = models.PositiveIntegerField(default=20)
    thumbnail = models.URLField(blank=True, null=True)
    creator_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class MetaverseElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    static = models.BooleanField(default=True)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class MetaverseMap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    thumbnail = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MapElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    map = models.ForeignKey(MetaverseMap, on_delete=models.CASCADE, related_name='map_elements')
    element = models.ForeignKey(MetaverseElement, on_delete=models.CASCADE)
    x = models.IntegerField(null=True, blank=True)
    y = models.IntegerField(null=True, blank=True)


class SpaceElement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='elements')
    element = models.ForeignKey(MetaverseElement, on_delete=models.CASCADE)
    x = models.IntegerField()
    y = models.IntegerField()


class MetaverseAvatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or str(self.id)
