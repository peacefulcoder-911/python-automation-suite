import argparse
import asyncio
import sys
import uvicorn
from rich.console import Console
from rich.panel import Panel

from src.automation import AutomationEngine
from src.config import Settings
from src.youtube.models import VideoNiche, VoiceConfig, VideoRenderConfig
from src.youtube.pipeline import YouTubeShortsPipeline

console = Console()


def print_banner(settings: Settings):
    banner = f"""[bold cyan]{settings.app_name}[/bold cyan] [yellow]v{settings.version}[/yellow]
Environment: [green]{settings.environment}[/green]
Python Automation & YouTube Shorts Pipeline"""
    console.print(Panel(banner, border_style="cyan"))


async def run_diagnostics():
    settings = Settings.from_yaml()
    print_banner(settings)
    engine = AutomationEngine(settings)
    console.print("\n[bold]Running Endpoint Diagnostics...[/bold]\n")
    await engine.run_health_checks()
    await engine.client.close()


async def run_shorts_pipeline(topic: str, niche_str: str, voice_name: str, live_upload: bool):
    settings = Settings.from_yaml()
    print_banner(settings)

    niche_map = {
        "space": VideoNiche.SPACE,
        "psychology": VideoNiche.PSYCHOLOGY,
        "stoicism": VideoNiche.STOICISM,
        "tech": VideoNiche.TECH,
        "history": VideoNiche.HISTORY,
    }
    niche = niche_map.get(niche_str.lower(), VideoNiche.SPACE)

    pipeline = YouTubeShortsPipeline(
        voice_config=VoiceConfig(voice=voice_name),
        render_config=VideoRenderConfig(output_dir="output/shorts"),
    )

    result = await pipeline.run(
        topic=topic,
        niche=niche,
        dry_run_upload=not live_upload,
    )

    if result.success:
        console.print(f"\n[bold green]Success![/bold green] Video generated: [cyan]{result.video_path}[/cyan]")
        console.print(f"Title: [yellow]{result.metadata.title}[/yellow]")
    else:
        console.print(f"\n[bold red]Pipeline failed:[/bold red] {result.error}")


def run_server():
    settings = Settings.from_yaml()
    print_banner(settings)
    console.print(f"[bold green]Starting FastAPI server at http://{settings.api.host}:{settings.api.port}[/bold green]")
    console.print(f"[bold cyan]Swagger UI available at http://{settings.api.host}:{settings.api.port}/docs[/bold cyan]\n")
    uvicorn.run("src.api:app", host=settings.api.host, port=settings.api.port, reload=settings.api.reload)


def main():
    parser = argparse.ArgumentParser(description="Python Automation Suite & YouTube Shorts Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # Command: run (diagnostics)
    subparsers.add_parser("run", help="Run system health checks and diagnostics")

    # Command: server
    subparsers.add_parser("server", help="Launch FastAPI REST control plane")

    # Command: shorts
    shorts_p = subparsers.add_parser("shorts", help="Run YouTube Shorts automation pipeline")
    shorts_p.add_argument("--topic", type=str, default="Cosmic Secrets of the Universe", help="Topic for the short")
    shorts_p.add_argument("--niche", type=str, choices=["space", "psychology", "stoicism", "tech", "history"], default="space")
    shorts_p.add_argument("--voice", type=str, default="en-US-ChristopherNeural", help="Edge-TTS neural voice")
    shorts_p.add_argument("--upload", action="store_true", help="Upload to YouTube (defaults to dry-run simulation)")

    args = parser.parse_args()

    if args.command == "server":
        run_server()
    elif args.command == "shorts":
        asyncio.run(run_shorts_pipeline(args.topic, args.niche, args.voice, args.upload))
    else:
        asyncio.run(run_diagnostics())


if __name__ == "__main__":
    main()