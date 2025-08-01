# Contributing to MetaClaude

Thank you for your interest in contributing to MetaClaude! This document provides guidelines for contributing to the project.

## Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/metaclaude.git`
3. **Install** dependencies: `poetry install`
4. **Create** a branch: `git checkout -b feature/your-feature-name`
5. **Make** your changes with tests
6. **Test** your changes: `poetry run pytest`
7. **Submit** a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/metaclaude.git
cd metaclaude

# Install development dependencies
poetry install

# Activate virtual environment
poetry shell

# Run tests
pytest

# Code quality checks
black --check .
ruff check .
mypy vcc/
```

## Code Guidelines

- **Python 3.9+** compatibility
- **Type hints** for all functions
- **Docstrings** for public APIs
- **Tests** for new features
- **Black** formatting
- **Ruff** linting compliance

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=vcc

# Run specific test file
pytest tests/test_cli.py
```

## Pull Request Process

1. **Update** documentation if needed
2. **Add** tests for new functionality
3. **Ensure** all tests pass
4. **Update** CHANGELOG.md if applicable
5. **Provide** clear commit messages

## Reporting Issues

When reporting issues, please include:

- **Operating system** and version
- **Python version**
- **Docker version**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Error messages** or logs

## Questions?

- Open a [GitHub Discussion](https://github.com/your-org/virtual-claude-code/discussions)
- Check existing [Issues](https://github.com/your-org/virtual-claude-code/issues)

Thank you for contributing! 🚀