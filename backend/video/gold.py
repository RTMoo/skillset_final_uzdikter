import os
import json
from moviepy.editor import VideoFileClip
from scenedetect import SceneManager, open_video, ContentDetector
from faster_whisper import WhisperModel

VIDEO_PATH = "nt.mp4"
OUTPUT_DIR = "output"
KEYWORDS = [
    "грант", "олимпиада", "победитель", "внимание", "важно",
    "запомните", "срочно", "теорема", "закон", "2025", "2024",
    "фишка", "лайфхак", "не нужно", "нельзя"
]
CLIP_DURATION = 30  # seconds
TOP_K = 5

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Step 1: Transcribe audio
def transcribe_audio(video_path):
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(video_path, beam_size=5)
    results = [(seg.start, seg.end, seg.text) for seg in segments if seg.text.strip()]
    return results

# Step 2: Detect scenes
def detect_scenes(video_path):
    video = open_video(video_path)
    manager = SceneManager()
    manager.add_detector(ContentDetector(threshold=30.0))
    manager.detect_scenes(video)
    return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in manager.get_scene_list()]

# Step 3: Score segments

def keyword_score(text):
    return sum(1 for word in KEYWORDS if word in text.lower())

def get_top_highlights(transcripts):
    scored = [(start, end, text, keyword_score(text)) for start, end, text in transcripts]
    scored = sorted(scored, key=lambda x: x[3], reverse=True)
    return scored[:TOP_K]

# Step 4: Cut clips
def save_clips(highlights):
    clips_info = []
    video = VideoFileClip(VIDEO_PATH)
    for i, (start, end, text, score) in enumerate(highlights):
        clip_start = max(0, start - 2)
        clip_end = min(video.duration, clip_start + CLIP_DURATION)
        clip = video.subclip(clip_start, clip_end)
        filename = os.path.join(OUTPUT_DIR, f"clip_{i+1}.mp4")
        clip.write_videofile(filename, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        clips_info.append({"file": filename, "start": clip_start, "end": clip_end, "text": text})
    return clips_info

# Step 5: Content plan
def generate_content_plan(clips):
    plan = []
    for i, clip in enumerate(clips):
        plan.append({
            "clip": os.path.basename(clip["file"]),
            "publish_date": f"2025-05-{18 + i}",
            "description": clip["text"][:80] + "..."
        })
    with open(os.path.join(OUTPUT_DIR, "content_plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    print("[1] Распознавание речи...")
    transcripts = transcribe_audio(VIDEO_PATH)

    print("[2] Анализ по ключевым словам...")
    highlights = get_top_highlights(transcripts)

    print("[3] Нарезка видео...")
    clips = save_clips(highlights)

    print("[4] Генерация контент-плана...")
    generate_content_plan(clips)

    print("Готово. Клип и content_plan.json находятся в папке output")

