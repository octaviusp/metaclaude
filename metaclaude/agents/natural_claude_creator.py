"""
Natural Claude Code Agent Creator

This module uses Claude Code in its natural mode to create specialized agents
for projects. Instead of forcing JSON responses, it lets Claude Code create
agent files naturally and then parses those files.
"""

import os
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

from ..utils.logging import get_logger
from ..utils.errors import MetaClaudeAgentError
from .parser import AgentConfig

logger = get_logger(__name__)


@dataclass
class ClaudeCreatedAgent:
    """An agent created by Claude Code naturally."""
    name: str
    description: str
    system_prompt: str
    file_path: str
    tools: List[str] = None
    reasoning: str = ""


class NaturalClaudeAgentCreator:
    """
    Creates agents by letting Claude Code work naturally to create agent files.
    
    This approach:
    1. Gives Claude Code a natural prompt to analyze the project
    2. Asks Claude to create individual .md files for specialized agents
    3. Parses the created files to extract agent information
    4. Converts to internal agent format
    """
    
    def __init__(self, docker_manager=None):
        """Initialize natural Claude Code agent creator.
        
        Args:
            docker_manager: Docker manager for running Claude Code
        """
        self.docker_manager = docker_manager
        
    def create_agent_creation_prompt(self, idea: str) -> str:
        """Create a natural prompt for Claude Code to create agents.
        
        Args:
            idea: Project idea description
            
        Returns:
            Natural language prompt for Claude Code
        """
        return f"""# Agent Creation Task

I need you to analyze this project idea and create specialized sub-agents that would work together optimally to complete this project:

**Project Idea:** {idea}

## Your Task

1. **Analyze the project** - understand what needs to be built, what technologies are involved, and what expertise areas are needed.

2. **Suggest 1-3 specialized agents** that would work together optimally for this project. Consider:
   - What specific expertise is needed?
   - What would be the most efficient division of work?
   - What agents would complement each other well?

3. **Create individual agent files** in the `.claude/agents/` directory. For each suggested agent, create a file named `[agent-name].md` with this structure:

```markdown
---
name: AgentName
description: Brief description of what this agent does
tools: ["Read", "Write", "Edit", "Bash", "TodoWrite"]
parallelism: 4
patterns: ["claude-created"]
---

# Agent Name

## Role & Expertise
Describe the agent's primary role and expertise areas.

## System Instructions
Write detailed system instructions for this agent. This will be their "personality" and approach to work. Include:
- How they should approach tasks
- Their specific expertise and knowledge
- How they should collaborate with other agents
- Quality standards they should follow

## Why This Agent?
Explain why this specific agent is needed for this project.
```

## Guidelines

- **Be specific:** Each agent should have a clear, distinct role
- **Be practical:** Consider what would actually work well for this project
- **Be detailed:** The system instructions should give the agent clear guidance
- **Consider tools:** Suggest appropriate tools from: Read, Write, Edit, MultiEdit, Bash, Glob, Grep, WebFetch, TodoWrite, WebSearch

## Example Agent Types (adapt as needed)
- FrontendSpecialist (for UI/UX work)
- BackendArchitect (for server-side logic)
- DatabaseDesigner (for data modeling)
- TestingExpert (for quality assurance)
- DevOpsEngineer (for deployment/infrastructure)
- SecurityAuditor (for security review)

Create the agents that make the most sense for: **{idea}**

Start by analyzing the project, then create the appropriate agent files in `.claude/agents/`.
"""

    async def create_agents_with_claude(
        self, 
        idea: str, 
        container_id: str,
        workspace_path: Path
    ) -> List[ClaudeCreatedAgent]:
        """
        Use Claude Code naturally to create specialized agents.
        
        Args:
            idea: Project idea description
            container_id: Docker container ID where Claude Code is running
            workspace_path: Path to workspace directory
            
        Returns:
            List of Claude-created agents
            
        Raises:
            MetaClaudeAgentError: If agent creation fails
        """
        logger.info(f"Asking Claude Code to naturally create agents for: {idea[:50]}...")
        
        try:
            # Create the natural prompt
            prompt = self.create_agent_creation_prompt(idea)
            
            # Create a temporary file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(prompt)
                prompt_file = f.name
            
            try:
                # Copy prompt file to container
                container = self.docker_manager.client.containers.get(container_id)
                self.docker_manager.copy_to_container(
                    container, 
                    Path(prompt_file), 
                    "/workspace"
                )
                
                prompt_container_path = f"/workspace/{Path(prompt_file).name}"
                
                # Create the .claude/agents directory in container
                logger.info("Creating .claude/agents directory in container...")
                self.docker_manager.execute_command(
                    container,
                    "mkdir -p /workspace/.claude/agents",
                    workdir="/workspace"
                )
                
                # Execute Claude Code to analyze and create agents
                claude_command = f"claude-code --dangerously-skip-permissions {prompt_container_path}"
                
                logger.info("Executing Claude Code for natural agent creation...")
                exit_code, output = self.docker_manager.execute_command(
                    container, 
                    claude_command,
                    workdir="/workspace"
                )
                
                if exit_code != 0:
                    logger.warning(f"Claude Code execution had issues (exit code {exit_code}): {output}")
                    # Don't fail immediately, Claude might have still created files
                
                # Wait a moment for file system to settle
                time.sleep(2)
                
                # Check what files were created in .claude/agents
                logger.info("Checking for created agent files...")
                exit_code, ls_output = self.docker_manager.execute_command(
                    container,
                    "ls -la /workspace/.claude/agents/",
                    workdir="/workspace"
                )
                
                if exit_code == 0:
                    logger.info(f"Files in .claude/agents: {ls_output}")
                else:
                    logger.warning("Could not list .claude/agents directory")
                
                # Parse created agent files
                created_agents = await self._parse_created_agent_files(container)
                
                if not created_agents:
                    logger.warning("No agents were created by Claude Code")
                    return self._create_fallback_agent(idea)
                
                logger.info(f"Claude naturally created {len(created_agents)} agents: "
                          f"{[a.name for a in created_agents]}")
                
                return created_agents
                
            finally:
                # Cleanup temp file
                Path(prompt_file).unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Natural Claude agent creation failed: {e}")
            return self._create_fallback_agent(idea)
    
    async def _parse_created_agent_files(self, container) -> List[ClaudeCreatedAgent]:
        """Parse agent files created by Claude Code.
        
        Args:
            container: Docker container
            
        Returns:
            List of parsed agents
        """
        agents = []
        
        try:
            # List all .md files in the agents directory
            exit_code, output = self.docker_manager.execute_command(
                container,
                "find /workspace/.claude/agents -name '*.md' -type f",
                workdir="/workspace"
            )
            
            if exit_code != 0 or not output.strip():
                logger.warning("No .md files found in .claude/agents directory")
                return agents
            
            file_paths = [path.strip() for path in output.strip().split('\n') if path.strip()]
            logger.info(f"Found {len(file_paths)} agent files: {file_paths}")
            
            for file_path in file_paths:
                try:
                    # Read the file content
                    exit_code, content = self.docker_manager.execute_command(
                        container,
                        f"cat {file_path}",
                        workdir="/workspace"
                    )
                    
                    if exit_code == 0 and content.strip():
                        agent = self._parse_agent_file_content(content, file_path)
                        if agent:
                            agents.append(agent)
                            logger.info(f"Parsed agent: {agent.name}")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse agent file {file_path}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to parse created agent files: {e}")
        
        return agents
    
    def _parse_agent_file_content(self, content: str, file_path: str) -> Optional[ClaudeCreatedAgent]:
        """Parse individual agent file content.
        
        Args:
            content: File content
            file_path: Path to the file
            
        Returns:
            Parsed agent or None if parsing fails
        """
        try:
            # Extract YAML front matter and content
            lines = content.strip().split('\n')
            
            if not lines or lines[0] != '---':
                logger.warning(f"Agent file {file_path} missing YAML front matter")
                return None
            
            # Find end of YAML front matter
            yaml_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    yaml_end = i
                    break
            
            if yaml_end == -1:
                logger.warning(f"Agent file {file_path} has malformed YAML front matter")
                return None
            
            # Parse YAML front matter (simple parsing)
            yaml_lines = lines[1:yaml_end]
            metadata = {}
            
            for line in yaml_lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle arrays
                    if value.startswith('[') and value.endswith(']'):
                        value = [item.strip().strip('"').strip("'") for item in value[1:-1].split(',')]
                    else:
                        value = value.strip('"').strip("'")
                    
                    metadata[key] = value
            
            # Get system prompt from content after YAML
            system_prompt = '\n'.join(lines[yaml_end + 1:]).strip()
            
            # Create agent
            agent = ClaudeCreatedAgent(
                name=metadata.get('name', Path(file_path).stem),
                description=metadata.get('description', 'Claude-created agent'),
                system_prompt=system_prompt,
                file_path=file_path,
                tools=metadata.get('tools', ['Read', 'Write', 'Edit', 'TodoWrite']),
                reasoning=f"Created by Claude Code for specific project needs"
            )
            
            return agent
            
        except Exception as e:
            logger.error(f"Failed to parse agent file content: {e}")
            return None
    
    def _create_fallback_agent(self, idea: str) -> List[ClaudeCreatedAgent]:
        """Create a fallback agent if Claude creation fails.
        
        Args:
            idea: Project idea
            
        Returns:
            List with single fallback agent
        """
        logger.warning("Creating fallback agent due to Claude Code failure")
        
        fallback_agent = ClaudeCreatedAgent(
            name="GeneralDeveloper",
            description="General-purpose developer (fallback)",
            system_prompt=f"""# General Developer

You are a skilled software developer working on: {idea}

## Your Approach
1. Analyze the requirements carefully
2. Break down the task into manageable steps  
3. Implement clean, well-documented code
4. Test your implementation
5. Provide clear documentation

## Guidelines
- Follow best practices for the technology stack
- Write maintainable, readable code
- Include proper error handling
- Create useful documentation
- Work systematically and thoroughly

Focus on delivering a working solution that meets the user's needs.""",
            file_path="/fallback/general_developer.md",
            tools=["Read", "Write", "Edit", "MultiEdit", "Bash", "TodoWrite"],
            reasoning="Fallback agent when Claude Code agent creation fails"
        )
        
        return [fallback_agent]
    
    def convert_to_agent_configs(self, claude_agents: List[ClaudeCreatedAgent]) -> List[AgentConfig]:
        """Convert Claude-created agents to AgentConfig objects.
        
        Args:
            claude_agents: List of Claude-created agents
            
        Returns:
            List of AgentConfig objects
        """
        configs = []
        
        for agent in claude_agents:
            config = AgentConfig(
                name=agent.name,
                description=f"{agent.description} (Claude-created)",
                tools=agent.tools or ["Read", "Write", "Edit", "TodoWrite"],
                parallelism=4,
                patterns=["claude-created", "natural"],
                content=agent.system_prompt,
                file_path=agent.file_path
            )
            configs.append(config)
        
        return configs