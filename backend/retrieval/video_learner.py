from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path

STORAGE_PATH = Path(__file__).resolve().parent.parent / "data" / "learned_videos.jsonl"
KEYFRAME_INTERVAL = 30  # seconds


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.strip().encode()).hexdigest()[:16]


def _load_known() -> dict[str, dict]:
    if not STORAGE_PATH.exists():
        return {}
    known: dict[str, dict] = {}
    for line in STORAGE_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        known[obj.get("url", "")] = obj
    return known


def _download_audio(url: str, tmp_dir: str) -> tuple[str, dict]:
    """Download audio via yt-dlp. Returns (audio_path, metadata)."""
    import yt_dlp

    audio_path = os.path.join(tmp_dir, "audio")
    metadata: dict = {}

    def _hook(d: dict) -> None:
        if d.get("status") == "finished":
            metadata["filename"] = d.get("filename", "")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": audio_path + ".%(ext)s",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        metadata["title"] = info.get("title", "")
        metadata["duration"] = info.get("duration", 0)
        metadata["uploader"] = info.get("uploader", "")

    # Find the downloaded file
    final_path = audio_path + ".mp3"
    if not os.path.exists(final_path):
        # Fallback: find any file starting with audio
        for f in os.listdir(tmp_dir):
            if f.startswith("audio"):
                final_path = os.path.join(tmp_dir, f)
                break

    return final_path, metadata


def _download_video(url: str, tmp_dir: str) -> str:
    """Download video for keyframe extraction. Returns video path."""
    import yt_dlp

    video_path = os.path.join(tmp_dir, "video")
    ydl_opts = {
        "format": "worst[ext=mp4]/worst",
        "outtmpl": video_path + ".%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    for f in os.listdir(tmp_dir):
        if f.startswith("video") and f.endswith((".mp4", ".mkv", ".webm")):
            return os.path.join(tmp_dir, f)
    return ""


def _transcribe(audio_path: str) -> str:
    """Transcribe audio using local whisper model."""
    import whisper

    model = whisper.load_model("base")
    result = model.transcribe(audio_path, fp16=False)
    return result.get("text", "").strip()


def _extract_keyframes(video_path: str) -> list[dict]:
    """Extract keyframe timestamps every KEYFRAME_INTERVAL seconds."""
    import cv2

    if not video_path or not os.path.exists(video_path):
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_ms = (total_frames / fps) * 1000 if fps else 0

    keyframes: list[dict] = []
    timestamp = 0.0
    idx = 0

    while timestamp * 1000 <= duration_ms:
        cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
        ret, _frame = cap.read()
        if not ret:
            break
        keyframes.append(
            {
                "timestamp_seconds": round(timestamp, 2),
                "frame_index": idx,
            }
        )
        idx += 1
        timestamp += KEYFRAME_INTERVAL

    cap.release()
    return keyframes


def _summarize_transcript(transcript: str, max_sentences: int = 5) -> str:
    """Simple extractive summary: first N sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", transcript.strip())
    summary = " ".join(sentences[:max_sentences])
    return summary if summary else transcript[:500]


def _build_knowledge(
    url: str,
    title: str,
    transcript: str,
    keyframes: list[dict],
    duration: int,
    uploader: str,
) -> dict:
    return {
        "url": url,
        "title": title,
        "transcript": transcript,
        "keyframe_timestamps": [kf["timestamp_seconds"] for kf in keyframes],
        "duration_seconds": duration,
        "knowledge_extracted": _summarize_transcript(transcript),
        "uploader": uploader,
    }


def _store(obj: dict) -> None:
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def learn_from_url(url: str) -> dict:
    """Main entry point. Downloads, transcribes, extracts keyframes, stores knowledge."""
    url = url.strip()
    if not url:
        return {"status": "error", "knowledge": ""}

    known = _load_known()
    if url in known:
        return {"status": "already_known", "knowledge": known[url].get("knowledge_extracted", "")}

    with tempfile.TemporaryDirectory() as tmp_dir:
        audio_path, meta = _download_audio(url, tmp_dir)
        transcript = _transcribe(audio_path)
        video_path = _download_video(url, tmp_dir)
        keyframes = _extract_keyframes(video_path)

    knowledge = _build_knowledge(
        url=url,
        title=meta.get("title", ""),
        transcript=transcript,
        keyframes=keyframes,
        duration=meta.get("duration", 0),
        uploader=meta.get("uploader", ""),
    )
    _store(knowledge)

    return {"status": "learned", "knowledge": knowledge["knowledge_extracted"]}
