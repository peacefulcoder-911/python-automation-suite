import pytest
from src.config import Settings
from src.client import APIClient
from src.automation import AutomationEngine


def test_settings_load():
    settings = Settings.from_yaml()
    assert settings.app_name is not None
    assert settings.version == "1.0.0"


@pytest.mark.asyncio
async def test_api_client_lifecycle():
    client = APIClient()
    httpx_client = await client.get_client()
    assert httpx_client is not None
    await client.close()


@pytest.mark.asyncio
async def test_health_check_execution():
    settings = Settings.from_yaml()
    engine = AutomationEngine(settings)
    results = await engine.run_health_checks()
    assert isinstance(results, list)
    assert len(results) > 0
    await engine.client.close()