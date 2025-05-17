import os
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VideoRequestSerializer
from .highlights import analyze_video_with_scores, get_random_frame
from .utils import convert_to_seconds, cut_video_segments, create_zip_from_files, send_zip_via_email
import uuid

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
    email = serializer.validated_data["email"]
    video_path = video.temporary_file_path()
    
    result = analyze_video_with_scores(video_path)
    highlights = result["highlights"]
    timestamps = [convert_to_seconds(h["time"]) for h in highlights]
    
    segment_paths = cut_video_segments(video_path, timestamps)
    zip_path = "/tmp/highlights.zip"
    create_zip_from_files(segment_paths, zip_path)
    
    img_path = None
    try:
        image = get_random_frame(video_path)
        if image:
            img_path = f"/tmp/frame_{uuid.uuid4().hex}.jpg"
            image.save(img_path)

            send_zip_via_email(email, zip_path, img_path)
        else:
            raise Exception("Не удалось получить кадр из видео")
    except Exception as e:
        return Response({"status": "error", "message": f"Ошибка при отправке письма: {e}"}, status=500)
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if img_path and os.path.exists(img_path):
            os.remove(img_path)
        for p in segment_paths:
            if os.path.exists(p):
                os.remove(p)

    return Response({"status": "ok", "message": "Анализ завершён, нарезки отправлены на email."})

