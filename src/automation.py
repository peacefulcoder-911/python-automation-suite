import asyncio
from datetime import datetime
from typing import Any, Dict, List
from rich.console import Console
from rich.table import Table

from src.client import APIClient
from src.config import Settings

console = Console()


class AutomationEngine:
    """Core automation runner for scheduled tasks, health checks, and notifications."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = APIClient()

    async def run_health_checks(self) -> List[Dict[str, Any]]:
        """Checks all configured endpoints concurrently."""
        tasks = [
            self.client.check_endpoint(target.name, target.url)
            for target in self.settings.automation.health_check_urls
        ]
        results = await asyncio.gather(*tasks)

        self._print_results_table(results)
        return results

    def _print_results_table(self, results: List[Dict[str, Any]]) -> None:
        table = Table(title=f"Health Check Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        table.add_column("Service", style="cyan", no_wrap=True)
        table.add_column("URL", style="magenta")
        table.add_column("Status Code", justify="center")
        table.add_column("Latency (ms)", justify="right")
        table.add_column("Health", justify="center")

        for r in results:
            health_badge = "[bold green]PASS[/bold green]" if r.get("healthy") else "[bold red]FAIL[/bold red]"
            status = str(r.get("status_code")) if r.get("status_code") else "[dim]N/A[/dim]"
            latency = f"{r.get('latency_ms')} ms" if r.get("latency_ms") is not None else "[dim]--[/dim]"
            table.add_row(r["name"], r["url"], status, latency, health_badge)

        console.print(table)

    async def trigger_webhook(self, message: str) -> bool:
        """Sends an alert notification if a webhook URL is configured."""
        if not self.settings.webhook_url:
            return False
        payload = {"text": message, "timestamp": datetime.utcnow().isoformat()}
        result = await self.client.request("POST", self.settings.webhook_url, json_data=payload)
        return result.get("success", False)