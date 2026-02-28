"""CLI entry point for ai-harness-scorecard."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from .models import Grade
from .reporters.json_reporter import render_json
from .reporters.markdown import render_markdown
from .scanner import assess_repo

console = Console()

GRADE_COLORS = {
    Grade.A: "green",
    Grade.B: "blue",
    Grade.C: "yellow",
    Grade.D: "red",
    Grade.F: "bright_red",
}


@click.group()
@click.version_option(package_name="ai-harness-scorecard")
def main() -> None:
    """AI Harness Scorecard - Grade repos on engineering practices for safe AI-assisted development."""


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False))
@click.option(
    "--format", "output_format",
    type=click.Choice(["terminal", "markdown", "json"]),
    default="terminal",
    help="Output format.",
)
@click.option(
    "--output", "-o", "output_file",
    type=click.Path(),
    default=None,
    help="Write report to file instead of stdout.",
)
def assess(path: str, output_format: str, output_file: str | None) -> None:
    """Assess a repository against AI-assisted development best practices."""
    repo_path = Path(path).resolve()

    console.print(f"\n[bold]Assessing:[/bold] {repo_path}\n")

    with console.status("[bold green]Running checks..."):
        assessment = assess_repo(repo_path)

    if output_format == "json":
        report = render_json(assessment)
        _output(report, output_file)
        return

    if output_format == "markdown":
        report = render_markdown(assessment)
        _output(report, output_file)
        return

    _render_terminal(assessment)

    if output_file:
        report = render_markdown(assessment)
        _output(report, output_file)
        console.print(f"\n[dim]Report written to {output_file}[/dim]")


def _render_terminal(assessment) -> None:
    grade_color = GRADE_COLORS[assessment.grade]
    console.print(
        f"[bold {grade_color}]Grade: {assessment.grade.value}[/bold {grade_color}]"
        f"  ({assessment.overall_score:.1f}/100)"
    )
    console.print(f"[dim]{assessment.grade_description}[/dim]\n")

    summary = Table(title="Category Scores", show_lines=False)
    summary.add_column("Category", style="bold")
    summary.add_column("Weight", justify="right")
    summary.add_column("Score", justify="right")
    summary.add_column("Checks", justify="center")

    for cat in assessment.categories:
        passed = sum(1 for c in cat.checks if c.passed)
        total = len(cat.checks)
        score_color = _score_color(cat.percentage)
        summary.add_row(
            cat.name,
            f"{cat.weight:.0%}",
            f"[{score_color}]{cat.percentage:.0f}%[/{score_color}]",
            f"{passed}/{total}",
        )

    console.print(summary)
    console.print()

    for cat in assessment.categories:
        failed = [c for c in cat.checks if not c.passed]
        if not failed:
            continue
        console.print(f"[bold]{cat.name}[/bold] - failed checks:")
        for check in failed:
            console.print(f"  [red]FAIL[/red] {check.name}: {check.evidence}")
            if check.remediation:
                console.print(f"        [dim]Fix: {check.remediation}[/dim]")
        console.print()

    console.print(
        f"[bold]Total:[/bold] "
        f"{assessment.passed_checks}/{assessment.total_checks} checks passed"
    )
    lang_str = ", ".join(assessment.languages) if assessment.languages else "none detected"
    console.print(f"[dim]Languages: {lang_str}[/dim]")


def _score_color(percentage: float) -> str:
    if percentage >= 85:
        return "green"
    if percentage >= 70:
        return "blue"
    if percentage >= 55:
        return "yellow"
    return "red"


def _output(content: str, output_file: str | None) -> None:
    if output_file:
        Path(output_file).write_text(content, encoding="utf-8")
    else:
        click.echo(content)
