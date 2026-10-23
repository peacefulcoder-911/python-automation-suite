import os
import re
from pathlib import Path
from typing import List, Tuple
from moviepy.editor import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
)
from rich.console import Console

from src.youtube.models import VideoRenderConfig

console = Console()


class ShortsVideoRenderer:
    """Assembles video footage, synchronized voiceover audio, and viral stylized subtitle overlays."""

    def __init__(self, config: VideoRenderConfig = VideoRenderConfig()):
        self.config = config

    def render_short(
        self,
        background_video_path: str,
        audio_path: str,
        subtitles_path: str,
        output_video_path: str,
    ) -> str:
        out_file = Path(output_video_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)

        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        video_clip = VideoFileClip(background_video_path)

        if video_clip.duration < duration:
            loop_count = int(duration // video_clip.duration) + 1
            from moviepy.editor import concatenate_videoclips
            video_clip = concatenate_videoclips([video_clip] * loop_count)

        video_clip = video_clip.subclip(0, duration)
        video_clip = video_clip.resize((self.config.width, self.config.height))
        video_clip = video_clip.set_audio(audio_clip)

        subtitle_clips = self._generate_subtitles_clips(subtitles_path, duration)
        all_clips = [video_clip] + subtitle_clips

        final_composite = CompositeVideoClip(all_clips, size=(self.config.width, self.config.height))

        console.print(f"[bold cyan]Rendering YouTube Short ({duration:.1f}s) to:[/bold cyan] {output_video_path}")
        final_composite.write_videofile(
            str(out_file),
            fps=self.config.fps,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=4,
            logger=None,
        )

        video_clip.close()
        audio_clip.close()
        final_composite.close()

        return str(out_file)

    def _generate_subtitles_clips(self, subtitles_path: str, total_duration: float) -> List[TextClip]:
        clips = []
        if not os.path.exists(subtitles_path):
            return clips

        sub_entries = self._parse_vtt(subtitles_path)
        for start, end, text in sub_entries:
            if start >= total_duration:
                continue
            clip_end = min(end, total_duration)
            clip_duration = clip_end - start
            if clip_duration <= 0.05:
                continue

            try:
                txt_clip = (
                    TextClip(
                        text.upper(),
                        fontsize=self.config.subtitle_font_size,
                        color=self.config.subtitle_color,
                        font="Arial-Bold",
                        stroke_color=self.config.subtitle_stroke_color,
                        stroke_width=self.config.subtitle_stroke_width,
                        method="caption",
                        size=(self.config.width - 120, None),
                    )
                    .set_start(start)
                    .set_duration(clip_duration)
                    .set_position(("center", 1250))
                )
                clips.append(txt_clip)
            except Exception:
                pass

        return clips

    def _parse_vtt(self, filepath: str) -> List[Tuple[float, float, str]]:
        results = []
        time_pattern = re.compile(r"(\d{2}):(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[.,](\d{3})")

        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            match = time_pattern.search(lines[i])
            if match:
                h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, match.groups())
                start_sec = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
                end_sec = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
                i += 1
                text_lines = []
                while i < len(lines) and lines[i].strip():
                    text_lines.append(lines[i].strip())
                    i += 1
                text = " ".join(text_lines)
                if text:
                    results.append((start_sec, end_sec, text))
            i += 1

        return results