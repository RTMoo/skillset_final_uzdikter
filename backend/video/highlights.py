import cv2
import torch
import clip
import whisper
from PIL import Image
from datetime import timedelta

device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, preprocess = clip.load("ViT-B/32", device=device)
whisper_model = whisper.load_model("tiny", device=device)

CLIP_INTERVAL = 5
TOP_K = 5
KEYWORDS = [
    "грант", "олимпиада", "победитель", "внимание", "важно",
    "запомните", "срочно", "теорема", "закон", "2025", "2024",
    "фишка", "лайфхак", "не нужно", "нельзя"
]
PROMPTS = [
    "exciting moment",
    "important announcement",
    "student wins",
    "funny moment",
    "emotional reaction"
]

def analyze_video_with_scores(video_path: str) -> dict:
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

if __name__ == "__main__":
    result = analyze_video_with_scores("nt.mp4")
    for h in result["highlights"]:
        print(f"{h['time']} — score {h['score']:.2f}")