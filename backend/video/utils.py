from django.core.mail import EmailMessage
from datetime import timedelta
import zipfile
import os
import uuid
import subprocess

def cut_video_segments(video_path: str, timestamps: list[int]) -> list[str]:
    segment_paths = []

    for i, t in enumerate(timestamps):
        start = max(t - 15, 0)
        duration = 30  # фиксированная длина: 15 до + 15 после

        output_path = f"/tmp/segment_{uuid.uuid4().hex}.mp4"
        cmd = [
            "ffmpeg",
            "-ss", str(start),
            "-i", video_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-y",  # overwrite
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            segment_paths.append(output_path)
        except subprocess.CalledProcessError:
            continue  # если ошибка при нарезке — просто пропускаем

    return segment_paths

def create_zip_from_files(file_paths: list[str], zip_path: str):
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file_path in file_paths:
            arcname = os.path.basename(file_path)  # без полного пути
            zipf.write(file_path, arcname)

def convert_to_seconds(t: str) -> int:
    h, m, s = map(float, t.split(":"))
    return int(timedelta(hours=h, minutes=m, seconds=s).total_seconds())

def send_zip_via_email(to_email: str, zip_path: str):
    subject = "Ваши нарезки с видео"
    body = "Во вложении находятся выделенные фрагменты видео."
    
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=None,  # берётся из DEFAULT_FROM_EMAIL
        to=[to_email]
    )
    
    email.attach_file(zip_path)  # Прикрепляем .zip файл
    email.send()
