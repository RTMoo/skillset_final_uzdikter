from rest_framework.serializers import Serializer, EmailField, FileField

class VideoRequestSerializer(Serializer):
    email = EmailField()
    video = FileField()
