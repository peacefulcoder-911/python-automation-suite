from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class HealthCheckTarget(BaseModel):
    name: str
    url: str
    timeout_seconds: int = 5


class AutomationConfig(BaseModel):
    schedule_interval_minutes: int = 15
    health_check_urls: List[HealthCheckTarget] = Field(default_factory=list)


class APIConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class Settings(BaseSettings):
    app_name: str = "Python Automation Suite"
    version: str = "1.0.0"
    environment: str = "development"
    api: APIConfig = APIConfig()
    automation: AutomationConfig = AutomationConfig()
    webhook_url: Optional[str] = None
    log_level: str = "INFO"

    @classmethod
    def from_yaml(cls, yaml_path: str = "config/config.yaml") -> "Settings":
        path = Path(yaml_path)
        if not path.exists():
            return cls()

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        app_info = data.get("app", {})
        api_info = data.get("api", {})
        auto_info = data.get("automation", {})
        notif_info = data.get("notifications", {})

        return cls(
            app_name=app_info.get("name", "Python Automation Suite"),
            version=app_info.get("version", "1.0.0"),
            environment=app_info.get("environment", "development"),
            api=APIConfig(**api_info) if api_info else APIConfig(),
            automation=AutomationConfig(**auto_info) if auto_info else AutomationConfig(),
            webhook_url=notif_info.get("webhook_url"),
            log_level=data.get("logging", {}).get("level", "INFO"),
        )