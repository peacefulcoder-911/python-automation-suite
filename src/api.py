from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
from src.config import Settings
from src.automation import AutomationEngine

app = FastAPI(
    title="Python Automation & API Suite",
    description="REST API and scheduler control plane for automated workflows",
    version="1.0.0",
)

settings = Settings.from_yaml()
engine = AutomationEngine(settings)


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
    """Returns application health and runs target endpoint diagnostics."""
    results = await engine.run_health_checks()
    all_healthy = all(r.get("healthy", False) for r in results)
    return JSONResponse(
        status_code=200 if all_healthy else 503,
        content={"system": "ok", "checks": results, "all_healthy": all_healthy},
    )


@app.post("/trigger/health-checks")
async def trigger_checks(background_tasks: BackgroundTasks):
    """Triggers health checks as an asynchronous background task."""
    background_tasks.add_task(engine.run_health_checks)
    return {"message": "Health check suite queued in background"}