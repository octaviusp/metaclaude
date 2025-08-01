import os
from pathlib import Path
from metaclaude.core.orchestrator import MetaClaudeOrchestrator

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.resolve()

    # Set the templates and output directories
    templates_dir = project_root / "templates"
    output_base_dir = project_root

    # Set the project idea
    idea = "Create a simple hello world python script"

    # Check if the ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
        return

    # Create an instance of the orchestrator
    orchestrator = MetaClaudeOrchestrator(
        templates_dir=templates_dir,
        output_base_dir=output_base_dir,
        enable_agentic_mode=False, # Forcing traditional mode for simplicity
    )

    # Execute the orchestrator
    try:
        result = orchestrator.execute(
            idea=idea,
            force_traditional_mode=True, # Forcing traditional mode for simplicity
        )
        print("Execution result:", result)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
