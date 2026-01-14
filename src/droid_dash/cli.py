"""CLI entry point for Factory Dashboard."""

from __future__ import annotations

import json
import os
import shutil
import sys

import click
from rich.console import Console
from rich.table import Table

from .core import SessionAggregator, SessionParser
from .core.cost import CostEstimator, format_cost
from .core.models import Session
from .tui import FactoryDashboardApp

console = Console()


def _connect_to_session(session: Session) -> None:
    """Connect to a Droid session by replacing the current process."""
    # Check if droid is available
    droid_path = shutil.which("droid")
    if not droid_path:
        console.print("[red]Error: 'droid' command not found in PATH[/]")
        console.print("\nTo manually connect, run:")
        console.print(f"  cd {session.cwd or '.'}")
        console.print(f"  droid -r {session.id}")
        sys.exit(1)

    # Change to project directory if available
    if session.cwd and os.path.isdir(session.cwd):
        os.chdir(session.cwd)
        console.print(f"[dim]Changed directory to: {session.cwd}[/]")

    console.print(f"[bold green]Connecting to session:[/] {session.title}")
    console.print(f"[dim]Session ID: {session.id}[/]\n")

    # Replace current process with droid
    os.execvp(droid_path, [droid_path, "-r", session.id])


def format_tokens(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    elif count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def format_duration(ms: int) -> str:
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


@click.group(invoke_without_command=True)
@click.option(
    "--sessions-dir",
    "-d",
    type=click.Path(exists=True),
    default=None,
    help="Path to Factory sessions directory",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True),
    default=None,
    help="Path to config file (TOML)",
)
@click.pass_context
def main(ctx: click.Context, sessions_dir: str | None, config: str | None) -> None:
    """Factory Dashboard - TUI for Factory.ai session analytics."""
    from pathlib import Path

    from .core.config import load_config

    ctx.ensure_object(dict)

    # Load configuration
    config_path = Path(config) if config else None
    cfg = load_config(config_path)
    ctx.obj["config"] = cfg
    ctx.obj["sessions_dir"] = sessions_dir or cfg.get_sessions_dir()

    if ctx.invoked_subcommand is None:
        app = FactoryDashboardApp(sessions_dir=ctx.obj["sessions_dir"], config=cfg)
        result = app.run()

        # If result is a Session, connect to it with Droid
        if result is not None and hasattr(result, "id") and hasattr(result, "cwd"):
            _connect_to_session(result)


@main.command()
@click.option("--group", "-g", help="Filter by project group")
@click.option("--project", "-p", help="Filter by project name")
@click.pass_context
def stats(ctx: click.Context, group: str | None, project: str | None) -> None:
    """Display quick statistics."""
    parser = SessionParser(ctx.obj["sessions_dir"])
    sessions = parser.parse_all_sessions()

    if group:
        sessions = [s for s in sessions if s.project_group == group]
    if project:
        sessions = [s for s in sessions if s.project_name == project]

    if not sessions:
        console.print("[yellow]No sessions found[/]")
        return

    aggregator = SessionAggregator(sessions)
    stats = aggregator.get_dashboard_stats()
    cost_estimator = CostEstimator()
    total_cost = cost_estimator.estimate_total_cost(sessions)

    table = Table(title="Session Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Total Sessions", str(stats.total_sessions))
    table.add_row("Total Projects", str(len(stats.projects)))
    table.add_row("Project Groups", str(len(stats.project_groups)))
    table.add_row("Total Tokens", format_tokens(stats.total_tokens.total_tokens))
    table.add_row("Input Tokens", format_tokens(stats.total_tokens.input_tokens))
    table.add_row("Output Tokens", format_tokens(stats.total_tokens.output_tokens))
    table.add_row(
        "Cache Write", format_tokens(stats.total_tokens.cache_creation_tokens)
    )
    table.add_row("Cache Read", format_tokens(stats.total_tokens.cache_read_tokens))
    table.add_row("Cache Hit Ratio", f"{stats.total_tokens.cache_hit_ratio:.1%}")
    table.add_row("Active Time", format_duration(stats.total_active_time_ms))
    table.add_row("Estimated Cost", format_cost(total_cost))

    console.print(table)

    if stats.project_groups:
        groups_table = Table(title="By Project Group")
        groups_table.add_column("Group")
        groups_table.add_column("Projects")
        groups_table.add_column("Sessions")
        groups_table.add_column("Tokens")
        groups_table.add_column("Cost")

        for g in stats.project_groups:
            g_cost = sum(
                cost_estimator.estimate_session_cost(s)
                for p in g.projects
                for s in p.sessions
            )
            groups_table.add_row(
                g.name,
                str(g.project_count),
                str(g.session_count),
                format_tokens(g.total_tokens.total_tokens),
                format_cost(g_cost),
            )

        console.print(groups_table)


@main.command()
@click.option("--limit", "-n", default=10, help="Number of projects to show")
@click.pass_context
def tokens(ctx: click.Context, limit: int) -> None:
    """Display token usage by project."""
    parser = SessionParser(ctx.obj["sessions_dir"])
    sessions = parser.parse_all_sessions()
    aggregator = SessionAggregator(sessions)
    cost_estimator = CostEstimator()

    table = Table(title=f"Top {limit} Projects by Token Usage")
    table.add_column("Project")
    table.add_column("Group")
    table.add_column("Sessions")
    table.add_column("Tokens")
    table.add_column("Cost")

    top_projects = aggregator.get_top_projects_by_tokens(limit)
    for project in top_projects:
        cost = sum(cost_estimator.estimate_session_cost(s) for s in project.sessions)
        table.add_row(
            project.name,
            project.group,
            str(project.session_count),
            format_tokens(project.total_tokens.total_tokens),
            format_cost(cost),
        )

    console.print(table)


@main.command()
@click.option(
    "--format", "-f", "fmt", type=click.Choice(["json", "csv"]), default="json"
)
@click.option("--output", "-o", type=click.Path(), default=None)
@click.pass_context
def export(ctx: click.Context, fmt: str, output: str | None) -> None:
    """Export session data."""
    parser = SessionParser(ctx.obj["sessions_dir"])
    sessions = parser.parse_all_sessions()

    data = []
    for s in sessions:
        data.append(
            {
                "id": s.id,
                "project_name": s.project_name,
                "project_group": s.project_group,
                "project_path": s.project_path,
                "title": s.title,
                "timestamp": s.timestamp.isoformat() if s.timestamp else None,
                "model": s.model,
                "autonomy_mode": s.autonomy_mode,
                "active_time_ms": s.active_time_ms,
                "input_tokens": s.tokens.input_tokens,
                "output_tokens": s.tokens.output_tokens,
                "cache_creation_tokens": s.tokens.cache_creation_tokens,
                "cache_read_tokens": s.tokens.cache_read_tokens,
                "thinking_tokens": s.tokens.thinking_tokens,
                "total_tokens": s.tokens.total_tokens,
                "message_count": s.message_count,
            }
        )

    if fmt == "json":
        result = json.dumps(data, indent=2)
    else:
        import csv
        import io

        if not data:
            console.print("[yellow]No sessions to export[/]")
            return

        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        result = buffer.getvalue()

    if output:
        with open(output, "w") as f:
            f.write(result)
        console.print(f"[green]Exported {len(data)} sessions to {output}[/]")
    else:
        console.print(result)


@main.command()
@click.pass_context
def groups(ctx: click.Context) -> None:
    """List all project groups."""
    parser = SessionParser(ctx.obj["sessions_dir"])
    sessions = parser.parse_all_sessions()
    aggregator = SessionAggregator(sessions)
    stats = aggregator.get_dashboard_stats()

    for group in stats.project_groups:
        console.print(
            f"\n[bold cyan]{group.name}[/] ({group.session_count} sessions, {group.project_count} projects)"
        )
        for project in group.projects[:5]:
            console.print(f"  - {project.name} ({project.session_count} sessions)")
        if len(group.projects) > 5:
            console.print(f"  ... and {len(group.projects) - 5} more")


if __name__ == "__main__":
    main()
