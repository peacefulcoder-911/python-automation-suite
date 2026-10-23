import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from src.youtube.models import (
    PipelineResult,
    ShortScript,
    VideoNiche,
    VideoRenderConfig,
    VoiceConfig,
)
from src.youtube.script_generator import ScriptGenerator
from src.youtube.voiceover import EdgeTTSVoiceoverEngine
from src.youtube.media_fetcher import MediaFetcher
from src.youtube.video_renderer import ShortsVideoRenderer
from src.youtube.metadata import MetadataOptimizer
from src.youtube.uploader import YouTubeUploader

console = Console()


class YouTubeShortsPipeline:
    """Unified Orchestrator: Topic -> Script -> Voiceover -> Subtitles -> Render -> Upload."""

    def __init__(
        self,
        voice_config: VoiceConfig = VoiceConfig(),
        render_config: VideoRenderConfig = VideoRenderConfig(),
    ):
        self.voice_config = voice_config
        self.render_config = render_config
        self.voice_engine = EdgeTTSVoiceoverEngine(voice_config)
        self.media_fetcher = MediaFetcher()
        self.renderer = ShortsVideoRenderer(render_config)
        self.uploader = YouTubeUploader()

    async def run(
        self,
        topic: str,
        niche: VideoNiche = VideoNiche.SPACE,
        dry_run_upload: bool = True,
    ) -> PipelineResult:
        console.print(Panel(f"[bold green]Starting YouTube Shorts Pipeline[/bold green]\nTopic: [yellow]{topic}[/yellow] | Niche: [cyan]{niche.value}[/cyan]"))

        try:
            console.print("[bold]Step 1/6: Generating high-retention script...[/bold]")
            script = ScriptGenerator.generate(topic=topic, niche=niche)

            console.print("[bold]Step 2/6: Synthesizing neural voiceover & synchronized subtitles via Edge-TTS...[/bold]")
            slug = topic.lower().replace(" ", "_")[:20]
            audio_path = f"{self.render_config.output_dir}/{slug}_audio.mp3"
            subtitles_path = f"{self.render_config.output_dir}/{slug}_subs.vtt"
            await self.voice_engine.generate_speech(script.full_voice_text, audio_path, subtitles_path)

            console.print("[bold]Step 3/6: Fetching background footage / motion canvas...[/bold]")
            bg_video_path = f"{self.render_config.output_dir}/{slug}_bg.mp4"
            await self.media_fetcher.fetch_or_generate_background(
                query=topic,
                duration_seconds=script.estimated_duration_seconds,
                output_path=bg_video_path,
            )

            console.print("[bold]Step 4/6: Compositing vertical 9:16 video and burning stylized subtitles...[/bold]")
            final_video_path = f"{self.render_config.output_dir}/{slug}_short.mp4"
            self.renderer.render_short(bg_video_path, audio_path, subtitles_path, final_video_path)

            console.print("[bold]Step 5/6: Generating SEO title, tags, and description...[/bold]")
            metadata = MetadataOptimizer.optimize(script)

            console.print("[bold]Step 6/6: Publishing to YouTube...[/bold]")
            yt_id = self.uploader.upload_short(final_video_path, metadata, dry_run=dry_run_upload)

            console.print(Panel("[bold green]YouTube Shorts Automation Pipeline Finished Successfully![/bold green]"))

            return PipelineResult(
                success=True,
                topic=topic,
                script=script,
                metadata=metadata,
                audio_path=audio_path,
                subtitles_path=subtitles_path,
                video_path=final_video_path,
                youtube_video_id=yt_id,
            )

        except Exception as e:
            console.print(f"[bold red]Pipeline Error:[/bold red] {e}")
            return PipelineResult(
                success=False,
                topic=topic,
                script=ScriptGenerator.generate(topic=topic, niche=niche),
                metadata=MetadataOptimizer.optimize(ScriptGenerator.generate(topic=topic, niche=niche)),
                error=str(e),
            )