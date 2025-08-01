# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MetaClaude is a Poetry-managed Python CLI that transforms natural language ideas into complete, production-ready software projects. It leverages Claude AI within isolated Docker environments, featuring a rich terminal UI, comprehensive error handling, and specialized agent orchestration for automated software development.

## Architecture

```
Host System
├─ metaclaude.py (Main CLI entry point)
├─ metaclaude/ (Python package with modular architecture)
│  ├─ cli.py (Typer-based CLI with Rich UI)
│  ├─ core/ (Business logic: orchestrator, analyzer)
│  ├─ docker/ (Docker container management)
│  ├─ agents/ (Agent selection and parsing)
│  ├─ templates/ (Jinja2 template system)
│  ├─ utils/ (Logging, errors, filesystem)
│  └─ mcp/ (Model Context Protocol integration)
├─ templates/.claude/ (Agent templates and configurations)
├─ docker/ (Dockerfile and container specs)
└─ metaclaude_output/<timestamp>/ (Generated project outputs)
    └─ Docker Container Runtime
       ├─ Debian + Node 20 + Claude Code CLI
       ├─ /workspace (mounted volume)
       └─ Generated project files
```

## Core Components

### MetaClaude Orchestrator (vcc/core/orchestrator.py)
Central coordination engine managing the complete generation workflow:
- **Workflow**: Idea analysis → Agent selection → Docker runtime → Claude Code execution → Project output
- **Components**: Integrates DockerManager, TemplateManager, AgentSelector, and IdeaAnalyzer
- **State Management**: Tracks execution state, containers, timeouts, and cleanup
- **Error Handling**: Comprehensive exception handling with recovery suggestions

### CLI Interface (vcc/cli.py)
Rich terminal interface built with Typer and Rich:
- **Commands**: `main` (generation), `doctor` (health check), `agents` (list), `validate` (templates)
- **Enhanced UI**: ASCII art banners, colored output, progress indicators, error panels
- **Input Validation**: Model validation, timeout parsing, comprehensive error messages

### Agent System (vcc/agents/)
Intelligent agent selection and management:
- **AgentSelector**: Analyzes project requirements and selects optimal AI specialists
- **AgentParser**: Parses YAML front-matter agent configurations
- **Available Agents**: fullstack-engineer, ml-dl-engineer, devops-engineer, qa-engineer

### Docker Integration (vcc/docker/manager.py)
Containerized execution environment:
- **Image Management**: Build, cache, and lifecycle management
- **Container Operations**: Run, monitor, execute commands, copy files
- **Volume Mounting**: Workspace and output directory management
- **Security**: Isolated execution with limited network access

## Development Commands

```bash
# Environment Setup
poetry install                    # Install dependencies
poetry shell                      # Activate virtual environment
export ANTHROPIC_API_KEY="..."    # Set API key for testing

# Main Usage
python metaclaude.py main "Create a React todo app"                    # Basic generation
python vcc.py main "Build ML pipeline" --model sonnet --verbose # Advanced options
python vcc.py main "Complex project" --timeout unlimited        # No timeout limit

# Utility Commands
python metaclaude.py doctor              # System health check
python metaclaude.py agents              # List available agents
python metaclaude.py validate            # Validate templates

# Testing and Quality
poetry run pytest                 # Run all tests
poetry run pytest tests/unit/     # Run specific test directory
poetry run pytest -k test_name    # Run single test
poetry run mypy vcc/              # Type checking
poetry run black vcc/             # Code formatting
poetry run ruff check vcc/        # Linting

# Docker Operations
docker build -t metaclaude:latest ./docker/  # Build image
docker images | grep metaclaude              # List MetaClaude images
docker container prune --filter "label=metaclaude" # Clean up containers
```

## Key Implementation Details

### Execution Flow (MetaClaude Orchestrator)
1. **Workspace Preparation**: Create timestamped output directory with proper permissions
2. **Idea Analysis**: Extract domains, technologies, complexity using IdeaAnalyzer
3. **Agent Selection**: Choose specialized agents based on project requirements
4. **Docker Runtime**: Build/reuse image, inject configuration templates
5. **Claude Code Launch**: Execute with comprehensive prompt and environment setup
6. **Progress Monitoring**: Real-time log monitoring with timeout handling
7. **Cleanup**: Container teardown with optional debugging retention

### Error Handling Architecture (vcc/utils/errors.py)
Enhanced exception hierarchy with recovery suggestions:
- **MetaClaudeError**: Base class with category, recovery hints, and context
- **Specialized Errors**: Docker, Template, Agent, Config, Execution, Timeout, Network, Validation
- **Error Mapping**: Automatic conversion from standard exceptions to MetaClaude errors
- **Rich Display**: Formatted error panels with actionable suggestions

### Agent Configuration System
Agent templates in `templates/.claude/agents/` with YAML front-matter:
```yaml
---
name: fullstack-engineer
description: Senior full-stack developer with expertise in modern web technologies
tools: [Bash, Read, Write, Edit, Glob, Grep, WebFetch, TodoWrite, WebSearch]
parallelism: 4
patterns: [coder, tester]
---
```

### CLI Command Structure
- **Main Command**: `python metaclaude.py main "<idea>"` with rich option parsing
- **Timeout Handling**: Supports unlimited, time units (30m, 2h), or raw seconds
- **Model Selection**: opus (default), sonnet, haiku with color-coded display
- **Debug Mode**: `--keep-container --verbose` for development/debugging

## Code Quality Standards

### Type Annotations
- Full type hint coverage with mypy strict mode
- Enhanced types in utils/errors.py with Enum categorization
- Optional/Union types for flexible parameter handling

### Code Formatting and Linting
- **Black**: Line length 100, Python 3.9+ target
- **Ruff**: Comprehensive rule set with security and performance checks
- **MyPy**: Strict type checking with no untyped definitions

### Testing Structure
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Cross-component integration tests  
- `tests/e2e/`: End-to-end workflow testing with Docker

## Extension Points

### Adding New Agents
1. Create `.md` file in `templates/.claude/agents/`
2. Add YAML front-matter with name, description, tools, patterns
3. Agent automatically discovered by AgentParser on next run

### Custom Error Types
Extend the error hierarchy in `vcc/utils/errors.py`:
```python
class MetaClaudeCustomError(MetaClaudeError):
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CUSTOM,
            recovery_hint="Custom recovery suggestion",
            **kwargs
        )
```

### MCP Server Integration
Configure additional servers in `vcc/mcp/manager.py`:
- Auto-detection via npm package availability
- Credential validation and configuration generation
- Dynamic server capability reporting

## Performance Characteristics

- **Startup Time**: 2-5 seconds for CLI initialization
- **Docker Build**: 3-8 minutes (cached: <30 seconds)
- **Generation Time**: 2-8 minutes depending on project complexity
- **Output Size**: Complete projects with documentation and build configs
- **Resource Usage**: Moderate CPU during generation, minimal memory footprint