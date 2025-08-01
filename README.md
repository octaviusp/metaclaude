# MetaClaude

<div align="center">

```
██╗   ██╗██╗██████╗ ████████╗██╗   ██╗ █████╗ ██╗     
██║   ██║██║██╔══██╗╚══██╔══╝██║   ██║██╔══██╗██║     
██║   ██║██║██████╔╝   ██║   ██║   ██║███████║██║     
╚██╗ ██╔╝██║██╔══██╗   ██║   ██║   ██║██╔══██║██║     
 ╚████╔╝ ██║██║  ██║   ██║   ╚██████╔╝██║  ██║███████╗
  ╚═══╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
                                                       
 ██████╗██╗      █████╗ ██╗   ██╗██████╗ ███████╗      
██╔════╝██║     ██╔══██╗██║   ██║██╔══██╗██╔════╝      
██║     ██║     ███████║██║   ██║██║  ██║█████╗        
██║     ██║     ██╔══██║██║   ██║██║  ██║██╔══╝        
╚██████╗███████╗██║  ██║╚██████╔╝██████╔╝███████╗      
 ╚═════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝      
```

**🚀 Transform Ideas into Complete Software Projects with AI**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![Claude](https://img.shields.io/badge/powered%20by-Claude-orange.svg)](https://claude.ai/)

</div>

## 🌟 Overview

MetaClaude is a revolutionary CLI tool that transforms natural language ideas into complete, production-ready software projects. By leveraging the power of Claude AI within isolated Docker environments, MetaClaude provides a safe, scalable, and intelligent approach to automated software development.

### ✨ Key Features

- 🤖 **AI-Powered Generation**: Harness Claude's advanced reasoning to build complete projects
- 🐳 **Docker Isolation**: Safe, reproducible builds in containerized environments  
- 🎨 **Rich Terminal UI**: Beautiful, interactive command-line experience
- 🧩 **Modular Agents**: Specialized AI agents for different development domains
- 📋 **Template System**: Flexible, customizable project templates
- 🔧 **MCP Integration**: Model Context Protocol support for enhanced capabilities
- 📊 **Analytics & Insights**: Track generation progress and performance
- 🛡️ **Enterprise Ready**: Robust error handling and logging

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** - [Download](https://www.python.org/downloads/)
- **Docker** - [Install Docker](https://docs.docker.com/get-docker/)
- **Poetry** - [Install Poetry](https://python-poetry.org/docs/#installation)
- **Anthropic API Key** - [Get your key](https://console.anthropic.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/metaclaude.git
cd metaclaude

# Install dependencies
poetry install && poetry shell

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Verify installation
metaclaude doctor
```

### Your First Project

```bash
# Generate a React todo application
python metaclaude.py main "Create a React todo app with authentication"

# Build a Python ML pipeline  
python metaclaude.py main "Build a sentiment analysis pipeline with scikit-learn" --model sonnet

# Create a Node.js REST API
python metaclaude.py main "Design a REST API for a bookstore with Express and MongoDB"
```

## 📖 Usage

### Basic Commands

```bash
# Generate projects from natural language
python metaclaude.py main "Your project idea here"

# Use specific Claude model
python metaclaude.py main "Build a Django blog" --model opus

# Enable detailed logging
python metaclaude.py main "Create a REST API" --verbose

# Keep container for debugging
python metaclaude.py main "Build a complex app" --keep-container --timeout unlimited
```

### Command Options

| Option | Description | Example |
|--------|-------------|---------|
| `<IDEA>` | Project description (required) | `"Create a React todo app"` |
| `--model` | Claude model (opus/sonnet/haiku) | `--model sonnet` |
| `--timeout` | Execution timeout | `--timeout 2h` or `unlimited` |
| `--verbose` | Detailed logging | `--verbose` |
| `--keep-container` | Keep container for debugging | `--keep-container` |

### Utility Commands

```bash
python metaclaude.py doctor    # System health check
python metaclaude.py agents    # List available agents  
python metaclaude.py validate  # Validate templates
```

## 🤖 What Can MetaClaude Build?

MetaClaude can generate complete, production-ready projects across multiple domains:

### 🌐 Web Development
- React, Vue, Angular applications
- REST APIs and GraphQL services
- Full-stack applications with authentication
- Progressive Web Apps (PWAs)

### 🤖 Machine Learning  
- ML pipelines with scikit-learn, TensorFlow
- Data analysis with pandas, matplotlib
- NLP projects with transformers
- Computer vision applications

### 📱 Mobile & Desktop
- React Native and Flutter apps
- Electron desktop applications
- CLI tools and utilities

### 🛠️ DevOps & Infrastructure
- Docker configurations
- CI/CD pipelines
- Cloud deployment scripts
- Kubernetes manifests

## 🎯 Example Projects

```bash
# Web Applications
vcc "Create a React e-commerce site with Stripe integration"
vcc "Build a Vue.js dashboard with charts and real-time data"
vcc "Design a Next.js blog with markdown support"

# APIs and Backend
vcc "Create a FastAPI server for image processing"
vcc "Build a GraphQL API with authentication and authorization"
vcc "Design a microservice for user management"

# Machine Learning
vcc "Build a customer churn prediction model"
vcc "Create a sentiment analysis API with BERT"
vcc "Design an image classification pipeline"

# Mobile Applications  
vcc "Create a React Native expense tracker"
vcc "Build a Flutter weather app with location services"

# DevOps & Tools
vcc "Create a GitHub Actions workflow for Python testing"
vcc "Build a Dockerfile for a Node.js application"
vcc "Design Terraform scripts for AWS infrastructure"
```

## 🏗️ How It Works

```
1. 💭 Natural Language Input → "Create a React todo app"
2. 🧠 AI Analysis → Extract domains, technologies, complexity  
3. 🤖 Agent Selection → Choose specialized agents automatically
4. 🐳 Docker Isolation → Safe, reproducible environment
5. 🚀 Claude Code Generation → Complete project creation
6. 📦 Ready-to-Use Project → Full codebase with documentation
```

## ⚡ Quick Examples

**React Todo App (2-3 minutes)**
```bash
vcc "Create a React todo app with local storage"
# ✅ Full React app with components, styling, and functionality
```

**Python API (3-5 minutes)**  
```bash
vcc "Build a FastAPI server for a bookstore with CRUD operations"
# ✅ Complete API with endpoints, models, and documentation
```

**ML Pipeline (5-8 minutes)**
```bash
vcc "Create a sentiment analysis pipeline with training and inference"
# ✅ Full ML project with data processing, model training, and API
```

## 🛠️ Development

```bash
# Clone and setup
git clone https://github.com/your-org/metaclaude.git
cd metaclaude
poetry install

# Run tests
poetry run pytest

# Contribute
# 1. Fork the repo
# 2. Create feature branch  
# 3. Make changes with tests
# 4. Submit pull request
```

## 🐛 Troubleshooting  

**Docker Issues**: Ensure Docker is running (`docker info`)  
**API Key Issues**: Set `ANTHROPIC_API_KEY` environment variable  
**Timeouts**: Use `--timeout unlimited` for complex projects  
**Debug**: Use `--verbose --keep-container` for detailed logs

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

<div align="center">

**🚀 Transform Your Ideas into Reality with MetaClaude**

*MetaClaude - AI-Powered Software Development*

</div>