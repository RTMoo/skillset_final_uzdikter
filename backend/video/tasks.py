import zipfile
from io import BytesIO
from django.core.mail import EmailMessage
from celery import shared_task

@shared_task
def send_video_zip_email(file_content: bytes, filename: str, email_to: str):
    # Архивируем
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(filename, file_content)
    zip_buffer.seek(0)

    # Email
    email = EmailMessage(
        subject='Ваше видео',
        body='Во вложении ваше видео в архиве.',
        to=[email_to],
    )
    email.attach('video.zip', zip_buffer.read(), 'application/zip')
    email.send()
