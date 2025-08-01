# Project Understanding

## Executive Summary
MetaClaude is a Python CLI tool that automates the process of generating complete software projects from a single idea. It leverages AI agents, powered by Anthropic's Claude models, within a sandboxed Docker environment to analyze requirements, select appropriate technologies, and generate all necessary code, configuration, and documentation. The system is designed to be extensible, allowing for different AI agents with specialized skills (e.g., frontend, backend, QA) to collaborate on a project.

## Architecture Overview
The architecture is centered around the `MetaClaudeOrchestrator`, which manages the entire project generation workflow. The process can be summarized as follows:
1.  **Idea Analysis**: The user provides a project idea as a string. The `IdeaAnalyzer` component parses this idea to extract key domains, technologies, and complexity.
2.  **Agent Selection**: Based on the analysis, the `AgentSelector` chooses a team of specialized AI agents. The system supports two modes:
    *   **Traditional Mode**: Selects from a predefined set of agents (`fullstack-engineer`, `ml-dl-engineer`, `devops-engineer`, `qa-engineer`).
    *   **Agentic Mode**: (Currently the primary mode) Uses a `ClaudeAgenticIntegration` component to dynamically generate a team of agents tailored to the specific project idea.
3.  **Workspace Preparation**: A unique timestamped directory is created for the project in the `metaclaude_output` folder.
4.  **Docker Runtime**: A Docker image (`metaclaude:latest`) is built, containing the necessary environment for the Claude agents to run.
5.  **Configuration Injection**: The `TemplateManager` creates a `.claude` directory in the workspace, populating it with configuration files (`CLAUDE.md`, `settings.json`, `mcp.json`) and the selected agent definitions. These files instruct the Claude agents on how to build the project.
6.  **Container Execution**: The `DockerManager` starts a container from the `metaclaude:latest` image, mounting the workspace. A startup script inside the container then invokes the Claude agents to generate the project files in the `output` subdirectory.
7.  **Monitoring & Cleanup**: The orchestrator monitors the container's logs for completion or errors and cleans up the container afterward.

The system is modular, with clear separation of concerns between orchestration, Docker management, agent selection, template management, and idea analysis.

## Component Breakdown
-   **`metaclaude.cli`**: The entry point of the application, using `Typer` to create the command-line interface. It initializes and runs the `MetaClaudeOrchestrator`.
-   **`metaclaude.core.orchestrator.MetaClaudeOrchestrator`**: The central component that coordinates the entire project generation process. It orchestrates the other components to move from an idea to a complete project.
-   **`metaclaude.core.analyzer.IdeaAnalyzer`**: Responsible for parsing the user's project idea to identify domains (web, ML, etc.), technologies (Python, React, etc.), and complexity.
-   **`metaclaude.agents.selector.AgentSelector`**: Selects the most appropriate pre-defined AI agents for a given project idea based on the analysis from the `IdeaAnalyzer`. It can also be used to validate a user's forced selection of agents.
-   **`metaclaude.agents.parser.AgentParser`**: Parses agent definition files (in Markdown with YAML front-matter) into `AgentConfig` Pydantic models.
-   **`metaclaude.agents.claude_agentic_integration.ClaudeAgenticIntegration`**: A more advanced agent selection mechanism that uses a Claude model to dynamically create a team of agents with specific roles and responsibilities tailored to the project idea.
-   **`metaclaude.templates.manager.TemplateManager`**: Manages the creation of the `.claude` configuration directory. It uses Jinja2 to render templates for `CLAUDE.md`, `settings.json`, and `mcp.json`, and copies the selected agent definitions into the workspace.
-   **`metaclaude.docker.manager.DockerManager`**: A wrapper around the `docker-py` library to handle building the Docker image, running the container, executing commands, monitoring logs, and cleaning up resources.
-   **`metaclaude.config.models`**: Contains Pydantic models for strongly-typed configuration of various parts of the system (Docker, Agents, Logging, etc.).
-   **`run_metaclaude.py`**: A helper script to run the orchestrator directly, bypassing the CLI.

## Technology Stack
-   **Programming Language**: Python 3.9+
-   **CLI Framework**: `Typer`
-   **Containerization**: `Docker`
-   **Configuration Parsing**: `PyYAML` for agent front-matter.
-   **Templating**: `Jinja2` for generating Claude configuration files.
-   **Data Validation**: `Pydantic` for configuration models.
-   **Dependencies Management**: `Poetry`
-   **Testing**: `pytest`
-   **Linting/Formatting**: `ruff`, `black`

## Data Architecture
The primary data flow is as follows:
1.  A user's **project idea** (string) is the initial input.
2.  This is transformed into an **analysis dictionary** by the `IdeaAnalyzer`.
3.  The analysis is used by the `AgentSelector` to produce a **list of `AgentConfig` objects**.
4.  These `AgentConfig` objects, along with other project details, are used by the `TemplateManager` to generate a set of **configuration files** (`.claude/*`) within a temporary workspace.
5.  The Claude agents inside the Docker container read these configuration files to understand their roles and the project requirements.
6.  The final output is a **directory of generated source code** and project files.

There is no persistent database; the state is managed through files in the workspace for each execution.

## External Integrations
-   **Anthropic API**: The core dependency. The agents running inside the Docker container make calls to the Anthropic API to leverage Claude models for code generation. The `ANTHROPIC_API_KEY` must be available as an environment variable.
-   **Docker Hub/Registry**: The `docker` command-line tool needs to be installed and configured to pull base images if necessary.

## Deployment & Operations
The application is run as a local CLI tool. It is not designed to be deployed as a service. The main operational concerns are:
-   **Docker Daemon**: The Docker daemon must be running on the host machine.
-   **Anthropic API Key**: A valid `ANTHROPIC_API_KEY` must be set in the environment.
-   **Dependencies**: Project dependencies are managed by `Poetry`.

## Development Setup
1.  Clone the repository.
2.  Ensure Python 3.9+ and `Poetry` are installed.
3.  Run `poetry install` to create a virtual environment and install dependencies.
4.  Set the `ANTHROPIC_API_KEY` environment variable.
5.  Run the application using `poetry run metaclaude ...` or `poetry run python run_metaclaude.py`.
6.  Tests can be run with `poetry run pytest`.

## Security Architecture
-   **Sandboxing**: The most critical security feature is the use of Docker containers. All code generation and execution by the AI agents happen inside an isolated container, which has limited access to the host filesystem (only the workspace directory is mounted). This mitigates the risk of the AI generating and executing malicious code on the host.
-   **API Keys**: The `ANTHROPIC_API_KEY` is passed to the container as an environment variable. It is not stored in any configuration files.
-   **Permissions**: The `.claude/settings.local.json` file defines a set of allowed and denied shell commands that the Claude agents can execute, providing a layer of command-level security.

## Component Diagram
```
+-------------------------------------------------+
|                   User (CLI)                    |
+-------------------------------------------------+
                        |
                        v
+-------------------------------------------------+
|              metaclaude.cli (Typer)             |
+-------------------------------------------------+
                        |
                        v
+-------------------------------------------------+
|   metaclaude.core.orchestrator.MetaClaudeOrchestrator   |
+-------------------------------------------------+
      |          |          |          |          |
      v          v          v          v          v
+----------+ +----------+ +----------+ +----------+ +----------+
|  Idea    | |  Agent   | | Template | |  Docker  | | Claude   |
| Analyzer | | Selector | | Manager  | | Manager  | | Agentic  |
|          | |          | | (Jinja2) | | (Docker) | |Integration|
+----------+ +----------+ +----------+ +----------+ +----------+
                                           |
                                           v
+-------------------------------------------------+
|              Docker Container (metaclaude:latest) |
| +-------------------------------------------+   |
| |              Claude Agents                |   |
| |  (Interact with Anthropic API)            |   |
| +-------------------------------------------+   |
|                       |                       |
|                       v                       |
| +-------------------------------------------+   |
| |        Generated Project Files            |   |
| +-------------------------------------------+   |
+-------------------------------------------------+
```