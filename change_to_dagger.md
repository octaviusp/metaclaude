# Migration Plan: MetaClaude from Docker to Dagger

This document outlines a comprehensive, phased plan to migrate the MetaClaude project from its custom Docker orchestration logic to a robust, modern pipeline-as-code implementation using the Dagger Python SDK.

## Executive Summary

The current architecture uses a Python script (`vcc/docker/manager.py`) to programmatically build, run, and manage Docker containers. While functional, this approach is imperative and lacks the benefits of a declarative, cache-aware, and composable system.

Dagger provides a CI/CD-as-Code framework that aligns perfectly with MetaClaude's goal of orchestrating containerized AI tasks. Migrating to Dagger will introduce:
- **Robustness & Reproducibility**: Declarative pipelines with automatic dependency tracking.
- **Performance**: Content-addressable caching for all intermediate steps.
- **Composability**: Modular agent logic encapsulated in reusable Dagger Functions.
- **Developer Experience**: Improved local debugging, testing, and observability.

---

## Phase 1: Foundation & Initial Dagger Setup

**Goal:** Establish the Dagger SDK in the project and replicate the existing Docker image build process as a Dagger Function.

**Steps:**

1.  **Install Dagger SDK:**
    -   Add `dagger-io` to the `[tool.poetry.dependencies]` in `pyproject.toml`.
    -   Run `poetry lock` and `poetry install` to update the environment.

2.  **Create Dagger Directory Structure:**
    -   Create a new top-level directory: `dagger/`.
    -   Inside `dagger/`, create a Python package structure: `dagger/src/metaclaude_dagger/__init__.py`. This will house our Dagger pipeline modules.

3.  **Initialize Dagger Client:**
    -   Create a new file: `dagger/src/metaclaude_dagger/pipeline.py`.
    -   In this file, write a basic `main` function that initializes the Dagger client to verify the installation:
        ```python
        import dagger
        import sys

        async def main():
            async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:
                container = client.container().from_("alpine:latest")
                version = await container.with_exec(["cat", "/etc/alpine-release"]).stdout()
                print(f"Hello from Dagger and Alpine {version}")

        # To run: python -m dagger.src.metaclaude_dagger.pipeline
        ```

4.  **Convert `Dockerfile` to a Dagger Function:**
    -   Create a new file `dagger/src/metaclaude_dagger/environment.py`.
    -   Create a Dagger Function `create_base_environment(client: dagger.Client) -> dagger.Container:` that programmatically reproduces the steps from the existing `docker/Dockerfile`.
    -   This function will:
        -   Start from `debian:bookworm-slim`.
        -   Install system dependencies (`curl`, `git`, etc.).
        -   Install Node.js 20.
        -   Create the non-root `vcc` user.
        -   Set up the `/workspace` directory.
        -   Install the `@anthropic-ai/claude-code` CLI via `npm`.
        -   Set all necessary environment variables (`NODE_ENV`, `PATH`, etc.).
    -   This function will return a configured but not yet executed `dagger.Container` object. This container will serve as the base for all subsequent agent tasks.

---

## Phase 2: Porting Core Components to Dagger Functions

**Goal:** Encapsulate the core logic of MetaClaude (analysis, templating, agent execution) into modular, testable Dagger Functions.

**Steps:**

1.  **Idea Analysis as a Dagger Function:**
    -   In `dagger/src/metaclaude_dagger/analyzer.py`, create a function: `analyze_idea(client: dagger.Client, idea: str) -> dagger.File:`.
    -   This function will:
        -   Start with a minimal Python container.
        -   Mount the `vcc/core/analyzer.py` and its dependencies into the container.
        -   Execute a script that runs the `IdeaAnalyzer` on the input `idea` string.
        -   Return the structured analysis results as a `dagger.File` object (e.g., `analysis.json`).

2.  **Template Injection as a Dagger Function:**
    -   In `dagger/src/metaclaude_dagger/templating.py`, create a function: `inject_configuration(client: dagger.Client, analysis_file: dagger.File, selected_agents: list[str], model: str) -> dagger.Directory:`.
    -   This function will:
        -   Start with a Python container with `Jinja2` installed.
        -   Mount the `templates/` directory.
        -   Mount the `analysis.json` file from the previous step.
        -   Execute a script that uses `TemplateManager` logic to render the entire `.claude` configuration directory.
        -   Return the resulting `.claude` directory as a `dagger.Directory` object.

3.  **Agent Execution as Dagger Functions:**
    -   In `dagger/src/metaclaude_dagger/agents.py`, create a generic function: `run_agent(base_env: dagger.Container, claude_config: dagger.Directory, startup_script: dagger.File) -> dagger.Directory:`.
    -   This function will:
        -   Take the base environment container as input.
        -   Mount the rendered `.claude` configuration directory.
        -   Mount a generated `startup.sh` script (similar to the current implementation).
        -   Execute the script.
        -   Return the `/workspace/output` directory as a `dagger.Directory` containing the generated project code.

---

## Phase 3: Orchestrating the Pipeline in Dagger

**Goal:** Combine the individual Dagger Functions into a coherent, end-to-end pipeline that replicates and enhances the current workflow.

**Steps:**

1.  **Create the Main Pipeline Function:**
    -   In `dagger/src/metaclaude_dagger/pipeline.py`, create the main orchestration function: `generate_project(client: dagger.Client, idea: str, model: str, agents: list[str], api_key: dagger.Secret) -> dagger.Directory:`.

2.  **Implement the DAG (Directed Acyclic Graph):**
    -   Inside `generate_project`, chain the Dagger Functions together:
        1.  Call `create_base_environment()` to get the base container.
        2.  Call `analyze_idea()` with the `idea` string.
        3.  Use the output of `analyze_idea()` to determine the final list of agents.
        4.  Call `inject_configuration()` with the analysis file and agent list.
        5.  Inject the `ANTHROPIC_API_KEY` using `with_secret_variable()`.
        6.  Generate the `startup.sh` script as a `dagger.File`.
        7.  Call `run_agent()` with the base container, the `.claude` directory, and the startup script.
        8.  Return the final `dagger.Directory` containing the generated project.

3.  **Integrate Secret Management:**
    -   Modify the pipeline to accept the Anthropic API key as a `dagger.Secret`.
    -   Use `client.set_secret()` to load the key from an environment variable or file.
    -   Pass this secret to the `run_agent` function, which will use `with_secret_variable()` to securely expose it to the container.

4.  **Enable Parallelism (Future Enhancement):**
    -   Structure the pipeline to allow for future parallel execution of agents if the workflow is ever adapted to support it (e.g., generating frontend and backend code simultaneously). Dagger's `async/await` syntax will handle this naturally.

---

## Phase 4: Integrating Dagger with the CLI

**Goal:** Replace the existing `DockerManager` with the new Dagger pipeline, making the transition seamless for the end-user.

**Steps:**

1.  **Modify `vcc/core/orchestrator.py`:**
    -   Remove the `DockerManager` dependency.
    -   Add a method `_execute_dagger_pipeline(...)`.
    -   This method will be responsible for:
        -   Importing the Dagger pipeline functions.
        -   Initializing the `dagger.Connection`.
        -   Calling the main `generate_project` Dagger function.
        -   Passing all necessary parameters (idea, model, API key secret).

2.  **Handle Artifacts:**
    -   The `generate_project` function will return a `dagger.Directory`.
    -   Use the `export()` method on the directory object to write the generated project files to the host filesystem in the `metaclaude_output` directory.

3.  **Stream Logs to the Console:**
    -   Modify the Dagger functions to stream their `stdout` and `stderr` to the Dagger client's log output.
    -   The `VCCOrchestrator` will capture and display this output using the `Rich` console, providing real-time feedback to the user.

4.  **Update CLI (`vcc/cli.py`):**
    -   Ensure that all CLI arguments are correctly passed to the `VCCOrchestrator` and then into the Dagger pipeline.
    -   The user-facing commands (`metaclaude`, `metaclaude doctor`, etc.) should remain unchanged.

---

## Phase 5: Refinement, Testing, and Cleanup

**Goal:** Finalize the migration by adding tests, leveraging Dagger's advanced features, and removing legacy code.

**Steps:**

1.  **Implement Caching:**
    -   Verify that Dagger's content-addressable caching is working as expected. Subsequent runs with the same inputs should be significantly faster. This requires no extra code but should be tested.

2.  **Write Tests for the Dagger Pipeline:**
    -   Create a `dagger/tests/` directory.
    -   Write unit tests for individual Dagger Functions (e.g., test the `analyze_idea` function with mock inputs).
    -   Write an end-to-end integration test for the main `generate_project` pipeline.

3.  **Refine Error Handling:**
    -   Wrap Dagger execution calls in `try...except` blocks within the `VCCOrchestrator`.
    -   Catch `dagger.QueryError` and other Dagger-specific exceptions.
    -   Translate these into user-friendly `VCCError` exceptions to maintain a consistent error-reporting experience.

4.  **Deprecate and Remove Legacy Code:**
    -   Once the Dagger pipeline is stable and fully integrated, delete the `vcc/docker/manager.py` file.
    -   Delete the `docker/Dockerfile` and `docker/.dockerignore` files.
    -   Remove any now-unused logic from the `VCCOrchestrator`.

5.  **Update Documentation:**
    -   Update `README.md` to mention the use of Dagger and remove manual Docker build steps from the development section.
    -   Update `CLAUDE.md` and `understanding.md` to reflect the new Dagger-based architecture.
    -   Add a developer guide explaining how to run and debug the Dagger pipeline locally.
