from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from src.config import Settings
from src.automation import AutomationEngine
from src.youtube.models import VideoNiche, VoiceConfig, VideoRenderConfig
from src.youtube.pipeline import YouTubeShortsPipeline

app = FastAPI(
    title="Python Automation & YouTube Shorts API",
    description="REST API control plane for endpoint diagnostics and YouTube Shorts automation",
    version="1.0.0",
)

settings = Settings.from_yaml()
engine = AutomationEngine(settings)
pipeline = YouTubeShortsPipeline()


class ShortsGenerateRequest(BaseModel):
    topic: str = "Mind-Blowing Space Secrets"
    niche: str = "space"
    voice: str = "en-US-ChristopherNeural"
    dry_run: bool = True


@app.get("/")
def root():
    return {
        "status": "online",
        "service": settings.app_name,
        "version": settings.version,
        "docs_url": "/docs",
    }


@app.get("/health")
async def health_check():
    results = await engine.run_health_checks()
    all_healthy = all(r.get("healthy", False) for r in results)
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={"system": "ok", "checks": results, "all_healthy": all_healthy},
    )


@app.post("/trigger/health-checks")
async def trigger_checks(background_tasks: BackgroundTasks):
    background_tasks.add_task(engine.run_health_checks)
    return {"message": "Health check suite queued in background"}


@app.post("/youtube/shorts/generate")
async def generate_short(req: ShortsGenerateRequest):
    """Triggers end-to-end generation of a YouTube Short."""
    niche_map = {
        "space": VideoNiche.SPACE,
        "psychology": VideoNiche.PSYCHOLOGY,
        "stoicism": VideoNiche.STOICISM,
        "tech": VideoNiche.TECH,
        "history": VideoNiche.HISTORY,
    }
    niche = niche_map.get(req.niche.lower(), VideoNiche.SPACE)
    result = await pipeline.run(topic=req.topic, niche=niche, dry_run_upload=req.dry_run)
    return result