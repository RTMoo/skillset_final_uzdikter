import cv2
import torch
import os
import clip
import whisper
from PIL import Image
from datetime import timedelta
import random
import google.generativeai as genai

# Настройки безопасности Gemini
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Конфигурация Gemini
API = 'AIzaSyBXEXz9uxbDkPCs1O5PcVEKVjx0JUZ1-74'
genai.configure(api_key=API)
model = genai.GenerativeModel('gemini-1.5-flash', safety_settings=safety_settings)

# Модели
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)
whisper_model = whisper.load_model("tiny", device=device)

# Константы
CLIP_INTERVAL = 5
TOP_K = 5
KEYWORDS = [
    "грант", "олимпиада", "победитель", "внимание", "важно",
    "запомните", "срочно", "теорема", "закон", "2025", "2024",
    "фишка", "лайфхак", "не нужно", "нельзя"
]
PROMPTS = [
    "exciting moment", "important announcement", "student wins",
    "funny moment", "emotional reaction"
]


def get_random_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for _ in range(5): 
        frame_id = random.randint(0, total_frames - 1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
        success, frame = cap.read()

        if success and frame.mean() > 20:
            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            cap.release()
            return image

    cap.release()
    return None


def analyze_video_with_scores(video_path):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = int(frame_count / fps) if fps else 0

    audio_result = whisper_model.transcribe(video_path, verbose=False)
    segments = audio_result.get("segments", [])

    text_tokens = clip.tokenize(PROMPTS).to(device)

    scores = []
    for sec in range(0, duration, CLIP_INTERVAL):
        video.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        success, frame = video.read()
        if not success:
            continue

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        image_input = preprocess(image).unsqueeze(0).to(device)

        with torch.no_grad():
            image_features = clip_model.encode_image(image_input)
            text_features = clip_model.encode_text(text_tokens)

            image_features /= image_features.norm(dim=-1, keepdim=True)
            text_features /= text_features.norm(dim=-1, keepdim=True)

            similarity = (image_features @ text_features.T).squeeze()
            clip_score = float(similarity.max().item())

        speech_bonus = 0
        for seg in segments:
            if seg["start"] <= sec <= seg["end"]:
                if any(k in seg["text"].lower() for k in KEYWORDS):
                    speech_bonus = 0.3
                    break

        total_score = clip_score + speech_bonus
        scores.append((sec, total_score))

    top_scores = sorted(scores, key=lambda x: -x[1])[:TOP_K]
    highlights = [{"time": str(timedelta(seconds=t)), "score": s} for t, s in top_scores]

    video.release()
    return {
        "highlights": highlights,
        "transcript": audio_result["text"]
    }


def req_to_gemini(img) -> str:
    res = model.generate_content(["Опиши что тут в одном слове для названия видео, без лишних комментариев и специальных символах, только одно предложение - название ролика", img])
    return res.text


def hashtag_to_gemini(img) -> str:
    res = model.generate_content(["Сгенерируй на русском языке хэштеги для видео (минимум 5) что видишь сейчас и без лишних комментариев, только чистые данные. Формат: #tag, #tag... в одну строку, основная тема всех видео образовательная", img])
    return res.text


def main():
    video_path = "nt.mp4"
    result = analyze_video_with_scores(video_path)

    image = get_random_frame(video_path)
    if image:
        file_path = "random_frame.jpg"
        image.save(file_path)

        try:
            img = Image.open(file_path)

            title = req_to_gemini(img)
            hashtags = hashtag_to_gemini(img)

            print("Название:", title)
            print("Хэштеги:", hashtags)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    print("Highlights:")
    for h in result["highlights"]:
        print(f"{h['time']} — score {h['score']:.2f}")

if __name__ == "__main__":
    main()