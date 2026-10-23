import asyncio
from pathlib import Path
from typing import Dict, List, Tuple
import edge_tts
from rich.console import Console

from src.youtube.models import VoiceConfig

console = Console()


class EdgeTTSVoiceoverEngine:
    """High-fidelity neural text-to-speech engine using Microsoft Edge TTS (100% Free)."""

    POPULAR_VOICES = {
        "deep_doc": "en-US-ChristopherNeural",
        "energetic": "en-US-GuyNeural",
        "professional": "en-US-JennyNeural",
        "storyteller": "en-US-AriaNeural",
        "british": "en-GB-RyanNeural",
    }

    def __init__(self, config: VoiceConfig = VoiceConfig()):
        self.config = config

    async def generate_speech(
        self,
        text: str,
        output_audio_path: str,
        output_subtitles_path: str,
    ) -> Tuple[str, str]:
        audio_path = Path(output_audio_path)
        sub_path = Path(output_subtitles_path)

        audio_path.parent.mkdir(parents=True, exist_ok=True)
        sub_path.parent.mkdir(parents=True, exist_ok=True)

        communicate = edge_tts.Communicate(
            text=text,
            voice=self.config.voice,
            rate=self.config.rate,
            pitch=self.config.pitch,
            volume=self.config.volume,
        )

        submaker = edge_tts.SubMaker()
        with open(audio_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    submaker.create_sub((chunk["offset"], chunk["duration"]), chunk["text"])

        with open(sub_path, "w", encoding="utf-8") as file:
            file.write(submaker.generate_subs())

        console.print(f"[bold green]Voiceover generated:[/bold green] {audio_path}")
        console.print(f"[bold green]Subtitles generated:[/bold green] {sub_path}")

        return str(audio_path), str(sub_path)