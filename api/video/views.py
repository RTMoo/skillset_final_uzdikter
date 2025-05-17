from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VideoRequestSerializer

@extend_schema(
    summary="Загрузка видео и email для анализа",
    description="Принимает видеофайл и email, возвращает подтверждение.",
    request=VideoRequestSerializer,
    responses={200: {"type": "object", "properties": {"ok": {"type": "string"}, "video": {"type": "string"}}}}
)
@api_view(["POST"])
def upload_video(request):
    serializer = VideoRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    video = serializer.validated_data["video"]
    email = serializer.validated_data["email"]
    
    return Response({"ok": email, "video": str(type(video))})
