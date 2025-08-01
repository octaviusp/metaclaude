#!/usr/bin/env python3
"""
MetaClaude - Main entry point

A Poetry-managed Python CLI that bootstraps an isolated Claude Code runtime 
inside Docker to generate complete software projects in a single shot.
"""

import sys
from pathlib import Path

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from metaclaude.cli import app

if __name__ == "__main__":
    app()