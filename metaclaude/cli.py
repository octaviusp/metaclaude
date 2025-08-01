"""Main CLI interface for MetaClaude.

This module provides the command-line interface for MetaClaude, a tool that automates
the creation of complete software projects using Claude Code in isolated Docker
environments. It features rich terminal UI, comprehensive error handling, and
multiple commands for project generation and management.

Features:
    - Interactive project generation with AI assistance
    - Rich terminal UI with colors and progress indicators
    - Docker-based isolation for safe code generation
    - Template and agent management
    - Health checking and validation tools

Example:
    Basic usage:
        $ metaclaude "Create a React todo app with authentication"
    
    Advanced usage:
        $ metaclaude "Build a Python ML pipeline" --model sonnet --timeout 2h --verbose
    
    List available agents:
        $ metaclaude agents
    
    Health check:
        $ metaclaude doctor
"""

import sys
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.status import Status
from rich.tree import Tree
from rich.markup import escape
from rich.align import Align
from rich.columns import Columns
from rich.live import Live

from .core.orchestrator import MetaClaudeOrchestrator
from .utils.logging import setup_logging, get_logger, log_execution_start, log_execution_complete
from .utils.errors import MetaClaudeError, MetaClaudeTimeoutError

# Initialize CLI app and console
app = typer.Typer(
    name="metaclaude",
    help="🤖 MetaClaude - AI-powered project generation system",
    add_completion=False,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)
console = Console(stderr=True)
logger = get_logger(__name__)


def version_callback(value: bool) -> None:
    """Show version information."""
    if value:
        from . import __version__
        console.print(f"MetaClaude v{__version__}")
        raise typer.Exit()


@app.command()
def main(
    idea: str = typer.Argument(
        ...,
        help="Project idea or description to generate",
        metavar="IDEA",
    ),
    model: str = typer.Option(
        "opus",
        "--model",
        "-m",
        help="Claude model to use (opus, sonnet, haiku)",
        metavar="MODEL",
    ),
    agents: Optional[str] = typer.Option(
        None,
        "--agents",
        "-a",
        help="Comma-separated list of agents to use (auto for automatic selection)",
        metavar="AGENTS",
    ),
    no_cache: bool = typer.Option(
        False,
        "--no-cache",
        help="Force rebuild of Docker image (ignore cache)",
    ),
    timeout: str = typer.Option(
        "unlimited",
        "--timeout",
        "-t",
        help="Execution timeout (e.g., 30m, 2h, 7200s, unlimited)",
        metavar="TIMEOUT",
    ),
    keep_container: bool = typer.Option(
        False,
        "--keep-container",
        help="Keep Docker container after execution for debugging",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging output",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Custom output directory (default: ./metaclaude_output)",
        metavar="DIR",
    ),
    log_file: Optional[str] = typer.Option(
        None,
        "--log-file",
        help="Log to file (default: metaclaude.log)",
        metavar="FILE",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    agentic_mode: bool = typer.Option(
        True,
        "--agentic/--traditional",
        help="Use AI-powered agentic agent creation (default) or traditional pre-defined agents",
    ),
) -> None:
    """Generate a complete software project from an idea using AI.
    
    MetaClaude uses AI-powered agentic agent creation to automatically generate
    specialized sub-agents with research-enhanced knowledge for your project.
    These agents collaborate to build production-ready software projects.
    
    Examples:
    
        metaclaude "Create a React todo app with authentication"
        
        metaclaude "Build a Python ML pipeline for sentiment analysis" --model sonnet
        
        metaclaude "Design a REST API for a bookstore" --agentic
        
        metaclaude "Create an Electron desktop app" --timeout 2h --keep-container
        
        metaclaude "Build a blockchain dapp" --traditional --agents fullstack-engineer,qa-engineer
    """
    # Validate and setup
    _validate_inputs(idea, model, timeout)
    
    # Setup logging
    log_file_path = Path(log_file) if log_file else Path("metaclaude.log")
    setup_logging(
        level="DEBUG" if verbose else "INFO",
        log_file=log_file_path,
        verbose=verbose,
    )
    
    # Display banner
    _display_banner(idea, model)
    
    # Parse configuration
    timeout_seconds = _parse_timeout(timeout)
    force_agents = _parse_agents(agents) if agents and agents != "auto" else None
    output_base_dir = Path(output_dir) if output_dir else Path.cwd()
    
    # Get templates directory
    templates_dir = Path(__file__).parent.parent / "templates"
    
    try:
        # Initialize orchestrator
        orchestrator = MetaClaudeOrchestrator(
            templates_dir=templates_dir,
            output_base_dir=output_base_dir,
            enable_agentic_mode=agentic_mode,
        )
        
        # Execute VCC workflow
        results = orchestrator.execute(
            idea=idea,
            model=model,
            force_agents=force_agents,
            no_cache=no_cache,
            timeout=timeout_seconds,
            keep_container=keep_container,
            force_traditional_mode=not agentic_mode,
        )
        
        # Display results
        _display_results(results)
        
    except MetaClaudeTimeoutError:
        error_panel = Panel(
            "[red]⏰ Execution timed out![/red]\n\n"
            "💡 [dim]Try increasing timeout with [bold]--timeout[/bold] flag[/dim]",
            title="[bold red]⚠️  Timeout Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        )
        console.print(error_panel)
        sys.exit(1)
        
    except MetaClaudeError as e:
        error_panel = Panel(
            f"[red]❌ {e}[/red]\n\n"
            "💡 [dim]Check logs with [bold]--verbose[/bold] for more details[/dim]",
            title="[bold red]🚨 MetaClaude Error[/bold red]",
            border_style="red", 
            padding=(1, 2),
        )
        console.print(error_panel)
        if verbose:
            console.print_exception()
        sys.exit(1)
        
    except KeyboardInterrupt:
        interrupt_panel = Panel(
            "[yellow]⚠️  Execution interrupted by user[/yellow]\n\n"
            "[dim]Generation process was cancelled. \n"
            "Any partial results may be available in the output directory.[/dim]",
            title="[bold yellow]🛑 User Interrupt[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )
        console.print(interrupt_panel)
        sys.exit(1)
        
    except Exception as e:
        error_panel = Panel(
            f"[red]💥 {e}[/red]\n\n"
            "[dim]This is an unexpected error. Please report this issue on GitHub.[/dim]",
            title="[bold red]🔥 Unexpected Error[/bold red]",
            border_style="bright_red",
            padding=(1, 2),
        )
        console.print(error_panel)
        if verbose:
            console.print_exception()
        sys.exit(1)


def _validate_inputs(idea: str, model: str, timeout: str) -> None:
    """Validate command line inputs.
    
    Args:
        idea: Project idea
        model: Claude model name
        timeout: Timeout string
        
    Raises:
        typer.BadParameter: If validation fails
    """
    # Validate idea
    if not idea.strip():
        raise typer.BadParameter("Project idea cannot be empty")
    
    if len(idea) < 10:
        raise typer.BadParameter("Project idea should be at least 10 characters")
    
    # Validate model
    valid_models = ["opus", "sonnet", "haiku", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
    if model not in valid_models:
        raise typer.BadParameter(f"Invalid model. Choose from: {', '.join(valid_models[:3])}")
    
    # Validate timeout format
    try:
        _parse_timeout(timeout)
    except ValueError as e:
        raise typer.BadParameter(f"Invalid timeout format: {e}")


def _parse_timeout(timeout_str: str) -> int:
    """Parse timeout string to seconds.
    
    Args:
        timeout_str: Timeout string (e.g., '30m', '2h', '7200s', 'unlimited', '0')
        
    Returns:
        Timeout in seconds (0 for unlimited)
        
    Raises:
        ValueError: If format is invalid
    """
    timeout_str = timeout_str.strip().lower()
    
    # Handle unlimited timeout
    if timeout_str in ('unlimited', 'none', '0'):
        return 0  # 0 means unlimited
    
    if timeout_str.endswith('s'):
        return int(timeout_str[:-1])
    elif timeout_str.endswith('m'):
        return int(timeout_str[:-1]) * 60
    elif timeout_str.endswith('h'):
        return int(timeout_str[:-1]) * 3600
    elif timeout_str.isdigit():
        return int(timeout_str)  # Assume seconds
    else:
        raise ValueError(f"Invalid timeout format: {timeout_str}. Use format like '30m', '2h', '7200s', or 'unlimited'")


def _parse_agents(agents_str: str) -> List[str]:
    """Parse agents string to list.
    
    Args:
        agents_str: Comma-separated agents string
        
    Returns:
        List of agent names
    """
    agents = [agent.strip() for agent in agents_str.split(",")]
    return [agent for agent in agents if agent]  # Remove empty strings


def _display_banner(idea: str, model: str) -> None:
    """Display VCC banner and execution info with enhanced visuals.
    
    Args:
        idea: Project idea
        model: Claude model
    """
    # ASCII Art Banner
    ascii_art = Text("""
███╗   ███╗███████╗████████╗ █████╗  ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗
████╗ ████║██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝
██╔████╔██║█████╗     ██║   ███████║██║     ██║     ███████║██║   ██║██║  ██║█████╗  
██║╚██╔╝██║██╔══╝     ██║   ██╔══██║██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝  
██║ ╚═╝ ██║███████╗   ██║   ██║  ██║╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗
╚═╝     ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
""", style="bold cyan")
    
    subtitle = Text("AI-Powered Project Generation Platform", style="bold white")
    
    banner_content = Align.center(Columns([ascii_art, subtitle], equal=True))
    
    panel = Panel(
        banner_content,
        title="[bold magenta]🚀 MetaClaude[/bold magenta]",
        subtitle="[dim]Transforming ideas into complete software projects[/dim]",
        border_style="bright_cyan",
        padding=(1, 2),
    )
    console.print(panel)
    
    # Enhanced execution info with visual hierarchy
    info_panel = Panel(
        _create_execution_info_table(idea, model),
        title="[bold blue]⚙️  Execution Configuration[/bold blue]",
        border_style="blue",
        padding=(0, 1),
    )
    console.print(info_panel)
    console.print()

def _create_execution_info_table(idea: str, model: str) -> Table:
    """Create enhanced execution info table."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Icon", style="bold", width=4)
    table.add_column("Field", style="bold cyan", width=12)
    table.add_column("Value", style="white")
    
    # Truncate idea intelligently
    display_idea = idea[:80] + "..." if len(idea) > 80 else idea
    
    # Model display with color coding
    model_color = {
        "opus": "bright_magenta",
        "sonnet": "bright_green", 
        "haiku": "bright_yellow"
    }.get(model.lower(), "white")
    
    table.add_row("📝", "Idea:", f"[white]{escape(display_idea)}[/white]")
    table.add_row("🧠", "Model:", f"[{model_color}]{model.upper()}[/{model_color}]")
    table.add_row("🐳", "Runtime:", "[bright_blue]Docker + Claude Code[/bright_blue]")
    table.add_row("⏱️", "Timeout:", "[green]Unlimited[/green]")
    
    return table


def _display_results(results: dict) -> None:
    """Display execution results with enhanced visual formatting.
    
    Args:
        results: Execution results dictionary
    """
    # Success banner
    success_panel = Panel(
        "[bold green]🎉 PROJECT GENERATION COMPLETED SUCCESSFULLY! 🎉[/bold green]",
        border_style="bright_green",
        padding=(1, 0),
    )
    console.print(success_panel)
    
    # Results summary tree
    results_tree = Tree("[bold cyan]📊 Generation Summary[/bold cyan]")
    
    # Output information
    if results.get("output_path"):
        output_branch = results_tree.add("[bold blue]📁 Output Location[/bold blue]")
        output_branch.add(f"[white]{results['output_path']}[/white]")
    
    # Agent information
    if results.get("selected_agents"):
        # Show agentic mode info
        agentic_mode = results.get("agentic_mode", False)
        mode_icon = "🧠" if agentic_mode else "📋"
        mode_text = "AI-Generated Agents" if agentic_mode else "Pre-defined Agents"
        agents_branch = results_tree.add(f"[bold magenta]{mode_icon} {mode_text}[/bold magenta]")
        
        for agent in results["selected_agents"]:
            agent_icon = "🎯" if agentic_mode else "✓"
            agents_branch.add(f"[green]{agent_icon}[/green] {agent}")
        
        # Show agentic metadata if available
        if agentic_mode and results.get("agentic_metadata"):
            metadata = results["agentic_metadata"]
            if metadata.get("coordination_strategy"):
                agents_branch.add(f"[dim]Strategy: {metadata['coordination_strategy']}[/dim]")
            if metadata.get("blueprint", {}).get("estimated_duration"):
                agents_branch.add(f"[dim]Est. Duration: {metadata['blueprint']['estimated_duration']}[/dim]")
    
    # Technical details
    if results.get("analysis"):
        analysis = results["analysis"]
        tech_branch = results_tree.add("[bold yellow]⚙️  Technical Stack[/bold yellow]")
        
        if analysis.get("domains"):
            domains_sub = tech_branch.add("🏷️  Domains")
            for domain in analysis["domains"]:
                domains_sub.add(f"[cyan]{domain}[/cyan]")
        
        if analysis.get("technologies"):
            tech_sub = tech_branch.add("🔧 Technologies")
            for tech in analysis["technologies"]:
                tech_sub.add(f"[bright_blue]{tech}[/bright_blue]")
    
    # Performance metrics
    metrics_branch = results_tree.add("[bold red]📈 Performance Metrics[/bold red]")
    
    if results.get("execution_time"):
        time_str = f"{results['execution_time']:.1f}s"
        metrics_branch.add(f"⏱️  Duration: [green]{time_str}[/green]")
    
    if results.get("analysis", {}).get("confidence"):
        confidence = results["analysis"]["confidence"]["overall"]
        confidence_color = "green" if confidence > 0.7 else "yellow" if confidence > 0.4 else "red"
        metrics_branch.add(f"📊 Confidence: [{confidence_color}]{confidence:.1%}[/{confidence_color}]")
    
    console.print(results_tree)
    
    # Next steps panel
    next_steps = """[bold white]🚀 Next Steps:[/bold white]
    
[bold]1.[/bold] Navigate to output directory
[bold]2.[/bold] Review generated code and documentation  
[bold]3.[/bold] Follow setup instructions in README
[bold]4.[/bold] Install dependencies and run the project"""
    
    if results.get("output_path"):
        next_steps += f"\n\n[dim]💡 Quick start: [bold]cd {results['output_path']}[/bold][/dim]"
    
    next_steps_panel = Panel(
        next_steps,
        title="[bold green]📋 What's Next?[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print(next_steps_panel)


@app.command("validate")
def validate_templates() -> None:
    """Validate MetaClaude templates and configuration."""
    console.print("[blue]🔍 Validating MetaClaude templates...[/blue]")
    
    try:
        from .templates.manager import TemplateManager
        
        templates_dir = Path(__file__).parent.parent / "templates"
        template_manager = TemplateManager(templates_dir)
        
        errors = template_manager.validate_templates()
        
        if not errors:
            console.print("[green]✅ All templates are valid![/green]")
        else:
            console.print(f"[red]❌ Found {len(errors)} validation errors:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        sys.exit(1)


@app.command("agents")
def list_agents() -> None:
    """List available agents and their capabilities."""
    console.print("[blue]🤖 Available MetaClaude Agents[/blue]\n")
    
    try:
        from .agents.selector import AgentSelector
        
        templates_dir = Path(__file__).parent.parent / "templates"
        agents_dir = templates_dir / ".claude" / "agents"
        
        agent_selector = AgentSelector(agents_dir)
        
        if not agent_selector.available_agents:
            console.print("[yellow]⚠️  No agents found[/yellow]")
            return
        
        # Create agents table
        agents_table = Table()
        agents_table.add_column("Agent", style="cyan", width=20)
        agents_table.add_column("Description", style="white", width=50)
        agents_table.add_column("Tools", style="dim", width=15)
        agents_table.add_column("Patterns", style="green", width=15)
        
        for name, config in agent_selector.available_agents.items():
            tools_count = f"{len(config.tools)} tools"
            patterns_str = ", ".join(config.patterns) if config.patterns else "none"
            
            agents_table.add_row(
                name,
                config.description[:47] + "..." if len(config.description) > 50 else config.description,
                tools_count,
                patterns_str,
            )
        
        console.print(agents_table)
        
        # Show usage example
        console.print(f"\n[dim]Usage: metaclaude \"your idea\" --agents agent1,agent2[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to list agents: {e}[/red]")
        sys.exit(1)


@app.command("doctor")
def doctor() -> None:
    """Check MetaClaude system health and requirements."""
    console.print("[blue]🏥 MetaClaude System Health Check[/blue]\n")
    
    checks = []
    
    # Check Docker
    try:
        import docker
        client = docker.from_env()
        client.ping()
        checks.append(("Docker", "✅ Available", "green"))
    except Exception as e:
        checks.append(("Docker", f"❌ Error: {e}", "red"))
    
    # Check templates
    try:
        templates_dir = Path(__file__).parent.parent / "templates"
        if templates_dir.exists():
            checks.append(("Templates", "✅ Found", "green"))
        else:
            checks.append(("Templates", "❌ Not found", "red"))
    except Exception as e:
        checks.append(("Templates", f"❌ Error: {e}", "red"))
    
    # Check output directory permissions
    try:
        test_dir = Path.cwd() / "metaclaude_output"
        test_dir.mkdir(exist_ok=True)
        test_file = test_dir / "test.txt"
        test_file.write_text("test")
        test_file.unlink()
        checks.append(("Output Directory", "✅ Writable", "green"))
    except Exception as e:
        checks.append(("Output Directory", f"❌ Error: {e}", "red"))
    
    # Display results
    health_table = Table()
    health_table.add_column("Component", style="cyan", width=20)
    health_table.add_column("Status", width=30)
    
    all_good = True
    for component, status, color in checks:
        health_table.add_row(component, f"[{color}]{status}[/{color}]")
        if color == "red":
            all_good = False
    
    console.print(health_table)
    
    if all_good:
        console.print("\n[green]🎉 All systems operational![/green]")
    else:
        console.print("\n[red]⚠️  Some issues detected. Please resolve before using MetaClaude.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()