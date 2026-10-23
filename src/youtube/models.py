from enum import Enum
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class VideoNiche(str, Enum):
    SPACE = "space"
    PSYCHOLOGY = "psychology"
    STOICISM = "stoicism"
    TECH = "tech"
    HISTORY = "history"
    CUSTOM = "custom"


class ShortScript(BaseModel):
    niche: VideoNiche = VideoNiche.CUSTOM
    topic: str
    hook: str = Field(description="Attention-grabbing opening hook (0-3s)")
    facts_or_body: List[str] = Field(description="3-4 punchy key points or story narrative")
    call_to_action: str = Field(description="Closing CTA (e.g. Subscribe for daily mind facts)")
    estimated_duration_seconds: int = Field(default=45, ge=15, le=60)

    @property
    def full_voice_text(self) -> str:
        body_text = " ".join(self.facts_or_body)
        return f"{self.hook} {body_text} {self.call_to_action}".strip()


class VoiceConfig(BaseModel):
    voice: str = "en-US-ChristopherNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


class VideoRenderConfig(BaseModel):
    width: int = 1080
    height: int = 1920
    fps: int = 30
    subtitle_font_size: int = 56
    subtitle_color: str = "yellow"
    subtitle_stroke_color: str = "black"
    subtitle_stroke_width: int = 4
    output_dir: str = "output/shorts"


class YouTubeMetadata(BaseModel):
    title: str
    description: str
    tags: List[str]
    category_id: str = "27"
    privacy_status: str = "private"
    scheduled_time: Optional[str] = None


class PipelineResult(BaseModel):
    success: bool
    topic: str
    script: ShortScript
    metadata: YouTubeMetadata
    audio_path: Optional[str] = None
    subtitles_path: Optional[str] = None
    video_path: Optional[str] = None
    youtube_video_id: Optional[str] = None
    error: Optional[str] = None