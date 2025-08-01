# VCC Execution Flow Trace

This document provides an ultra-detailed trace of the function calls and logical flow when a user executes the command `poetry run vcc "Create a todo list app using React"`.

The flow is broken down by the component responsible for the actions.

---

### 1. Entry Point: Poetry & Typer CLI

1.  **User Command**:
    ```bash
    poetry run vcc "Create a todo list app using React"
    ```

2.  **Poetry Execution**:
    -   Poetry looks at `pyproject.toml` under `[tool.poetry.scripts]`.
    -   It finds the `vcc` script is mapped to `vcc.cli:main`.
    -   Poetry executes the `main` function located in the `/vcc/cli.py` file.

3.  **`vcc.cli.main(idea: str, ...)` function is invoked**:
    -   `idea` = `"Create a todo list app using React"`
    -   Other arguments (`model`, `timeout`, etc.) receive their default values or values from the command line.
    -   `_validate_inputs(idea, model, timeout)` is called to perform basic checks on the arguments.
    -   `setup_logging(...)` is called to configure the application's logger.
    -   `_display_banner(idea, model)` is called to print the welcome message and initial parameters to the console.
    -   `_parse_timeout("4h")` is called to convert the human-readable time string into an integer of seconds (e.g., `14400`).
    -   `templates_dir = Path(...)` calculates the absolute path to the `/templates` directory.
    -   **`orchestrator = VCCOrchestrator(templates_dir=..., output_base_dir=...)`**: An instance of the main orchestrator is created.
        -   **`VCCOrchestrator.__init__(...)`** (`vcc/core/orchestrator.py`):
            -   `self.docker_manager = DockerManager(...)` is instantiated.
            -   `self.template_manager = TemplateManager(...)` is instantiated.
            -   `self.agent_selector = AgentSelector(...)` is instantiated.
            -   `self.idea_analyzer = IdeaAnalyzer()` is instantiated.
    -   **`orchestrator.execute(idea=idea, ...)`**: This is the primary function call that triggers the main workflow.

---

### 2. Core Orchestration (`VCCOrchestrator.execute`)

The `execute` method in `vcc/core/orchestrator.py` now takes control.

1.  **`with self._timeout_context(timeout)`**: A timeout handler is set up to gracefully exit if the process takes too long.

2.  **`self._prepare_workspace(idea)`**:
    -   A unique, timestamped directory name is generated (e.g., `20250801_120000_CreateatodolistappusingReact`).
    -   The workspace directory is created: `vcc_output/20250801_120000.../`
    -   The final code destination is created: `vcc_output/20250801_120000.../output/`
    -   The paths are returned to the `execute` method.

3.  **`self._analyze_idea(idea)`**:
    -   Calls `self.idea_analyzer.analyze_comprehensive(idea)`.
        -   **`IdeaAnalyzer.analyze_comprehensive(idea)`** (`vcc/core/analyzer.py`):
            -   Parses the string `"Create a todo list app using React"`.
            -   Identifies keywords: `"todo"`, `"app"`, `"React"`.
            -   Determines `domains`: `['web']`.
            -   Determines `technologies`: `['react']`.
            -   Returns a dictionary containing this analysis.

4.  **`self._select_agents(idea, ...)`**:
    -   Calls `self.agent_selector.select_agents(idea, max_agents=4)`.
        -   **`AgentSelector.select_agents(idea, ...)`** (`vcc/agents/selector.py`):
            -   Performs its own internal analysis of the idea.
            -   Based on the "web" domain and "React" technology, it consults its internal mappings.
            -   It selects a list of agent names: `['fullstack-engineer', 'qa-engineer']`.
            -   This list is returned.

5.  **`self._build_runtime(no_cache)`**:
    -   Calls `self.docker_manager.image_exists()`.
        -   **`DockerManager.image_exists()`** (`vcc/docker/manager.py`):
            -   Calls `self.client.images.get("vcc-claude:latest")` to check if the image is already present.
    -   Assuming the image doesn't exist, it calls `self.docker_manager.build_image(...)`.
        -   **`DockerManager.build_image(...)`** (`vcc/docker/manager.py`):
            -   Calls `self.client.images.build(path="docker/", ...)` which executes the `Dockerfile` to build the `vcc-claude:latest` image.

6.  **`self._inject_configuration(...)`**:
    -   Calls `self.template_manager.render_claude_config(...)`.
        -   **`TemplateManager.render_claude_config(...)`** (`vcc/templates/manager.py`):
            -   Creates the `.claude` directory inside the unique workspace folder.
            -   **`self._render_settings(...)`**: Reads `templates/.claude/settings.json`, injects variables (like the model name), and writes the result to `vcc_output/.../.claude/settings.json`.
            -   **`self._render_claude_md(...)`**: Reads `templates/.claude/CLAUDE.md`, injects the user's `idea` and other analysis results, and writes it to `vcc_output/.../.claude/CLAUDE.md`.
            -   **`self._copy_selected_agents(...)`**:
                -   It finds the agent files `templates/.claude/agents/fullstack-engineer.md` and `templates/.claude/agents/qa-engineer.md`.
                -   It copies these files into the `vcc_output/.../.claude/agents/` directory.

7.  **`self._launch_claude_session(...)`**:
    -   Calls `self.docker_manager.run_container(...)`.
        -   **`DockerManager.run_container(...)`** (`vcc/docker/manager.py`):
            -   Defines the volume mounts, mapping the host workspace directory to `/workspace` inside the container.
            -   Defines the command to be run: `claude-code --dangerously-skip-permissions .`
            -   Calls `self.client.containers.run(...)` to start the container in detached mode.
            -   Returns the `Container` object.

8.  **`self._monitor_progress(container, timeout)`**:
    -   Enters a loop that calls `self.docker_manager.monitor_logs(container)`.
        -   **`DockerManager.monitor_logs(container)`** (`vcc/docker/manager.py`):
            -   Yields log lines from `container.logs(stream=True, follow=True)` as they are produced by the `claude-code` process inside the container.
    -   The orchestrator inspects each log line for signs of completion or errors.

---

### 3. Inside the Docker Container

Simultaneously, the `claude-code` process starts inside the container.

1.  **Initialization**: `claude-code` starts in the `/workspace` directory.
2.  **Configuration Loading**: It reads all the files in the `.claude` directory to configure itself.
    -   It sees the model name in `settings.json`.
    -   It reads its main goal from `CLAUDE.md`.
    -   It identifies its "team" by loading the agent files from the `.claude/agents/` directory.
3.  **Execution Loop**: The agents begin working on the goal.
    -   They might use tools like `bash` to run `npx create-react-app .` in the `/workspace/output` directory.
    -   They use tools like `Write` and `Edit` to create and modify files (`App.js`, `App.css`, etc.).
    -   The `qa-engineer` writes test files (`App.test.js`).
    -   All file system activity is contained within the `/workspace/output` directory, which is mounted back to the host.
4.  **Logging**: Throughout this process, `claude-code` prints its progress, thoughts, and actions to standard output, which is what the `VCCOrchestrator` is monitoring.

---

### 4. Finalization

1.  **Completion**: The `claude-code` process finishes and prints a completion message.
2.  **`VCCOrchestrator._monitor_progress(...)`**:
    -   The loop sees the completion message and breaks.
3.  **`VCCOrchestrator._cleanup(container, ...)`**:
    -   Calls `self.docker_manager.stop_container(container)`.
    -   Calls `self.docker_manager.cleanup_container(container, ...)` which removes the container.
4.  **Return to `vcc.cli.main`**:
    -   The `orchestrator.execute(...)` method returns a final `results` dictionary containing the output path, agents used, execution time, etc.
    -   `_display_results(results)` is called to print a final summary to the user.
    -   The program exits.

The user is left with a complete, ready-to-use React project in the `vcc_output/20250801_120000.../output/` directory.