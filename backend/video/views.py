import os
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VideoRequestSerializer
from .highlights import analyze_video_with_scores

@extend_schema(
    summary="Загрузка видео и email для анализа",
    description="Принимает видеофайл и email, возвращает результат анализа видео.",
    request=VideoRequestSerializer,
    responses={200: {"type": "object"}}
)
@api_view(["POST"])
def upload_video(request):
    serializer = VideoRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    video = serializer.validated_data["video"]
    
    path = video.temporary_file_path()

    result = analyze_video_with_scores(path)

    os.remove(path)

    return Response(result)
