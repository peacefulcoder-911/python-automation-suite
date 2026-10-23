import os
from pathlib import Path
from typing import Optional
from rich.console import Console
import httpx

console = Console()


class MediaFetcher:
    """Fetches vertical background footage or generates aesthetic motion canvases."""

    def __init__(self, pexels_api_key: Optional[str] = None):
        self.pexels_api_key = pexels_api_key or os.getenv("PEXELS_API_KEY")

    async def fetch_or_generate_background(
        self,
        query: str,
        duration_seconds: float,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
    ) -> str:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if self.pexels_api_key:
            try:
                downloaded = await self._fetch_pexels_video(query, str(out))
                if downloaded:
                    return str(out)
            except Exception as e:
                console.print(f"[yellow]Pexels API fetch failed ({e}), using procedural canvas generator...[/yellow]")

        return self.generate_procedural_background(duration_seconds, str(out), width, height)

    async def _fetch_pexels_video(self, query: str, output_path: str) -> bool:
        url = "https://api.pexels.com/videos/search"
        headers = {"Authorization": self.pexels_api_key}
        params = {"query": query, "orientation": "portrait", "per_page": 3}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
            videos = data.get("videos", [])
            if not videos:
                return False

            video_files = videos[0].get("video_files", [])
            hd_files = [f for f in video_files if f.get("width", 0) >= 1080 and f.get("height", 0) >= 1920]
            target_file = hd_files[0] if hd_files else video_files[0]
            download_url = target_file["link"]

            video_resp = await client.get(download_url)
            with open(output_path, "wb") as f:
                f.write(video_resp.content)
            return True

    def generate_procedural_background(
        self,
        duration_seconds: float,
        output_path: str,
        width: int = 1080,
        height: int = 1920,
    ) -> str:
        from moviepy.editor import ColorClip

        clip = ColorClip(size=(width, height), color=(14, 18, 32), duration=duration_seconds)
        clip.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            preset="ultrafast",
            logger=None,
        )
        console.print(f"[bold cyan]Procedural 9:16 background generated:[/bold cyan] {output_path}")
        return output_path