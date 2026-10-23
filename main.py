import argparse
import asyncio
import sys
import uvicorn
from rich.console import Console
from rich.panel import Panel

from src.automation import AutomationEngine
from src.config import Settings

console = Console()


def print_banner(settings: Settings):
    banner = f"""[bold cyan]{settings.app_name}[/bold cyan] [yellow]v{settings.version}[/yellow]
Environment: [green]{settings.environment}[/green]
Python Automation & REST API Control Plane"""
    console.print(Panel(banner, border_style="cyan"))


async def run_diagnostics():
    settings = Settings.from_yaml()
    print_banner(settings)
    engine = AutomationEngine(settings)
    console.print("\n[bold]Running Endpoint Diagnostics...[/bold]\n")
    await engine.run_health_checks()
    await engine.client.close()


def run_server():
    settings = Settings.from_yaml()
    print_banner(settings)
    console.print(f"[bold green]Starting FastAPI server at http://{settings.api.host}:{settings.api.port}[/bold green]")
    console.print(f"[bold cyan]Swagger UI available at http://{settings.api.host}:{settings.api.port}/docs[/bold cyan]\n")
    uvicorn.run(
        "src.api:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.reload,
    )


def main():
    parser = argparse.ArgumentParser(description="Python Automation Suite CLI")
    parser.add_argument(
        "command",
        choices=["run", "server", "check"],
        nargs="?",
        default="run",
        help="Command to run: 'check' for health checks, 'server' to launch API, 'run' for all diagnostics",
    )
    args = parser.parse_args()

    if args.command == "server":
        run_server()
    else:
        asyncio.run(run_diagnostics())


if __name__ == "__main__":
    main()