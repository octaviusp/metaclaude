# Project Understanding

## Executive Summary
MetaClaude is a sophisticated Python command-line tool designed to automate the generation of complete software projects. It takes a natural language description of a project (an "idea") as input and leverages a suite of specialized AI agents, running within an isolated Docker environment, to produce production-ready source code. The system is designed to be extensible, allowing for the addition of new agents and templates to support a wide varietyy of project types and technology stacks.

## Architecture Overview
MetaClaude follows a modular, orchestrated architecture. The user interacts with a CLI, which serves as the main entry point. The CLI delegates the core logic to an `Orchestrator` module. This orchestrator coordinates a set of specialized managers, each responsible for a specific aspect of the project generation process: idea analysis, agent selection, template rendering, and Docker runtime management.

The entire AI-driven code generation process is executed inside a sandboxed Docker container. This ensures that the generation process is reproducible, secure, and isolated from the host system. The project's configuration, including the definition of the AI agents and their instructions, is dynamically generated based on the user's input and injected into the container at runtime.

## Component Breakdown

*   **CLI Interface (`metaclaude/cli.py`)**: Built with `Typer`. It parses command-line arguments, provides help messages, and orchestrates the overall execution by calling the `VCCOrchestrator`. It also includes utility commands for system health checks (`doctor`), listing available agents (`agents`), and validating templates (`validate`).

*   **VCCOrchestrator (`metaclaude/core/orchestrator.py`)**: The central coordinator. It manages the entire workflow, from preparing the workspace to cleaning up the Docker container. It uses the other managers to perform specific tasks in a predefined sequence.

*   **IdeaAnalyzer (`metaclaude/core/analyzer.py`)**: Responsible for parsing the user's natural language "idea". It extracts keywords, identifies potential domains (e.g., web, ML), and detects required technologies to inform the agent selection process.

*   **AgentSelector (`metaclaude/agents/selector.py`)**: Selects the most appropriate AI agents for the given project idea. It loads available agent definitions and uses the analysis from the `IdeaAnalyzer` to make an informed selection. The user can also override this selection with a manual list of agents.

*   **TemplateManager (`metaclaude/templates/manager.py`)**: Manages the generation of the `.claude` configuration directory. It uses the `Jinja2` templating engine to render `settings.json`, `CLAUDE.md`, and other necessary files. It injects dynamic information like the project name, selected agents, and the Claude model to use.

*   **DockerManager (`metaclaude/docker/manager.py`)**: Handles all interactions with the Docker daemon using the `docker` Python SDK. Its responsibilities include building the Docker image from the `Dockerfile`, running the container with the correct volume mounts and environment variables, monitoring its logs, and ensuring proper cleanup.

*   **ConfigManager (`metaclaude/config/manager.py`)**: Manages application configuration. It loads settings from files (`metaclaude.yaml`), environment variables, and CLI arguments, merging them into a single, validated configuration object using `Pydantic` models.

*   **Docker Container**: A sandboxed environment based on a Debian image with Node.js and the Claude Code CLI installed. It runs the actual code generation process, ensuring it's isolated and reproducible. The generated project code is written to a mounted volume.

## Technology Stack

*   **Programming Language**: Python 3.9+
*   **CLI Framework**: `Typer`
*   **Dependency Management**: `Poetry`
*   **Containerization**: `Docker`
*   **Templating**: `Jinja2`
*   **Configuration**: `Pydantic` for validation, `PyYAML` for file parsing
*   **Code Formatting & Linting**: `Black`, `Ruff`
*   **Runtime Environment (in Docker)**: Node.js 20

## Data Architecture

The primary data flow in MetaClaude is as follows:

1.  **Input**: The user provides a string "idea" via the CLI.
2.  **Configuration**: The `ConfigManager` loads and merges configuration from files, environment variables, and CLI arguments.
3.  **Analysis**: The `IdeaAnalyzer` processes the "idea" string into a structured dictionary containing domains, technologies, and complexity estimates.
4.  **Templating**: The `TemplateManager` uses this structured data, along with the selected agents, to generate the `.claude` configuration files (JSON and Markdown).
5.  **Execution**: These configuration files are mounted into the Docker container and used by the Claude Code CLI to guide the code generation process.
6.  **Output**: The final output is a complete software project, with its directory structure and source code files, written to a timestamped folder in the `metaclaude_output` directory on the host's filesystem.

## Deployment & Operations

MetaClaude is a command-line tool and is not deployed as a service. It is installed locally on a developer's machine.

*   **Build**: The project is packaged using `Poetry`.
*   **Dependencies**: Dependencies are managed in `pyproject.toml`.
*   **Execution**: The tool is run from the command line via the `metaclaude` script.
*   **Docker Requirement**: A running Docker daemon is required on the host machine to execute the code generation.

## Development Setup

1.  **Prerequisites**: Python 3.9+, Poetry, Docker Desktop.
2.  **Clone**: Clone the repository.
3.  **Install**: Run `poetry install` to create a virtual environment and install dependencies.
4.  **Activate**: Run `poetry shell` to activate the virtual environment.
5.  **Run**: Execute the tool with `poetry run python metaclaude.py "<IDEA>"`.
6.  **Tests**: Run tests with `poetry run pytest`.

## Security Architecture

*   **Isolation**: The core principle is isolation. All code generation, which involves running an external tool (Claude Code CLI), happens inside a sandboxed Docker container.
*   **Volume Mounts**: The container has limited access to the host filesystem. It can only read the injected configuration from the workspace and write the generated code to the `output` subdirectory within that workspace.
*   **Network**: The `Dockerfile` can be configured to restrict network access from within the container, allowing connections only to necessary services like the Anthropic API and package managers.
*   **Permissions**: The container is configured to run as a non-root user (`vcc`) to reduce potential security risks.
*   **CLI Flags**: The tool uses the `--dangerously-skip-permissions` flag for the `claude-code` CLI, but this is considered safe because it runs within the context of the isolated, ephemeral container with limited filesystem access.

## Component Diagram
```
Host System
├─ metaclaude.py (Main CLI entry point)
├─ vcc/ (Python package with modular architecture)
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
