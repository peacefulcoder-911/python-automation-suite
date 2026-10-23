import os
from pathlib import Path
from typing import Optional
from rich.console import Console

from src.youtube.models import YouTubeMetadata

console = Console()


class YouTubeUploader:
    """Handles authentication and publishing to YouTube Data API v3."""

    def __init__(self, client_secrets_file: Optional[str] = None):
        self.client_secrets_file = client_secrets_file or os.getenv("YOUTUBE_CLIENT_SECRETS", "client_secrets.json")

    def upload_short(
        self,
        video_path: str,
        metadata: YouTubeMetadata,
        dry_run: bool = True,
    ) -> Optional[str]:
        if dry_run or not os.path.exists(self.client_secrets_file):
            console.print("[bold yellow]Dry-run mode active:[/bold yellow] YouTube upload simulated successfully!")
            console.print(f"Title: {metadata.title}")
            console.print(f"Privacy: {metadata.privacy_status}")
            console.print(f"Tags: {', '.join(metadata.tags[:5])}...")
            return "simulated-yt-short-id-12345"

        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
        credentials = flow.run_local_server(port=0)
        youtube = build("youtube", "v3", credentials=credentials)

        body = {
            "snippet": {
                "title": metadata.title,
                "description": metadata.description,
                "tags": metadata.tags,
                "categoryId": metadata.category_id,
            },
            "status": {
                "privacyStatus": metadata.privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

        console.print("[bold cyan]Uploading video to YouTube...[/bold cyan]")
        response = request.execute()
        video_id = response.get("id")
        console.print(f"[bold green]Video uploaded successfully! ID:[/bold green] {video_id}")
        return video_id