#!/usr/bin/env python3
"""Generate fake Factory.ai session data for demo purposes."""

from __future__ import annotations

import argparse
import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

# Pre-generated project structure
PROJECT_GROUPS = {
    "work": ["api-service", "frontend", "data-pipeline", "infra", "ml-models"],
    "personal": ["blog", "dotfiles", "notes", "side-project"],
    "opensource": ["contrib-react", "cli-tool", "python-lib"],
}

# Pre-generated session titles (realistic dev tasks)
SESSION_TITLES = [
    # Bug fixes
    "Fix authentication bug in login endpoint",
    "Debug memory leak in worker process",
    "Fix race condition in async handler",
    "Resolve CORS issues with API gateway",
    "Fix broken pagination in list view",
    "Debug failing CI pipeline",
    "Fix timezone handling in scheduler",
    "Resolve database connection timeout",
    "Fix CSS layout issues on mobile",
    "Debug WebSocket disconnection problem",
    # Features
    "Implement user authentication flow",
    "Add caching layer for API responses",
    "Create data export functionality",
    "Implement search with filters",
    "Add dark mode support",
    "Create admin dashboard",
    "Implement file upload feature",
    "Add email notification system",
    "Create REST API endpoints",
    "Implement real-time updates",
    # Refactoring
    "Refactor database connection pooling",
    "Migrate to TypeScript",
    "Refactor authentication middleware",
    "Clean up legacy code in utils",
    "Optimize database queries",
    "Refactor state management",
    "Migrate from REST to GraphQL",
    "Refactor error handling",
    "Clean up unused dependencies",
    "Modernize build configuration",
    # Testing
    "Add unit tests for user service",
    "Write integration tests for API",
    "Add e2e tests for checkout flow",
    "Improve test coverage for auth module",
    "Add performance benchmarks",
    "Write tests for edge cases",
    "Add snapshot tests for components",
    "Create test fixtures",
    # DevOps
    "Set up CI/CD pipeline",
    "Configure Docker containers",
    "Set up monitoring and alerts",
    "Configure logging infrastructure",
    "Optimize deployment process",
    "Set up staging environment",
    "Configure auto-scaling",
    "Implement blue-green deployment",
    # Documentation
    "Update API documentation",
    "Write README for new module",
    "Document deployment process",
    "Create architecture diagrams",
    # Data
    "Create data migration script",
    "Implement ETL pipeline",
    "Set up data validation",
    "Create database backup strategy",
    "Optimize data indexing",
    # Analysis
    "Analyze performance bottlenecks",
    "Review security vulnerabilities",
    "Investigate slow queries",
    "Profile memory usage",
]

# Models with weights (Opus used more frequently in real usage)
MODELS = [
    ("claude-opus-4-5-20251101", 0.7),
    ("claude-sonnet-4-20250514", 0.25),
    ("claude-3-5-sonnet-20241022", 0.05),
]

AUTONOMY_MODES = ["auto-full", "auto-medium", "auto-low", "suggest", "spec"]


def weighted_choice(choices: list[tuple]) -> str:
    """Select from weighted choices."""
    items, weights = zip(*choices)
    return random.choices(items, weights=weights, k=1)[0]


def generate_token_usage(is_empty: bool = False) -> dict[str, int]:
    """Generate realistic token usage statistics."""
    if is_empty:
        return {
            "inputTokens": 0,
            "outputTokens": 0,
            "cacheCreationTokens": 0,
            "cacheReadTokens": 0,
            "thinkingTokens": 0,
        }

    # Real sessions are heavily cache-read dominated
    cache_read = random.randint(500_000, 15_000_000)
    cache_creation = random.randint(50_000, 500_000)
    output = random.randint(5_000, 100_000)
    input_tokens = random.randint(50, 500)
    thinking = random.choice(
        [0, 0, 0, random.randint(1000, 50000)]
    )  # Occasional thinking

    return {
        "inputTokens": input_tokens,
        "outputTokens": output,
        "cacheCreationTokens": cache_creation,
        "cacheReadTokens": cache_read,
        "thinkingTokens": thinking,
    }


def generate_settings(
    model: str, active_time_ms: int, is_empty: bool = False
) -> dict[str, Any]:
    """Generate session settings."""
    return {
        "assistantActiveTimeMs": active_time_ms,
        "model": model,
        "reasoningEffort": "off",
        "autonomyMode": random.choice(AUTONOMY_MODES),
        "tokenUsage": generate_token_usage(is_empty),
    }


def generate_jsonl(session_id: str, title: str, cwd: str, timestamp: datetime) -> str:
    """Generate minimal JSONL conversation log."""
    lines = []

    # Session start
    session_start = {
        "type": "session_start",
        "id": session_id,
        "title": title[:50] + "..." if len(title) > 50 else title,
        "owner": "demo",
        "version": 2,
        "cwd": cwd,
    }
    lines.append(json.dumps(session_start))

    # First user message
    message = {
        "type": "message",
        "id": str(uuid.uuid4()),
        "timestamp": timestamp.isoformat(),
        "message": {"role": "user", "content": [{"type": "text", "text": title}]},
    }
    lines.append(json.dumps(message))

    return "\n".join(lines) + "\n"


def encode_path(path: str) -> str:
    """Encode path to directory name format (replace / with -)."""
    return "-" + path.lstrip("/").replace("/", "-")


def generate_sessions(
    output_dir: str,
    num_sessions: int,
    start_date: datetime,
    end_date: datetime,
    empty_ratio: float = 0.15,
    seed: int | None = None,
) -> None:
    """Generate fake session data."""
    if seed is not None:
        random.seed(seed)

    os.makedirs(output_dir, exist_ok=True)

    # Build project list
    projects = []
    for group, project_names in PROJECT_GROUPS.items():
        for project in project_names:
            path = f"/Users/demo/projects/{group}/{project}"
            projects.append((path, project, group))

    # Generate sessions
    all_session_ids = []
    date_range = (end_date - start_date).days

    for _i in range(num_sessions):
        session_id = str(uuid.uuid4())
        all_session_ids.append(session_id)

        # Random project
        path, project_name, group = random.choice(projects)

        # Random timestamp within range
        days_offset = random.randint(0, date_range)
        hours_offset = random.randint(0, 23)
        minutes_offset = random.randint(0, 59)
        timestamp = start_date + timedelta(
            days=days_offset, hours=hours_offset, minutes=minutes_offset
        )

        # Determine if this is an empty session
        is_empty = random.random() < empty_ratio

        # Session content
        if is_empty:
            title = random.choice(["New Session", "Untitled Session"])
            active_time_ms = 0
        else:
            title = random.choice(SESSION_TITLES)
            active_time_ms = random.randint(60_000, 3_600_000)  # 1 min to 1 hour

        model = weighted_choice(MODELS)

        # Create project directory
        project_dir = os.path.join(output_dir, encode_path(path))
        os.makedirs(project_dir, exist_ok=True)

        # Write settings file
        settings = generate_settings(model, active_time_ms, is_empty)
        settings_path = os.path.join(project_dir, f"{session_id}.settings.json")
        with open(settings_path, "w") as f:
            json.dump(settings, f, indent=2)

        # Write JSONL file
        jsonl_content = generate_jsonl(session_id, title, path, timestamp)
        jsonl_path = os.path.join(project_dir, f"{session_id}.jsonl")
        with open(jsonl_path, "w") as f:
            f.write(jsonl_content)

    # Generate favorites (random 5-10% of sessions)
    num_favorites = max(1, int(len(all_session_ids) * random.uniform(0.05, 0.10)))
    favorites = random.sample(all_session_ids, num_favorites)
    favorites_path = os.path.join(output_dir, ".favorites")
    with open(favorites_path, "w") as f:
        json.dump(favorites, f, indent=2)

    print(f"Generated {num_sessions} sessions in {output_dir}")
    print(f"  - Projects: {len(projects)}")
    print(f"  - Empty sessions: {int(num_sessions * empty_ratio)}")
    print(f"  - Favorites: {num_favorites}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate fake Factory.ai session data for demo purposes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./demo_sessions
  %(prog)s ./demo_sessions --num-sessions 100 --seed 42
  %(prog)s ./demo_sessions --start-date 2025-01-01 --end-date 2025-06-01
        """,
    )

    parser.add_argument(
        "output_dir",
        help="Target directory for fake sessions (required)",
    )
    parser.add_argument(
        "--num-sessions",
        "-n",
        type=int,
        default=50,
        help="Total number of sessions to generate (default: 50)",
    )
    parser.add_argument(
        "--start-date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc),
        default=datetime.now(timezone.utc) - timedelta(days=90),
        help="Start date for sessions YYYY-MM-DD (default: 90 days ago)",
    )
    parser.add_argument(
        "--end-date",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc),
        default=datetime.now(timezone.utc),
        help="End date for sessions YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--empty-ratio",
        type=float,
        default=0.15,
        help="Ratio of empty/new sessions (default: 0.15)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility",
    )

    args = parser.parse_args()

    generate_sessions(
        output_dir=args.output_dir,
        num_sessions=args.num_sessions,
        start_date=args.start_date,
        end_date=args.end_date,
        empty_ratio=args.empty_ratio,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()
