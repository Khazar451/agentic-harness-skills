"""Command Line Interface for Agentic Harness Skills."""

from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from agentic_harness_skills.core.loader import SkillCatalogLoader
from agentic_harness_skills.core.schema import parse_skill_markdown

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Agentic Harness Skills CLI: Validate, discover, and inspect agent skills."""
    pass


@main.command(name="list")
@click.option(
    "--path",
    "-p",
    "search_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="skills",
    help="Directory to scan for skills (defaults to ./skills)",
)
def list_skills(search_path: Path) -> None:
    """List all available skills with token footprint and trigger metadata."""
    loader = SkillCatalogLoader(search_paths=[search_path])
    skills = loader.discover()

    if not skills:
        console.print(f"[yellow]No skills found in '{search_path}'.[/yellow]")
        return

    table = Table(title="Discovered Agent Skills", show_lines=True)
    table.add_column("Skill Name", style="bold cyan", no_wrap=True)
    table.add_column("Version", style="green", justify="center")
    table.add_column("Est. Tokens", style="magenta", justify="right")
    table.add_column("Triggers (when_to_use)", style="yellow")
    table.add_column("Description", style="white")

    total_tokens = 0
    for name, meta in sorted(skills.items()):
        tokens = meta.estimated_prompt_tokens()
        total_tokens += tokens
        triggers = meta.when_to_use or "-"
        table.add_row(
            name,
            meta.version or "1.0.0",
            str(tokens),
            triggers,
            meta.description,
        )

    console.print(table)
    console.print(
        f"[dim]Total discovery prompt token footprint: ~{total_tokens} tokens "
        f"across {len(skills)} skills.[/dim]\n"
    )


@main.command(name="validate")
@click.option(
    "--path",
    "-p",
    "search_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="skills",
    help="Directory to scan for skills (defaults to ./skills)",
)
def validate_skills(search_path: Path) -> None:
    """Validate all SKILL.md files against harness rules and character limits."""
    files = list(search_path.glob("**/SKILL.md"))
    if not files:
        console.print(f"[yellow]No SKILL.md files found in '{search_path}'.[/yellow]")
        return

    console.print(f"Validating {len(files)} skill files...\n")
    errors = 0
    warnings = 0

    base_dir = search_path.parent if search_path.parent.exists() else search_path
    for file_path in sorted(files):
        rel_path = file_path.relative_to(base_dir)
        try:
            content = file_path.read_text(encoding="utf-8")
            definition = parse_skill_markdown(content, file_path)
            meta = definition.metadata

            # Front-load check on triggers
            if not meta.when_to_use:
                console.print(f"[yellow]WARN[/yellow] {rel_path}: Missing 'when_to_use' trigger.")
                warnings += 1
            elif not meta.when_to_use.lower().startswith("triggers on:"):
                console.print(
                    f"[yellow]WARN[/yellow] {rel_path}: 'when_to_use' should front-load "
                    "'Triggers on: ...' to optimize budget."
                )
                warnings += 1

            console.print(
                f"[green]PASS[/green] [bold]{meta.name}[/bold] ({rel_path}) - "
                f"Body: {len(definition.body)} chars (~{definition.total_estimated_tokens} tokens)"
            )
        except Exception as exc:
            console.print(f"[red]FAIL[/red] {rel_path}: {exc}")
            errors += 1

    console.print()
    if errors > 0:
        console.print(
            f"[bold red]Validation failed with {errors} error(s) "
            f"and {warnings} warning(s).[/bold red]"
        )
        sys.exit(1)
    else:
        console.print(
            f"[bold green]All skills passed validation ({warnings} warning(s))![/bold green]"
        )


@main.command(name="inspect")
@click.argument("skill_name")
@click.option(
    "--path",
    "-p",
    "search_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="skills",
)
def inspect_skill(skill_name: str, search_path: Path) -> None:
    """Inspect the metadata and full Markdown instructions of a skill."""
    loader = SkillCatalogLoader(search_paths=[search_path])
    try:
        skill = loader.load_skill(skill_name)
    except KeyError as exc:
        console.print(f"[bold red]{exc}[/bold red]")
        sys.exit(1)

    meta = skill.metadata
    meta_info = (
        f"[bold]Name:[/bold] {meta.name} | [bold]Version:[/bold] {meta.version} | "
        f"[bold]License:[/bold] {meta.license}\n"
        f"[bold]Description:[/bold] {meta.description}\n"
        f"[bold]Triggers:[/bold] {meta.when_to_use or 'N/A'}\n"
        f"[bold]Estimated Total Tokens:[/bold] {skill.total_estimated_tokens}\n"
        f"[bold]Path:[/bold] {skill.path}"
    )

    console.print(Panel(meta_info, title=f"Skill Metadata: {skill.name}", border_style="cyan"))
    console.print("\n[bold underline]Full Instructions Body:[/bold underline]\n")
    console.print(Markdown(skill.body))


@main.command(name="prompt-catalog")
@click.option(
    "--path",
    "-p",
    "search_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default="skills",
)
def prompt_catalog(search_path: Path) -> None:
    """Output the compact XML catalog representation for prompt injection."""
    loader = SkillCatalogLoader(search_paths=[search_path])
    rendered = loader.render_system_prompt_catalog()
    console.print(rendered)


if __name__ == "__main__":
    main()
